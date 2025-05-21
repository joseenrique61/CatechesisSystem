from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.parish_priest.forms import CatechizingForm
from app.main.data.dtos.base_dtos import CatechizingDTO
from app import dal

bp = Blueprint('parish_priest', __name__)

# TODO: Login required decorator
@bp.route('/catechizing/create', methods=['GET', 'POST'])
def register_catechizing():
    form = CatechizingForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        catechizing = CatechizingDTO.from_other_obj(form)

        # try:
        #     catechizing, success = dal.register_catechizing(catechizing)
        #     if not success:
        #         return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        # except Exception as e:
        #     print(f"Error inserting parish priest: {e}")
        #     flash('Error al registrar el sacerdote.', 'danger')
        #     return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)
        
        # flash(f'¡Sacerdote {catechizing.Person.FirstName} {catechizing.Person.FirstSurname} registrado exitosamente!', 'success')

    return render_template('admin/register_parish_priest.html', title='Registrar Sacerdote', form=form)