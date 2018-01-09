from . import api_v1

from flask import jsonify, request, json, url_for

from .views import auth_required
from ..models import db, Group, Member, ChargeRecord
from .tools import show_type


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
        group.short_name = group_data['group_shortname']
        group.description = group_data['description']
        group.manager_name = group_data['manager_name']
        group.email = group_data['email']
    except:
        return jsonify({'status': 'error'}), 400
    db.session.add(group)
    db.session.commit()
    return jsonify({'status': 'success'}), 201, {'Location': url_for('api_v1.get_one_group', id = group.id)}


@api_v1.route("/groups", methods=['GET'])
@auth_required
def get_group_list(user):
    sort = request.args.get('sort')
    range = request.args.get('range')
    filter = request.args.get('filter')
    sort_l = json.loads(sort)
    range = json.loads(range)
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
            'members': group.member_c,
            'group_shortname': group.short_name,
            'manager': group.manager_name,
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
            'telephone': group.tel or group.Owner.telephone,
            'group_description': group.description,
            'members': group.member_c,
            'group_shortname': group.short_name,
            'group_type': {"0": "Association", "1": "Student_union", "2": "Team", "3": "Classes", "4": "Collage", "5": "Match"}[str(group.type)],
            'manager_name': group.manager_name,
            'email': group.email
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
    try:
        group.type = {"Association": 0, "Student_union": 1, "Team": 2, "Classes": 3, "Collage": 4, "Match": 5}[
            group_data['group_type']]
    except KeyError:
        group.type = -1
    try:
        group.tel = group_data['telephone']
        group.short_name = group_data['group_shortname']
        group.description = group_data['group_description']
        group.manager_name = group_data['manager_name']
        group.email = group_data['email']
    except KeyError:
        pass
    return jsonify({'status': 'success'}), 200


@api_v1.route('/groups/<int:id>', methods=['DELETE'])
@auth_required
def delete_one_group(user, id):
    group = Group.query.filter_by(owner_id=user.uid).filter_by(iid=id).first()
    if group is None:
        return jsonify({'status': 'not found'}), 404
    members = Member.query.filter_by(group_id=group.id).all()
    user.balance += group.balance
    billing = ChargeRecord(amount=-group.balance/100, out_account_id=user.uid, in_group_id=group.id, deal_state=10)
    db.session.add(billing)
    group.owner_id = 0
    for member in members:
        db.session.delete(member)
    return jsonify({'status': 'success'}), 200
