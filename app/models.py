from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from .tools.mail_thread import send_email
from flask_login import current_user
import random
import time


# 加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    uid             用户id
    username        用户昵称
    password_hash   密码哈希
    email           电子邮件
    telephone       手机号码
    role_id         角色id（权限
    log_level       用于设置通知权限
    email_confirmed 用于标记电子邮件确认状态
    telephone_confirmed 用于标记手机号确认状态
    telephone_confirmed_code 用于记录上次生成的手机验证码
    telephone_confirmed_code_time 用于记录上次生成的手机验证码的时间
    this_login_time 记录本次登录时间
    last_login_time 用于记录上次登录时间
    useful_token    标记有效token
    balance         余额
    owned_group_id  所拥有的圈子

    """
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    password_change_time = db.Column(db.Integer, default=0)
    email = db.Column(db.String(128))
    telephone = db.Column(db.String(11))
    role_id = db.Column(db.Integer)
    log_level = db.Column(db.Integer)
    email_confirmed = db.Column(db.Boolean, default=False)
    telephone_confirmed = db.Column(db.Boolean, default=False)
    telephone_confirmed_code = db.Column(db.String(6))
    telephone_confirmed_code_time = db.Column(db.Integer, default=0)
    balance = db.Column(db.Integer, default=0)
    last_login_time = db.Column(db.Integer, default=time.time)
    this_login_time = db.Column(db.Integer, default=time.time)
    useful_token = db.Column(db.String(256), default=0)
    owned_group_id = db.relationship('Group', backref='Owner')
    charge_billing = db.relationship('ChargeRecord', backref='User')
    student_card = db.Column(db.String(128), default='NULL')
    student_auth = db.Column(db.Boolean, default=False)
    owned_form_id = db.relationship('Form', backref='Owner')
    balance_billing = db.relationship('Billing', backref='User')
    personal_message = db.relationship('PersonalMessage', backref='To', lazy='dynamic',
                                       primaryjoin='PersonalMessage.rec_id==User.uid')
    # 设置密码的可读属性
    @property
    def password(self):
        raise AttributeError('密码非可读属性！')

    # 设置密码修改时的动作
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

        # 密码修改通知信号
        if current_user.is_authenticated and current_user is not None:
            # 发送通知邮件
            send_email(current_user.email, '您的密码已经被修改！', 'auth/email/sig_changepw', user=current_user,
                       time=time.strftime("%Y-%m-%d %H:%M:%S"))
            # 标记密码修改时间
            current_user.password_change_time = int(time.time())

    # 认证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        try:
            return self.uid
        except AttributeError:
            raise NotImplementedError('No `uid` attribute - override `get_id`')

#   生成邮箱验证令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        self.useful_token = s.dumps({'confirm': self.get_id()})
        return self.useful_token

#   确认邮箱验证令牌
    def confirm(self, token):
        # token不是最后生成的有效token
        if token != self.useful_token.decode('utf-8'):
            return False
        s = Serializer(current_app.config['SECRET_KEY'])
        # 核对令牌
        try:
            data = s.loads(token)
        except:
            return False
        # 检查验证是否是当前登录账户
        if data.get('confirm') != self.uid:
            return False
        # 标记验证成功
        self.email_confirmed = True
        db.session.add(self)
        return True

#   生成手机验证码
    def generate_confirmation_token_tel(self):
        code_list = []
        # 检查距离上次发送短信的时间
        if int(time.time()) - self.telephone_confirmed_code_time < 59:
            return False
        for i in range(6):  # 0-9数字
            random_num = random.randint(0, 9)
            code_list.append(random_num)
        self.telephone_confirmed_code = ''.join(code_list)
        print("%s %s", self.telephone, self.telephone_confirmed_code)
        self.telephone_confirmed_code_time = int(time.time())
        # TODO
        # 发送短信信号
        return True

#   验证手机验证码
    def confirm_telephone_code(self, code):
        if code == self.telephone_confirmed_code and \
         (int(time.time()) - self.telephone_confirmed_code_time) < 300:
            self.telephone_confirmed = True
            return True
        return False

    def get_balance(self):
        return str(self.balance/1000)


class AnonymousUser(AnonymousUserMixin):
    @staticmethod
    def can(self, permissions):
        return False

    @staticmethod
    def is_administrator(self):
        return False


# 用于储存短信记录
class MessageRecord(db.Model):
    __tablename__ = 'msmrecords'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    timestamp = db.Column(db.Integer, default=time.time)
    content = db.Column(db.Text)


# 用于记录成员信息
class Member(db.Model):
    """
    用于记录组织所属的成员信息
    其中other字段用于以json形式储存更多信息

    """
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    messages_id = db.relationship("MessageRecord", backref='Member')

    tel = db.Column(db.String(11))
    name = db.Column(db.String(20))
    address = db.Column(db.String(128))
    gender = db.Column(db.Boolean)  # False 男   True 女

    other = db.Column(db.Text)


# 用于记录组织信息
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    name = db.Column(db.String(128))
    admins = db.relationship('GroupAdmin', backref='Admin')
    balance = db.Column(db.Integer, default=0)
    charge_record = db.relationship('ChargeRecord', backref='Group')
    member = db.relationship('Member', backref='Group')
    image = db.Column(db.LargeBinary)
    type = db.Column(db.Integer)
    tel = db.Column(db.String(11))

    def get_balance(self):
        return self.balance / 1000


# 用于记录组织管理员信息（子帐号
class GroupAdmin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    email = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.Integer)
    this_seen = db.Column(db.Integer)
    permission_level = db.Column(db.Integer)

    # 设置密码的可读属性
    @property
    def password(self):
        raise AttributeError('密码非可读属性！')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 重置密码
    def reset_password(self):
        code_list = []
        for i in range(6):  # 0-9数字
            random_num = random.randint(0, 9)
            code_list.append(random_num)
        self.password = ''.join(code_list)
        return ''.join(code_list)


class ChargeRecord(db.Model):
    """余额转入到组织的订单记录
        id   用于标记订单编号
        amount  用于记录交易金额
        out_account 用于标记转出的账户 一对多关系
        in_group    用于标记转入的账户 一对多关系
        time    标记交易发生的时间戳
        deal_state  用于标记交易完成的状态
                    0   待支付
                    1   已完成
                    2   已取消
                    3   错误
    """
    __tablename__ = 'billings'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    out_account_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    in_group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    time = db.Column(db.Integer, default=time.time)
    deal_state = db.Column(db.Integer, default=False)


class Form(db.Model):
    """
    用于记录用户生成的回收信息的表单
    form_data一个用于储存表单的json数组
    """
    __tablename__ = 'forms'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.uid"))
    form_data = db.Column(db.Text)
    data = db.relationship("FormData", backref='Form')

    @staticmethod
    def on_changed_data(self):
        # TODO
        # Adapt form data for now data
        pass


class FormData(db.Model):
    """
    用于储存对应表单的表单数据
    允许一张图片的上传，其他类型的数据保存以json形式保存在data中
    """
    __tablename__ = 'formdatas'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'))
    image = db.Column(db.LargeBinary)
    data = db.Column(db.Text)

    @staticmethod
    def adapt_data_for_form(self):
        # TODO
        # adapt the form_data to new version
        pass


class Billing(db.Model):
    __tablename__ = 'money_billings'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer, default=time.time)
    finish_time = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    amount = db.Column(db.Integer)
    token = db.Column(db.String(128))


class PersonalMessage(db.Model):
    __tablename__ = 'pms'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, default=time.time)
    status = db.Column(db.Boolean, default=False)
    rec_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    from_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    message = db.Column(db.Text)
    title = db.Column(db.String(128))
