from flask import Flask, redirect,render_template, request, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_manager, UserMixin, LoginManager, login_required, logout_user

import pymysql
pymysql.install_as_MySQLdb()


local_server = True
app=Flask(__name__)
app.secret_key="=Soyebahmed@123"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# db connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/socialmedia'
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# initializing signup model
class Signup(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
    phone = db.Column(db.Integer,unique=True)
    
    def get_id(self):
        return self.user_id
    
# initializing posts model    
class Posts(db.Model):
    post_id= db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(50))
    title= db.Column(db.String(100))
    description= db.Column(db.String(500))
    image= db.Column(db.String(500))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        firstName=request.form.get("fname")
        lastName=request.form.get("lname")
        email=request.form.get("email")
        phoneNumber=request.form.get("phone")
        password=request.form.get("pass1")
        confirmPassword=request.form.get("pass2")
        print(firstName,lastName,email,phoneNumber,password,confirmPassword)
        if password!=confirmPassword:
            flash("Passwords do not match","warning")
            return redirect(url_for('signup'))
        
        fetchemail=Signup.query.filter_by(email=email).first()
        fetchphone=Signup.query.filter_by(phone=phoneNumber).first()
        if fetchemail or fetchphone:
            flash("User already exists","warning")
            return redirect(url_for('signup'))
        
        if len(phoneNumber) !=10:
            flash("Phone number must be 10 digits","warning")
            return redirect(url_for('signup'))
            
        gen_pass=generate_password_hash(password)    
        query = f"INSERT into `signup` (`first_name`,`last_name`,`email`,`password`,`phone`) VALUES ('{firstName}','{lastName}','{email}','{gen_pass}','{phoneNumber}')"
        with db.engine.begin() as conn:
            conn.exec_driver_sql(query)
            flash("Signup successful !.","success")
            return redirect(url_for('login'))
            
    return render_template("signup.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("pass1")
        user = Signup.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful !.","success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password","danger")
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Success","primary")
    return redirect(url_for('login'))


@app.route("/test/")
def test():
    try:
        sql_query = "select * from test"
        with db.engine.begin() as conn:
            response = conn.exec_driver_sql(sql_query).all()
            print(response)
            return "Database is connected"
    except Exception as e:
        return f"Database is not Connected, {e}"
    
@app.route("/posts",methods=['GET','POST'])
def posts():
    return render_template("posts.html")
    

