from flask import jsonify, request, json, abort, url_for
from flask_login import current_user, login_required
from time import time, strftime, localtime
from functools import wraps
import base64
import urllib.parse

from ..models import PersonalMessage, db, MessageRecord, User, Group, Member, ChargeRecord, Billing, SMSTpl, GroupMember, UploadFile
from . import api_v1
from .tools import get_auth_token, show_type, createPhoneCode, getpay
from ..tools.mail_thread import send_email
from ..tools.signals import send_verify_code
import os


@api_v1.after_request
def add_header_response(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Range')
    return response


# Decorator to get user object in the headers
def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        try:
            token = token[7:]
        except:
            return abort(403)
        user = User.query.filter_by(auth_token=token).first()
        if user is not None:
            token_origin = base64.b64decode(token.encode())
            expire_time = token_origin.decode().split(":")[0]
            if float(expire_time) < time():
                abort(403)
            return func(user, *args, **kwargs)
        else:
            return abort(403)
    return wrapper


@api_v1.route("/get_message")
def get_message():
    pms = PersonalMessage.query.filter_by(rec_id=current_user.uid).order_by(db.desc(PersonalMessage.time)).all()
    js = {}
    i = 0
    for pm in pms:
        js[i] = {"title": pm.title,
                 "message": pm.message,
                 "time": pm.time,
                 "status": pm.status,
                 "from": pm.from_id,
                 "id": pm.id}
        i += 1
    return jsonify(js)


@api_v1.route("/read_message/<int:m_id>")
@login_required
def read_message(m_id):
    if m_id == 0:
        pms = PersonalMessage.query.filter_by(rec_id=current_user.uid, status=False).all()
        for pm in pms:
            pm.status = True
        return jsonify({'message': 'Marked all as read'})
    pms = PersonalMessage.query.filter_by(rec_id=current_user.uid, id=m_id).first()
    pms.status = True
    return jsonify({'message': 'marked as read'})


@api_v1.route("/login", methods=["POST"])
def get_token():
    try:
        json_data = request.get_json(force=True)
        user = User.query.filter_by(email=json_data['email']).first()
        if user is None:
            raise TimeoutError
        if user.verify_password(json_data['password']):
            user.auth_token = get_auth_token(json_data['email'])
            user.auth_token_expire = int(time() + 1800)
            db.session.add(user)
            return jsonify({
                "status": 1,
                "token": user.auth_token,
                "expire_time": user.auth_token_expire,

            })
        else:
            return jsonify({
                "status": 0
            }), 403
    except:
        return jsonify({
                "status": 0
            }), 403


@api_v1.route("/sms_response",methods=['GET','POST'])
def sms_response():
    values = request.get_data().decode("utf8").split('=')[1].split(';')
    for value in values:
        response = MessageRecord(content=urllib.parse.unquote(value,'gbk'))
        db.session.add(response)
        print(response.content)
    return "0"


@api_v1.route("/balance/<id>", methods=['GET'])
@auth_required
def get_balance(user, id=1):
    balance = user.balance / 100
    return jsonify({"balance": balance})


@api_v1.route("/user/", methods=['GET'])
@api_v1.route("/user/<id>", methods=['GET'])
@auth_required
def get_user_info(user, id=1):
    data = {
        'id': user.username,
        'email': user.email,
        'telephone': user.telephone[:3] + '****' + user.telephone[-4:],
        'email_c': user.email_confirmed,
        'telephone_c': user.telephone_confirmed,
        'last': user.last_login_time,
        'student': user.student_auth,
        "id_card": user.id_card[:5] + '*************' if user.id_card else None,
        "student_no": user.student_no,
        "school": user.school,
        "qq": user.qq,
        "username": user.username,
        "log_level": user.log_level,
        "name": user.name,
    }
    return jsonify(data)


@api_v1.route("/user/<id>", methods=['PUT'])
@auth_required
def update_user_info(user, id=1):
    static_record = ['id_card', 'telephone', 'last', 'student_no', 'email', 'username', 'email_c', 'telephone_c',
                     'student']
    map_table = {
        "telephone_c": "telephone_confirmed",
        "email_c": "email_confirmed",
        "student": "student_auth",
        "last": "last_login_time"
    }
    try:
        user_data = request.get_json()

    except:
        return jsonify({'msg': 'fail'}), 400

    for keys in user_data:
        key = keys if keys not in map_table else map_table[keys]
        if user_data[keys] and (keys not in static_record or exec('user.' + key + ' is not None')):#为可修改项或该记录为空
            exec('user.' + key + '="' + str(user_data[keys]) + '"')
    return jsonify({'msg': 'success'})


def create_products():
    print(request.get_json())
    return jsonify({'status': 'success'})


@api_v1.route('/check_email/<id>', methods=['GET'])
@auth_required
def check_email(user, id):
    token = user.generate_confirmation_token()

    send_email(user.email, '确认你的邮箱', 'auth/email/confirm', user=user, token=token,
                time=strftime("%Y-%m-%d %H:%M:%S"))
    return jsonify({'status': 'success'})


@api_v1.route('/send_sms/<id>', methods=['GET'])
@auth_required
def send_auth_sms(user, id):
    if id == 'send_sms':
        if user.telephone_confirmed :
            return jsonify({'msg': 'forbidden'}), 403
        if time() - user.telephone_confirmed_code_time < 60:
            return jsonify({'msg': 'please wait', 'time': int(time() - user.telephone_confirmed_code_time)}), 403
        user.telephone_confirmed_code = createPhoneCode()
        user.telephone_confirmed_code_time = time()
        send_verify_code.delay(user.telephone, os.environ.get('API_KEY'), os.environ.get('TPL_ID'),
                               code=user.telephone_confirmed_code)
        return jsonify({'msg': 'success'})
    if id[:12] == 'unlock_group':
        if time() - user.telephone_confirmed_code_time < 60:
            return jsonify({'msg': 'please wait', 'time': int(time() - user.telephone_confirmed_code_time)}), 403
        user.telephone_confirmed_code = createPhoneCode()
        user.telephone_confirmed_code_time = time()
        group = Group.query.filter_by(iid=id[13:], owner_id=user.uid).first()
        if group is None:
            return jsonify({'msg': 'not found'})
        send_verify_code.delay(user.telephone, os.environ.get('API_KEY'), os.environ.get('TPL_ID_2'),
                               group=group.name, code=user.telephone_confirmed_code)
        return jsonify({'msg': 'success'})


@api_v1.route('/confirm_sms/<id>', methods=['GET'])
@auth_required
def confirm_sms(user, id):
    if user.telephone_confirmed:
        return jsonify({'msg': 'forbidden'}), 403
    if time() - user.telephone_confirmed_code_time > 60:
        return jsonify({'msg': 'code timeout'}), 403
    if user.telephone_confirmed_code == id:
        user.telephone_confirmed = True
        return jsonify({'msg': 'success'})
    else:
        return jsonify({'msg': 'wrong number'}), 404


@api_v1.route('/charge_group/<iid>-<amount>',methods=['GET'])
@auth_required
def charge_group(user, iid, amount):
    iid = int(iid)
    amount = int(float(amount) * 100)
    group = Group.query.filter_by(owner_id=user.uid, iid=iid).first()
    if group is None:
        return jsonify({'msg': 'error', 'error': '找不到圈子'}), 404
    if amount > user.balance:
        return jsonify({'msg': 'error', 'error': '账户余额不足'}), 400
    bill = ChargeRecord(amount=amount/100, out_account_id=user.uid, in_group_id=group.id, deal_state=1)
    db.session.add(bill)
    user.balance -= amount
    group.balance += amount
    db.session.add(user)
    db.session.add(group)
    return jsonify({'msg': 'success'})


@api_v1.route('/charge_group_history', methods=['GET'])
@auth_required
def charge_group_history(user):
    range = json.loads(request.args.get('range'))
    bills = ChargeRecord.query.filter_by(out_account_id=user.uid).order_by(ChargeRecord.time.desc()).offset(range[0]).limit(range[1] - range[0]).all()
    datas = []
    for bill in bills:
        data = {
            'amount': '%.2f元' % bill.amount,
            'in_group': Group.query.filter_by(id=bill.in_group_id).first().name,
            'time': strftime("%Y-%m-%d %H:%M:%S", localtime(bill.time)),
            'id': bill.id,
        }
        datas.append(data)
    max_counter = ChargeRecord.query.filter_by(out_account_id=user.uid).count()
    if max_counter < range[1]:
        range[1] = max_counter
    return jsonify(datas), {'Content-Range': 'posts ' + str(range[0]) + '-' +
                                             str(range[1]) + '/' + str(max_counter)}


@api_v1.route('/bills', methods=['GET'])
@auth_required
def get_bills(user):
    range = json.loads(request.args.get('range'))
    bills = Billing.query.filter_by(user_id=user.uid).order_by(Billing.create_time.desc()).offset(range[0]).limit(range[1]-range[0]).all()
    datas = []
    type = ['支付宝', '微信', '人工', '网银']
    status = ['', '待支付⌛️', '已支付☑️', '完成✅', '已关闭⛔️']
    for bill in bills:
        data = {
            'amount': '%.2f元' % bill.amount,
            'type': type[int(bill.status / 10)],
            'time': strftime("%Y-%m-%d %H:%M:%S", localtime(bill.finish_time or bill.create_time)),
            'id': bill.id,
            'status': status[bill.status % 10]
        }
        datas.append(data)
    max_counter = Billing.query.filter_by(user_id=user.uid).count()
    if max_counter < range[1]:
        range[1] = max_counter
    return jsonify(datas), {'Content-Range': 'posts ' + str(range[0]) + '-' +
                                             str(range[1]) + '/' + str(max_counter)}


@api_v1.route('/bills/<amount>-<type>', methods=['GET'])
@auth_required
def charge(user, amount, type):
    types = ['支付宝', '微信', '人工', '网银']
    bill = Billing(status=int(type)*10+1, user_id=user.uid, amount=amount,
                   token=get_auth_token("%s,%d" % (types[int(type)], int(amount)), 3600))
    db.session.add(bill)
    db.session.commit()
    getpay(type, amount, bill.id, bill.token)
    return jsonify({'msg': 'success', 'url': getpay(type, amount, bill.id, bill.token)})


@api_v1.route('/unlock/<g_id>/<code>')
@auth_required
def unlock_g_with_tel(user, g_id, code):
    if user.telephone_confirmed_code == code and user.telephone_confirmed_code_time + 300 > time():
        user.telephone_confirmed = True
        group = Group.query.filter_by(iid=g_id, owner_id=user.uid).first()
        if group is None:
            return jsonify({'msg': 'not found'}), 404
        members = GroupMember.query.filter_by(group_id=group.id).first()
        members.valid_time = time()
        return jsonify({'msg': 'success'})
    return jsonify({'msg': 'not found'}), 404

