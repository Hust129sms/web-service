from flask_login import login_required, current_user
from flask import request, jsonify, flash, redirect, url_for, render_template
import json

from . import form
from ..models import Form, db, FormData


@form.route('/create_form', methods=['GET'])
@login_required
def create_form():
    if current_user.owned_group.query.count() == 0:
        flash("请先创立一个组织再进行该操作！")
        return redirect(url_for("manage.biew_group"))
    return render_template("index.html")


@form.route('/create_form', methods=['POST'])
@login_required
def create_form_p():
    if current_user.owned_group.query.count() == 0:
        return jsonify({"message": "no enough group", "code": 1})

    t = json.loads(request.form)
    # TODO validate t
    form = Form(data=t, owner_id=current_user.uid)
    db.session.add(form)
    return jsonify({"message": "success",
                    'code': 0})

@form.route('/f/<string:f_id>', methods=['GET', 'POST'])
def submit_form(f_id):
    if request.method == 'GET':
        return render_template("index.html")
    form = Form.get_by_fid()
    data = FormData(form_id=form.id, data=request.data)
    flash("提交成功")
    return jsonify({"message": "success", "code": 0})
