from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import User
from app.forms import UserForm


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route("/user_edit")
def edit():
    if 'id' in request.args:
        id = int(request.args['id'])
        user = User.query.filter(User.id == id).first()
        if user is None:
            flash("Wrong account id.", "danger")
            return redirect(url_for('main.accounts'))
        form = UserForm(
            id=user.id,
            name=user.name,
            user_type=user.user_type.name,
            password=user.password_val,
            activated=user.activated.name
            )

        form.is_edit = True
        form.save_route = url_for('user.save')
        return render_template(
                "user_edit.html",
                form=form
            )
    else:
        form = UserForm()
        form.is_edit = False
        print('form.user_type.data: ', form.user_type.data)
        form.save_route = url_for('user.save')
        return render_template(
                "user_edit.html",
                form=form
            )


@user_blueprint.route("/user_save", methods=["POST"])
def save():
    form = UserForm(request.form)
    print('request.form: ', request.form)
    if form.validate_on_submit():
        if form.id.data > 0:
            user = User.query.filter(User.id == form.id.data).first()
            for k in request.form.keys():
                user.__setattr__(k, form.__getattribute__(k).data)
        else:
            user = User(name=form.name.data, password_val=form.password.data, activated=form.activated.data)
        user.save()
        return redirect(url_for('main.users'))
    else:
        flash('Form validation error', 'danger')
    return redirect(url_for('user.edit', id=form.id.data))
