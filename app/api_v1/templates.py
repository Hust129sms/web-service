from time import strftime, localtime
from flask import jsonify, request, json

from . import api_v1
from .views import auth_required

from ..models import SMSTpl, db, Group


@api_v1.route('/templates', methods=['GET'])
@auth_required
def get_tpls(user):
    range = json.loads(request.args.get('range'))
    try:
        key = json.loads(request.args.get('filter'))
        group = key['group']
    except KeyError:
        group = None
    try:
        filter_content = key['content']
    except KeyError:
        filter_content = None
    try:
        filter_status = key['status']
    except KeyError:
        filter_status = None
    datas = []
    status = ['审核中', '审核通过', '审核失败，请修改后再申请，原因：', '保留', '保留']
    max_counter = 0
    groups = Group.query.filter_by(owner_id=user.uid)
    if group is not None and group != 0:
        groups = groups.filter_by(iid=group)
    groups = groups.all()
    if groups is None:
        return jsonify({'msg': 'not found'}), 404
    for group in groups:
        tpls = SMSTpl.query.filter_by(group_id=group.id)
        if filter_content is not None:
            tpls = tpls.filter(SMSTpl.content.like('%' + filter_content + '%'))
        if filter_status is not None:
            tpls = tpls.filter_by(status=filter_status)
        tpls = tpls.all()
        for tpl in tpls:
            datas.append({
                'id': tpl.id,
                'content': tpl.content,
                'time': strftime("", localtime(int(tpl.time))),
                'status': status[int(tpl.status)] + (('%s' % tpl.reason) if tpl.status == 2 else ''),
                'group': group.name
            })
            max_counter += 1
    if max_counter < range[1]:
        range[1] = max_counter
    return jsonify(datas[range[0]:range[1]]), {'Content-Range': 'posts ' + str(range[0]) + '-' +
                                             str(range[1]) + '/' + str(max_counter)}


@api_v1.route('/templates', methods=['POST'])
@auth_required
def create_template(user):
    data = request.get_json(force=True)
    group = Group.query.filter_by(owner_id=user.uid, iid=data['group_id']).first()
    if group is None:
        return jsonify({'msg': 'not found'}), 404
    tpl = SMSTpl(group_id=group.id, content='【%s】%s' % (data['sig'], data['content']), title=data['title'])
    db.session.add(tpl)
    return jsonify({'msg': 'success'})


@api_v1.route('/templates/<id>',methods=['GET'])
@auth_required
def get_one_template(user, id):
    tpl = SMSTpl.query.filter_by(id=id).first()
    if tpl.Group.owner_id != user.uid:
        return jsonify({'msg': 'forbidden'}), 403
    if tpl is None:
        return jsonify({'msg':'not found'}), 404
    return jsonify({'id': id, 'content': tpl.content, 'status': tpl.status})
    pass


@api_v1.route('/templates/<id>', methods=['DELETE'])
@auth_required
def delete_template(user, id):
    tpl = SMSTpl.query.filter_by(id=id).first()
    if Group.query.filter_by(id=tpl.group_id).first().owner_id != user.uid:
        return jsonify({'msg': 'forbidden'}), 403
    if tpl is None:
        return jsonify({'msg': 'not found'}), 404
    db.session.delete(tpl)
    return jsonify({'msg': 'success'})

