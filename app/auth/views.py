from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
import time

from . import auth
from .. import oid
from ..models import User, db, PersonalMessage
from .forms import LoginForm, RegForm, ChangepasswordForm, ForgetpasswordForm, ResetpasswordForm, OpenIDForm
from ..tools.mail_thread import send_email


@auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form = LoginForm()
    openid_form = OpenIDForm()
    if openid_form.validate_on_submit():
        return oid.try_login(openid_form.openid.data,ask_for=['nickname', 'email'], ask_for_optional=['fullname'])
    # 检查是否有有效登录表单
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Email验证失败，尝试验证手机号
        if user is None:
            user = User.query.filter_by(telephone=form.email.data).first()
        # 检查账户是否存在
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            user.last_login_time = user.this_login_time
            user.this_login_time = int(time.time())
            if user.this_login_time - user.last_login_time > 1339200:
                # TODO
                # 半月未登录后登录提醒
                # send_email(user.email, "您的账户刚刚进行了登录", "auth/email/longtimenologin.html", time=user.this_login_time)
                pass
            if not (user.email_confirmed or user.telephone_confirmed):
                flash({'type': "danger", 'content':"当前帐号未激活！请先激活邮箱/手机号！"})
                return redirect(url_for("manage.confirm", uid=user.get_id()))
            # 添加上次登录时间
            return redirect(request.args.get('next') or url_for('manage.index'))
        flash(u'用户名或密码错误！')
    # 返回登录页面
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash("外部认证错误！")
    return render_template('auth/login.html', form=form, openid_form=openid_form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(u"羽毛已经安全着陆了！")
    return redirect(url_for('manage.index'))


@auth.route('/reg', methods=['GET', 'POST'])
@oid.loginhandler
def reg():
    form = RegForm()
    openid_form = OpenIDForm()
    if current_user.is_authenticated:
        return redirect(url_for("manage.console"))
    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    telephone=form.telephone.data)
        db.session.add(user)
        db.session.commit()
        pm = PersonalMessage(rec_id=user.uid, from_id=0, message="亲爱的%s您已经完成了注册，请及时激活邮箱以便获得正常的访问权限！" % user.username,
                             title="系统提示")
        db.session.add(pm)
        flash(u"注册成功！")
        # user = User.query.filter_by(email=form.email.data).first()
        # 注册完成后直接登录
        login_user(user, False)
        return redirect(url_for("manage.console"))
    counter1 = User.query.count()
    counter = counter1 + 1
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash("外部登陆出错，请尝试重新登陆或使用其他方式")
    return render_template('auth/reg.html', form=form, cnt=counter, openid_form=openid_form)


@auth.route('/changepw', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            flash(u"密码已经成功修改，你的账户会进入3小时保护状态！期间进行敏感操作会被拦截。")
            pm = PersonalMessage(rec_id=current_user.uid, from_id=0,
                                 message="亲爱的%s您已经成功修改了密码！" % current_user.username,
                                 title="系统提示")
            db.session.add(pm)
    return render_template('auth/changepw.html', form=form, user=current_user)


@auth.route('/forgetpw', methods=['GET', 'POST'])
def forget_password():
    form = ForgetpasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(user.email, '找回密码', 'auth/email/forgetpw', user=user, token=token,
                       time=time.strftime("%Y-%m-%d %H:%M:%S"))
            flash("我们已经将邮件发送至了你的邮箱，请注意查收！")
        else:
            user = User.query.filter_by(telephone=form.email.data).first()
            # TODO
    return render_template("auth/forgetpw.html",form=form)


@auth.route('/forgetpw/<email>/<token>', methods=['GET', 'POST'])
def forget_password_reset(email, token):
    form = ResetpasswordForm()
    user = User.query.filter_by(email=email).first()
    if user is None:
        flash(u"认证失败！请重新获取邮件！")
        return redirect(url_for("auth.forget_password"))
    if user.confirm(token):
        if form.validate_on_submit():
            user.password = form.new_password.data
            user.useful_token = b""
            flash(u"重置密码成功！你可以重新登录了！")
            return redirect(url_for('auth.login'))
        flash(u"认证成功！你可以重置你的密码了！")
        return render_template("auth/resetpw.html", form=form)
    flash(u"认证失败！请重新获取邮件！")
    return redirect(url_for("auth.forget_password"))


@oid.after_login
def create_or_login(resp):
    username = resp.nickname or resp.email
    if not username:
        flash('错误的登陆请求！请重新尝试登陆！')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User.query.filter_by(username=resp.email).first()
    if user is None:
        user = User(username=username)
        if resp.email is None:
            flash("您的登陆信息中没有邮箱信息！请在注册后填写。")
        else:
            User.email = resp.email

        db.session.add(user)
        db.session.commit()

    return redirect(url_for('manage.console'))
