from flask import Flask, redirect,render_template, request, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask import flash


local_server = True
app=Flask(__name__)
app.secret_key="=Soyebahmed@123"

# db connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/socialmedia'
db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# initializing signup model

class Signup(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
    phone = db.Column(db.Integer,unique=True)



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
            
            
        query = f"INSERT into `signup` (`first_name`,`last_name`,`email`,`password`,`phone`) VALUES ('{firstName}','{lastName}','{email}','{password}','{phoneNumber}')"
        with db.engine.begin() as conn:
            conn.exec_driver_sql(query)
            flash("Signup successful !.","success")
            return redirect(url_for('login'))
            
    return render_template("signup.html")

@app.route("/login",methods=['GET','POST'])
def login():
    return render_template("login.html")



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
    
if __name__=="__main__":
    app.run(debug=False)
