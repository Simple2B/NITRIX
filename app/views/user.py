from flask import render_template, Blueprint, request, flash, redirect, url_for
from app.models import User
from app.forms import UserForm
from app.logger  import log

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route("/user_edit")
def edit():
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
            password=user.password_val,
            activated=user.activated.name
            )
        # form.products = Product.query.all()
        # form.resellers = Reseller.query.all()
        form.is_edit = True
        form.save_route = url_for('user.save')
        return render_template(
                "user_edit.html",
                form=form
            )
    form = UserForm()
    # form.products = Product.query.all()
    # form.resellers = Reseller.query.all()
    form.is_edit = False
    form.save_route = url_for('user.save')
    return render_template(
            "user_edit.html",
            form=form
        )


@user_blueprint.route("/user_save", methods=["POST"])
def save():
    log(log.INFO, '/user_save')
    form = UserForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter(User.id == form.id.data).first()
        for k in request.form.keys():
            user.__setattr__(k, form.__getattribute__(k).data)
        user.save()
        log(log.INFO, "User-{} was saved".format(user.id))
        return redirect(url_for('main.users'))
    else:
        flash('Form validation error', 'danger')
        log(log.ERROR, "Form validation error")
    return redirect(url_for('user.edit', id=form.id.data))
