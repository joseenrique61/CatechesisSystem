from app import dal
from flask import Blueprint, render_template, session

from app.auth.authentication import login_required

bp = Blueprint('catechist', __name__)

@bp.route("/dashboard", methods=["GET"])
@login_required("Catechist")
def dashboard():
    catechist = dal.get_catechist_by_id(session["id"], include=["Class", "Class.Schedule", "Class.Schedule.Classroom", "Class.Schedule.Classroom.Parish"])
    id_parish = catechist.Class[0].Schedule[0].Classroom.Parish.IDParish if len(catechist.Class) > 0 else -1
    if id_parish == -1:
        return render_template("catechist/dashboard.html",
                           title="Dashboard del párroco", 
                           catechizings=[], 
                           parish_classes=[])
    parish_classes = dal.get_classes_by_parish_id(catechist.IDParish, include=["Catechist.Person", "Catechizing", "Catechizing.Person", "Schedule.Classroom"])
    return render_template("catechist/dashboard.html",
                           title="Dashboard del párroco", 
                           catechizings=dal.get_catechizings_by_parish(catechist.IDParish, 
                                                                       include=["Class", "Class.Level"]), 
                           parish_classes=parish_classes)