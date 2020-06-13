from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import User
from app.forms import UserForm
from app.logger import log
from ..database import db


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route("/user_edit")
@login_required
def edit():
    if current_user.user_type.name not in ['super_admin']:
        return redirect(url_for("main.index"))
    log(log.INFO, '/user_edit')
    if 'id' in request.args:
        id = int(request.args['id'])
        user = User.query.filter(User.id == id).first()
        if user is None:
            flash("Wrong account id.", "danger")
            log(log.WARNING, "Wrong account id.")
            return redirect(url_for('main.accounts'))
        form = UserForm(
            id=user.id,
            name=user.name,
            user_type=user.user_type.name,
            activated=user.activated.name
            )

        form.is_edit = True
        form.save_route = url_for('user.save')
        form.delete_route = url_for('user.delete')
        form.close_button = url_for('main.users')
        return render_template(
                "user_edit.html",
                form=form
            )
    else:
        form = UserForm()
        form.is_edit = False
        form.save_route = url_for('user.save')
        form.delete_route = url_for('user.delete')
        form.close_button = url_for('main.users')
        return render_template(
                "user_edit.html",
                form=form
            )


@user_blueprint.route("/user_save", methods=["POST"])
@login_required
def save():
    if current_user.user_type.name not in ['super_admin']:
        return redirect(url_for("main.index"))
    log(log.INFO, '/user_save')
    form = UserForm(request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            user = User.query.filter(User.id == form.id.data).first()
            if user is None:
                flash("Wrong user id.", "danger")
                return redirect(url_for('main.users'))
            for k in request.form.keys():
                user.__setattr__(k, form.__getattribute__(k).data)
        else:
            user = User(name=form.name.data, activated=form.activated.data)
            user.password = form.password.data
        user.save()
        log(log.INFO, "User-{} was saved".format(user.id))
        return redirect(url_for('main.users'))
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error")
    return redirect(url_for('user.edit', id=form.id.data))


@user_blueprint.route("/user_delete", methods=["GET"])
@login_required
def delete():
    if current_user.user_type.name not in ['super_admin']:
        return redirect(url_for("main.index"))
    if 'id' in request.args:
        user_id = int(request.args['id'])
        User.query.filter(User.id == user_id).delete()
        db.session.commit()
        return redirect(url_for('main.users'))
    flash('Wrong request', 'danger')
    return redirect(url_for('main.users'))
