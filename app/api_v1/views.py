from flask import jsonify, request, json, abort, url_for
from flask_login import current_user, login_required
from time import time
from functools import wraps
import urllib.parse

from ..models import PersonalMessage, db, MessageRecord, User, Group, Member
from . import api_v1
from .tools import get_auth_token, show_type


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


@api_v1.after_request
def add_header_response(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Range')
    return response


@api_v1.route("/balance/<id>", methods=['GET'])
@auth_required
def get_balance(user, id=1):
    balance = user.balance / 100
    return jsonify({"balance": balance})


@api_v1.route("/user/<id>", methods=['GET'])
@auth_required
def get_user_info(user, id=1):
    data = {
        'email': user.email,
        'telephone': user.telephone,
        'email_c': user.email_confirmed,
        'telephone_c': user.telephone_confirmed,
        'last': user.last_login_time,
        'student': user.student_auth,
        "id_card": user.id_card[5:] + '*************' if user.id_card else None,
        "student_no": user.student_no,
        "school": user.school,
        "qq": user.qq,
        "username": user.username,
        "log_level": user.log_level,
    }
    return jsonify(data)

@api_v1.route("/user/<id>", methods=['PUT'])
@auth_required
def update_user_info(user, id=1):
    static_record = ['id_card', 'telephone', 'last', 'student_no', 'email', 'username', 'email_c', 'telephone_c',
                     'student']
    try:
        user_data = request.get_json()
        for keys in user_data:
            if keys not in static_record or not eval('user.' + keys) : #为可修改项或该记录为空
                eval('user.' + keys + '=' + user_data[keys])
        return jsonify({'msg': 'success'})
    except:
        return jsonify({'msg': 'fail'}), 400



@api_v1.route("/groups", methods=['POST'])
@auth_required
def create_group(user):
    try:
        group_data = request.get_json()
    except:
        return jsonify({'status': 'fail'}), 400
    # TODO codes to create group
    try:
        group = Group(iid=Group.query.filter_by(owner_id=user.uid).sort_by(Group.iid.desc()).first().iid + 1)
    except:
        group = Group(iid=1, owner_id=user.uid)
    try:
        # TODO code to add data to database
        group.name = group_data['group_name']
        try:
            group.type = {"Association": 0, "Student_union": 1, "Team": 2, "Classes": 3, "Collage": 4, "Match": 5}[group_data['group_type']]
        except KeyError:
            group.type = -1
        group.tel = group_data['telephone']
    except:
        return jsonify({'status': 'error'}), 400
    db.session.add(group)
    db.session.commit()
    return jsonify({'status': 'success'}), 201, {'Location': url_for('api_v1.get_one_group', id = group.id)}


@api_v1.route("/groups", methods=['GET'])
@api_v1.route("/products", methods=['GET'])
@auth_required
def get_group_list(user):
    sort = request.args.get('sort')
    range = request.args.get('range')
    filter = request.args.get('filter')
    sort_l = list(eval(sort))
    range = list(eval(range))
    sort_i = Group.id
    if sort_l[1] == 'DESC':
        if sort_l[0] == 'id':
            sort_i = Group.iid.desc()
        elif sort_l[0] == 'name':
            sort_i = Group.name.desc()
        elif sort_l[0] == 'type':
            sort_i = Group.type.desc()
        elif sort_l[0] == 'balance':
            sort_i = Group.balance.desc()
        elif sort_l[0] == 'members':
            sort_i = Group.member_c.desc()
    else:
        if sort_l[0] == 'id':
            sort_i = Group.iid.asc()
        elif sort_l[0] == 'name':
            sort_i = Group.name.asc()
        elif sort_l[0] == 'type':
            sort_i = Group.type.asc()
        elif sort_l[0] == 'balance':
            sort_i = Group.balance.asc()
        elif sort_l[0] == 'members':
            sort_i = Group.member_c.asc()
    groups = Group.query.filter_by(owner_id=user.uid).order_by(sort_i).offset(range[0]).limit(range[1] - range[0]).all()
    datas = []
    for group in groups:
        group_data = {
            'id': group.iid,
            'name': group.name,
            'balance': str(group.balance/100) + '元',
            'type': show_type(group.type),
            'manager_telephone': group.tel or group.Owner.telephone,
            'role_json': group.role_json,
            'description': group.name,
            'members': group.member_c
        }
        datas.append(group_data)
    max_counter = Group.query.filter_by(owner_id=user.uid).count()
    if max_counter < range[1]:
        range[1] = max_counter
    return jsonify(datas), {'Content-Range': 'posts ' + str(range[0]) + '-' +
                                                                           str(range[1]) + '/' + str(max_counter)}


@api_v1.route('/groups/<int:id>', methods=['GET'])
@auth_required
def get_one_group(user, id):
    group = Group.query.filter_by(owner_id=user.uid).filter_by(iid=id).first()
    if group is None:
        return jsonify({'status': 'not found'}), 404
    return jsonify(
        {
            'id': group.iid,
            'group_name': group.name,
            'group_type': group.type,
            'telephone': group.tel or group.Owner.telephone,
            'description': group.name,
            'members': group.member_c
        }
    )
    pass


@api_v1.route('/groups/<int:id>', methods=['PUT'])
@auth_required
def update_one_group(user, id):
    group = Group.query.filter_by(owner_id=user.uid).filter_by(iid=id).first()
    group_data = request.get_json()
    if group is None:
        return jsonify({'status': 'not found'}), 404
    # TODO code for modify group
    return jsonify({'status': 'success'}), 200


@api_v1.route('/groups/<int:id>', methods=['DELETE'])
@auth_required
def delete_one_group(user, id):
    group = Group.query.filter_by(owner_id=user.uid).filter_by(iid=id).first()
    if group is None:
        return jsonify({'status': 'not found'}), 404
    db.session.remove(group)
    return jsonify({'status': 'success'}), 200

def create_products():
    print(request.get_json())
    return jsonify({'status': 'success'})



