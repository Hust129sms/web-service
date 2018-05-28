from flask import jsonify, request, make_response
from urllib.parse import quote
import json
from time import time
import random
from io import BytesIO
import xlwt

from . import api_v1
from .views import auth_required
from ..models import db, Group, GroupMember, UploadFile


@api_v1.route('/members/<id>', methods=['GET'])
@auth_required
def get_member_list(user, id):
    group = Group.query.filter_by(iid=id, owner_id=user.uid).first()
    if group is None:
        return jsonify({'msg': 'not found'}), 404
    members = GroupMember.query.filter_by(group_id=group.id).first()
    if members is None:
        return jsonify([
            ['', '', '', '', ''],
        ])
    if members.valid_time + 1800 < time():
        return jsonify({'msg': 'auth required'}), 401
    return jsonify(json.loads(members.data))


@api_v1.route('/members/<id>', methods=['PUT'])
@auth_required
def save_member_list(user, id):
    group = Group.query.filter_by(iid=id, owner_id=user.uid).first()
    if group is None:
        return jsonify({'msg': 'not found'}), 404
    members = GroupMember.query.filter_by(group_id=group.id).first()
    if members is not None:
        if members.valid_time + 1800 < time():
            return jsonify({'msg': 'auth required'}), 401
        member_list = json.loads(request.data)
        result = []
        for row in member_list:
            empty = True
            result.append(row)
            for col in row:
                if col is not None and col != '' and col != ' ':
                    empty = False
                    break
            if empty:
                result.pop()
        if len(result) == 0:
            result = [['', '', '', '', '']]
        group.member_c = len(result)
        members.data = json.dumps(result)
    else:
        members = GroupMember(data=json.dumps(json.loads(request.data)), group_id=group.id)
        db.session.add(members)
    return jsonify({'msg': 'success'})


@api_v1.route('/members/set_file/<filename>')
@auth_required
def set_members_from_file(user, filename):
    upload = UploadFile.query.filter_by(name=filename).first()
    if upload is None or (upload.owner_id != user.uid and upload.owner_id != 0):
        return jsonify({'msg': 'not found'}), 404
    upload.owner_id = user.uid
    db.session.add(upload)
    data = json.loads(upload.data)
    return jsonify(
        {
            'record': len(data),
        }
    )


@api_v1.route('/members/file_confirm/<filename>/<g_id>')
@auth_required
def confirm_file(user, filename, g_id):
    upload = UploadFile.query.filter_by(name=filename, owner_id=user.uid).first()
    group = Group.query.filter_by(owner_id=user.uid, iid=g_id).first()
    if group is None:
        return jsonify({'msg': 'not found'}), 404
    member_list = GroupMember.query.filter_by(group_id=group.id).first()
    if member_list is None:
        member_list = GroupMember(group_id=group.id)
    member_list.data = upload.data
    db.session.add(member_list)
    db.session.delete(upload)
    return jsonify({'msg': 'success'}), 200


@api_v1.route('/members/download/<id>')
@auth_required
def member_download(user, id):
    group = Group.query.filter_by(iid=id, owner_id=user.uid).first()
    if group is None:
        return jsonify({'msg': 'not found'}), 404
    members = GroupMember.query.filter_by(group_id=group.id).first()
    if members is None:
        return jsonify({'msg': 'not found'}), 404
    if members.valid_time + 1800 < time():
        return jsonify({'msg': 'auth required'}), 401
    token = ''.join(random.sample('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890-=', 12))
    members.download_token = token
    return jsonify({'location': token})


@api_v1.route('/download/<iid>/<token>', methods=['GET'])
def get_xls(iid, token):
    members = GroupMember.query.filter_by(download_token=token).all()
    if len(members) == 0:
        return jsonify({'msg': 'not found'}), 404
    member = None
    for item in members:
        if Group.query.get_or_404(item.group_id).iid == int(iid):
            member = item
            member.download_token = 'used-%s' % str(time())[-7:]
            break
    if member is None:
        return jsonify({'msg': 'not found'}), 404
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(u'通讯录')
    datas = json.loads(member.data)
    row = 1
    sheet.write(0, 0, '编号')
    sheet.write(0, 1, '姓名')
    sheet.write(0, 2, '手机号')
    sheet.write(0, 3, '住址')
    sheet.write(0, 4, '备注')
    for items in datas:
        col = 0
        for item in items:
            sheet.write(row, col, item)
            col += 1
        row += 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    resp = make_response()
    resp.status_code = 200
    resp.data = output.getvalue()
    resp.mimetype = 'application/vnd.ms-excel'
    resp.headers['Content-Disposition'] = u'attachment;filename=[FIIYU]%s.xls' % \
                                          quote(Group.query.get_or_404(member.group_id).name)
    return resp
