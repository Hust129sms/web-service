from flask import jsonify
from flask_login import login_required, current_user
from ..models import PersonalMessage, db
from . import api_v1


@api_v1.route("/get_message")
@login_required
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
    pms = PersonalMessage.query.filter_by(rec_id=current_user.uid, id=m_id).first()
    pms.status = True
    return jsonify({'message': 'marked as read'})
