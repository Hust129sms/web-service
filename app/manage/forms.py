from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileStorage
from werkzeug.utils import secure_filename
from ..models import Group

from wtforms import SubmitField, ValidationError, RadioField, StringField
from wtforms.validators import DataRequired, Length


class EnableForm(FlaskForm):
    confirm_type = RadioField(u"请选择验证方式", choices=[(0, u"邮箱"), (1, u"手机")], coerce=int)
    submit = SubmitField(u'发送验证信息')

    @staticmethod
    def validate_confirm_type(self, field):
        if field.data == 0 and current_user.email_confirmed:
            raise ValidationError(u"该帐号已经验证过邮件！")
        if field.data == 1 and current_user.telephone_confirmed:
            raise ValidationError(u"该帐号已经验证过手机！")


class CreateGroupForm(FlaskForm):
    name = StringField(u"圈子名称", validators=[DataRequired(message="圈子名称不能为空！"),
                                            Length(3, 128, message=u"圈子名称最少3个字符！")])
    group_type = RadioField(u"圈子类型", validators=[DataRequired(message=u"请选择圈子类型以便我们提供更好的服务！")],
                            choices=[(1, u"管理层圈子"), (2, u"会员圈子"), (3, u"活动圈子")], coerce=int)
    tel = StringField(u"负责人电话", validators=[DataRequired(message=u'请填写负责人电话以便联系'),
                                            Length(11, 11, message=u"请输入u正确的手机号码")])
    image = FileField(u"上传圈子图片", validators=[FileAllowed(['png', 'jpg'], message=u"仅支持png格式和jpg格式的图片！")])
    submit = SubmitField(u"创建组织")

    @staticmethod
    def validate_name(self, field):
        if Group.query.filter_by(name=field.data, Owner=current_user, ).first():
            raise ValidationError(u'你已经创建了一个同名的组织！')
