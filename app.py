from flask import Flask, render_template, request, redirect, session , url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # Change time zone
import os
from flask_migrate import Migrate
#auth 
from flask import Blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URL')
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:1234@localhost:3306/tma_db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
migrate = Migrate(app,db)
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
from auth import User 

# Creating Table Todo
class Todo(db.Model):
    __tablename__ = "todo"
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

def create_db_if_not_exists():
    with app.app_context():
        db.create_all()  

create_db_if_not_exists()

# Home route for displaying and adding new items
@app.route('/', methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_datetime = datetime.now(tz=ist_tz)
        date_format = '%d-%m-%Y %H:%M:%S'
        date_str = ist_datetime.strftime(date_format)
        date_created = datetime.strptime(date_str, date_format)
        todo = Todo(title=user_title, desc=user_desc,
                    date_created=date_created,user_id=session["user_id"])
        db.session.add(todo)
        db.session.commit()

    all_items = Todo.query.filter(Todo.user_id == session["user_id"]).all()
    return render_template("index.html", all_todos=all_items)

# Update route
@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update_item(sno):
    item = Todo.query.get_or_404(sno)

    if item.user_id!=session["user_id"]:
        return "Unauthorized", 403
    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        item.title = user_title
        item.desc = user_desc
        db.session.add(item)
        db.session.commit()
        return redirect("/")

    return render_template("update.html", todo=item)

# Delete route
@app.route('/delete/<int:sno>')
def delete_item(sno):
    item = Todo.query.get_or_404(sno)

    if item.user_id !=session["user_id"]:
        return "Unauthorized", 403
    
    db.session.delete(item)
    db.session.commit()
    return redirect('/')

# Search route
@app.route('/search', methods=["GET", "POST"])
def search_item():
    # Get the search query from the URL parameter
    search_query = request.args.get('query')

   # Perform the search query
    result = Todo.query.filter(Todo.title.ilike(f"%{search_query}%"), Todo.user_id == session["user_id"]).all()

    # Render the result
    return render_template('result.html', posts=result)

if __name__ == "__main__":
    app.run(debug=True, port=4000)