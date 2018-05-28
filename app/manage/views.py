from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from ..tools.mail_thread import send_email
import base64
from ..models import Group, db, PersonalMessage
from random import randint
import time
import os
import xlrd
from werkzeug.utils import secure_filename
import random
import json
from io import BytesIO
from ..decorators import own_required

from . import manage
from .forms import EnableForm, CreateGroupForm
from ..models import Group, Member, Billing
from .. import db
from ..models import User, UploadFile


@manage.route('/', methods=['GET', 'POST'])
def index():
    #form = NameForm()
    #if form.validate_on_submit():
        #TODO
    #    return redirect(url_for('.index'))
    #return render_template('index.html', form=form, name=session.get('name'),
    #                       known=session.get('known', False),
    #                       current_time=datetime.utcnow())
    return render_template("index.html")


@manage.route('/console1')
@login_required
def console():
    if not (current_user.email_confirmed or current_user.telephone_confirmed):
        flash("当前帐号未激活！请先激活邮箱/手机号！")
        return redirect(url_for("manage.confirm", uid=current_user.get_id()))
    try:
        time_array = time.localtime(current_user.last_login_time)
        otm = time.strftime("%Y %m %d %T", time_array)
        # In order to against the strftime do not work
        t1 = [otm[:4], '年', otm[5:7], '月', otm[8:10], '日 ', otm[-8:]]
        otm = ''.join(t1)

    except:
        otm = "N/A"
    return render_template("manage/console.html", last_login_time=otm)


@manage.route('/confirm/<token>')
def confirm_token(token):
    token = token.encode(encoding="utf-8")
    user = User.query.filter_by(useful_token=token).first()
    if user is None:
        abort(404)
    if user.email_confirmed:
        return redirect('https://console.fiiyu.com')
    if user.confirm(token):
        user.email_confirmed = True
        flash(u"邮箱验证成功！")
    else:
        flash(u"验证链接非法或过期！请重新获取！")
    return redirect('https://console.fiiyu.com')


@manage.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    form = EnableForm()
    if form.validate_on_submit():
        print("true")
        if not form.confirm_type.data:
            # 认证邮件
            token = current_user.generate_confirmation_token()
            send_email(current_user.email, '确认你的邮箱', 'auth/email/confirm', user=current_user, token=token,
                       time=time.strftime("%Y-%m-%d %H:%M:%S"))
            flash("我们已经将激活邮件发送至了你的邮箱，请注意查收！")
            return redirect(url_for('manage.console'))
        else:
            # 认证手机
            # TODO
            return redirect('/confirm')
    return render_template('auth/confirm.html', form=form)


# 过滤未进行激活的用户
@manage.before_app_request
def before_request():
    if request.endpoint is None:
        abort(404)
    if current_user.is_authenticated \
    and not (current_user.email_confirmed or current_user.telephone_confirmed) \
    and request.endpoint[:5] != 'auth.' \
    and request.endpoint[:14] != 'manage.confirm' \
    and request.endpoint[:19] != 'manage.unconfirmed' \
    and request.endpoint != 'static' \
    and request.endpoint != 'api_v1.get_message' \
    and request.endpoint[:15] != 'manage.confirm_':
        print(request.endpoint[:16])
        return redirect(url_for('manage.unconfirmed'))


# 对为激活的用户进行提示
@manage.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.email_confirmed:
        return redirect(url_for('manage.index'))
    return render_template('manage/unconfirmed.html')


@manage.route('/user_info')
@login_required
def user_info():
    return render_template("manage/user_info.html")


@manage.route('/create_group', methods=['GET','POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group = Group()
        group.name = form.name.data
        group.owner_id = current_user.get_id()
        if form.image.data:
            group.image = form.image.data.read()
        db.session.add(group)
        flash("创建成功！")
    return render_template('manage/create_group.html', form=form)


@manage.route('/view_group', methods=['GET', 'POST'])
@login_required
def view_group():
    groups = Group.query.filter_by(Owner=current_user).all()
    member = Member()
    return render_template('manage/view_group.html', groups=groups, member=member)


@manage.route('/group_charge/<group_id>', methods=['GET', 'POST'])
@login_required
def group_charge(group_id):
    group_id = int(base64.b64decode(group_id))
    group = Group.query.get_or_404(group_id)
    group.balance += 55 * 1000
    current_user.balance -= 55 * 1000
    return "充值！%d" % group_id


@manage.route('/group_manage/<group_id>', methods=['GET', 'POST'])
@login_required
def group_manage(group_id):
    group_id = int(base64.b64decode(group_id))
    name = request.form.getlist('name[]')
    tel = request.form.getlist('tel[]')
    address = request.form.getlist('address[]')
    group = Group.query.get_or_404(group_id)
    count = 0
    count1 = 0
    for i in range(len(name)):
        # TODO
        # fix the update member form.
        if name[i] == '' and tel[i] == '' and address[i] == '':
            continue
        member = Member.query.filter_by(name=name[i], tel=tel[i], Group=group).first()
        if member is None:
            member = Member(name=name[i], tel=tel[i], address=address[i], Group=group)
            count += 1
        else:
            count1 += 1
        db.session.add(member)
    flash("提交成功！本次添加了%d个成员，更新了%d个成员的信息" % (count, count1))
    return render_template("manage/group_manage.html",
                           members=Member.query.filter_by(Group=Group.query.get_or_404(group_id)).all())


@manage.route("/charge", methods=["GET"])
@login_required
def charge():
    # return render_template("manage/charge.html")
    a = request.args.get('a', default=-1, type=int)
    if a <= 0:
        return render_template("manage/charge.html")
        # return redirect(url_for("manage.charge"))
    bill = Billing(amount=a, user_id=current_user.uid, token="myrandomtoken" + str(randint(1, 999)) + str(time.time()))
    db.session.add(bill)
    db.session.commit()
    flash("订单创建成功！请支付！%s" % bill.token)
    return redirect(url_for("manage.user_info"))


@manage.route("/charges/<string:token>")
def charge_response(token):
    bill = Billing.query.filter_by(token=token, status=1).first()
    if bill is None:
        return jsonify({"message": "error"})
    bill.User.balance += bill.amount * 100
    bill.status = 2
    bill.finish_time = time.time()
    pm = PersonalMessage(rec_id=bill.User.uid, from_id=0, message="您已充值成功！%d元已存入您的账户！", title="充值成功")
    db.session.add(pm)
    return jsonify({"message": "success",
                    "uid": bill.User.uid,
                    "amount": bill.amount})


@manage.route("/charge_billing")
@login_required
def view_billings():
    bill = Billing.query.filter_by(User=current_user).all()
    return render_template("manage/view_billings.html", bill=bill)


@manage.route("/uploads/xls", methods=["POST"])
def upload_xls():
    files = request.files['file']
    byteio = BytesIO()
    filename = ''.join(random.sample('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890-=', 30))\
               + secure_filename(files.filename)
    files.save(byteio)
    try:
        byteio.seek(0)
        excel = xlrd.open_workbook(file_contents=byteio.getvalue())
        table = excel.sheets()[0]
        data = []
        for i in range(table.nrows):
            data.append(table.row_values(i))
        data.pop(0)
        upload = UploadFile(name=filename, data=json.dumps(data))
        db.session.add(upload)
    except Exception:
        return jsonify({'msg': 'invalid file'}), 400
    finally:
        byteio.close()
        byteio = None
    return jsonify({'file': filename}), 200, {'Access-Control-Allow-Origin': '*'}

