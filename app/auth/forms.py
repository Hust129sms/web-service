from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, email, EqualTo, URL


from ..models import User


class LoginForm(FlaskForm):
    email = StringField("", validators=[DataRequired(message=u"电子邮件/手机号不能为空！"),
                                        Length(3, 64, message=u"输入错误")],
                        render_kw={"placeholder": u"电子邮件/手机号"})
    password = PasswordField("", validators=[DataRequired(message=u"密码不能为空"),
                                             Length(6, 64, message=u"密码长度不正确")],
                             render_kw={"placeholder": u"密码"})
    remember_me = BooleanField(u'记住登录状态')
    recaptcha = RecaptchaField()
    submit = SubmitField(u'登录')


class RegForm(FlaskForm):
    email = StringField(u"电子邮件", validators=[DataRequired(message=u"电子邮件地址不能为空！"),
                                             Length(3, 128, message=u"长度超出限制！（128个字符）"),
                                             email(message=u"请输入正确的电子邮件地址！")],
                        render_kw={"placeholder": "yourname@example.com"}
                        )
    username = StringField(u"用户名", validators=[DataRequired(message=u"用户名不能为空！"),
                                               Length(2, 128, message=u"名称应为2～128字符"),
                                               Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0,
                                                      message=u"用户名应以字母开头且由字母数字下划线组成")],
                           render_kw={"placeholder": u"example"}

                           )
    telephone = StringField(u"手机号码", validators=[DataRequired(message=u"手机号不能为空！"),
                                                 Length(11, 11, message=u"手机号长度不正确！"),
                                                 ],
                            render_kw={"placeholder": u"130-0000-0000"}
                            )
    password = PasswordField(u"密码", validators=[DataRequired(message=u'密码不能为空！'),
                                                Length(6,128,message=u'密码应为6～128位'),
                                                ],
                             render_kw={"placeholder": u"请输入密码"}
                             )

    password2 = PasswordField(u'确认密码', validators=[DataRequired(),
                                                   EqualTo("password", message=u"两次密码不一致，请检查输入！")],
                              render_kw={"placeholder": u"确认密码"}
                              )
    recaptcha = RecaptchaField()
    submit = SubmitField(u'成为羽毛')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮件已经被注册！您是否要选择<找回密码>')

    @staticmethod
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u"该用户名已被注册！您是否要选择<找回密码>")


class ChangepasswordForm(FlaskForm):
    old_password = PasswordField(u"输入旧密码", validators=[DataRequired(message=u"旧密码不能为空！")], render_kw={'placeholder': u"请输入旧密码"})
    new_password = PasswordField(u"密码", validators=[DataRequired(message=u'新密码不能为空！'),
                                 Length(6, 128, message=u'新密码应为6～128位'), ],
                                 render_kw={'placeholder': u"请输入新密码"})
    confirm_password = PasswordField(u"密码", validators=[DataRequired(message=u'确认密码不能为空！'),
                                     Length(6, 128, message=u'新密码应为6～128位'),
                                     EqualTo("new_password", message=u"两次密码不一致，请检查输入！")],
                                     render_kw={'placeholder': u"确认密码"}
                                     )
    submit = SubmitField(u'确认修改')


class ForgetpasswordForm(FlaskForm):
    email = StringField(u"请输入邮箱或手机号", validators=[DataRequired(message="请输入邮箱或手机号！")],
                        render_kw={'placeholder': u"邮箱/手机号"})
    submit = SubmitField(u"发送验证信息")

    @staticmethod
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            user = User.query.filter_by(telephone=field.data).first()
            if user is None:
                raise ValidationError(u"请确认你的输入！")
        return True


class ResetpasswordForm(FlaskForm):
    new_password = PasswordField(u"密码", validators=[DataRequired(message=u'新密码不能为空！'),
                                 Length(6, 128, message=u'新密码应为6～128位'), ],
                                 render_kw={'placeholder': u"请输入新密码"})
    confirm_password = PasswordField(u"密码", validators=[DataRequired(message=u'确认密码不能为空！'),
                                     Length(6, 128, message=u'新密码应为6～128位'),
                                     EqualTo("new_password", message=u"两次密码不一致，请检查输入！")],
                                     render_kw={'placeholder': u"确认密码"}
                                     )
    submit = SubmitField(u'确认修改')


class OpenIDForm(FlaskForm):
    openid = StringField('OpenID URL', validators=[DataRequired(), URL()])
