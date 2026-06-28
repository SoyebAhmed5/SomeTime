from flask import Flask, redirect,render_template, request, url_for
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_manager, UserMixin, LoginManager, login_required, logout_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import current_user

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

# Configuration for handling files
app.config['UPLOAD_FOLDER']='static/uploads/'
app.config['ALLOWED_EXTENSIONS']={'png','jpg','jpeg','gif'}
app.config['MAX_CONTENT_LENGTH']=16*1024*1024 #16mb max upload size



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
    profileimage = db.Column(db.String(500))
    
    def get_id(self):
        return self.user_id
    
# initializing posts model    
class Posts(db.Model):
    post_id= db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(50))
    name= db.Column(db.String(100))
    title= db.Column(db.String(100))
    description= db.Column(db.String(500))
    image= db.Column(db.String(500))
    date= db.Column(db.String(100))
    time= db.Column(db.String(100))
    likes= db.Column(db.Integer,nullable=True,default=0)


# Initializing the Comments Model
class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    comment = db.Column(db.String(500))
    commentedBy = db.Column(db.String(100))
    commentedOn= db.Column(db.String(100))


class Friends(db.Model):
    friends_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    requested_id = db.Column(db.Integer)
    isAccepted = db.Column(db.String(10))


@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    data=Posts.query.all()
    return render_template("index.html",data=data)

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
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
 
 
    
@app.route("/posts",methods=['GET','POST'])
def posts():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method=="POST":
        email=request.form['email']
        name=request.form['name']
        title=request.form['title']
        description=request.form['description']
        file=request.files['image']
        date=datetime.now()
        datee=date.date()
        time=date.time()
        
        if file and allowed_file(file.filename):
            # save the file in the upload folder
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            
            # write the query to save in db
            query=Posts(email=email,name=name,title=title,description=description,image=file.filename,date=datee,time=time,)
            db.session.add(query)
            db.session.commit()
            flash("Post is Uploaded","info")
            return redirect(url_for('index'))
        else:
            flash("Please use 'png', 'jpg', 'jpeg', 'gif' file format","warning")
        
    
    return render_template("posts.html")
    
# Logic for Likes
@app.route('/like/<int:id>',methods=['GET','POST'])
def like(id):
    post = Posts.query.filter_by(post_id=id).first()
    if post.likes == None:
        post.likes = 1
        db.session.commit()
    post.likes = post.likes + 1
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/comment/<int:id>',methods=['GET','POST'])
def comment(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        comment = request.form['comment']
        commentedBy = request.form['commented']
        commentedOn = datetime.now()
        query = Comments(post_id=id, comment=comment, commentedBy=commentedBy, commentedOn=commentedOn)
        db.session.add(query)
        db.session.commit()
        flash("Comment added successfully","success")
    return redirect(url_for('index'))


@app.route('/viewcomment/<int:id>',methods=['GET','POST'])
def viewcomment(id):
    post = Comments.query.filter_by(post_id=id).all()
    return render_template("comments.html", post=post)


@app.route('/connect',methods=['GET','POST'])
def connect():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    users = Signup.query.all()
    return render_template("connect.html",users=users)


@app.route("/connectfriend/<path:ids>", methods=['GET'])
def connectFriends(ids):
    print(ids)
    data = ids.split("/")
    print(data)
    users = Signup.query.all()
    d1 = Friends.query.filter_by(user_id=data[1]).first()
    d2 = Friends.query.filter_by(requested_id=data[0]).first()
    if d1 or d2:
        flash("Friend request already sent","primary")
        return render_template("connect.html",users=users)
    query = Friends(user_id=data[1], requested_id=data[0], isAccepted="False")
    db.session.add(query)
    db.session.commit()
    flash("Friend request sent successfully","success")
    return render_template("connect.html",users=users)


@app.route("/remove/<path:ids>", methods=['GET'])
def remove(ids):
    print(ids)
    data = ids.split("/")
    print(data)
    users = Signup.query.all()
    d1 = Friends.query.filter_by(user_id=data[1]).first()
    d2 = Friends.query.filter_by(requested_id=data[0]).first()
    if d1 or d2:
        query = f"DELETE FROM `friends` WHERE `friends`.`user_id` = {data[1]} AND `friends`.`requested_id` = {data[0]}"
        with db.engine.begin() as conn:
            conn.exec_driver_sql(query)
            flash("Request Cancelled", "success")
            return render_template("connect.html",users=users)
    return render_template("connect.html",users=users)
     
     
@app.route("/profile",methods=['GET','POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    userdata = Signup.query.filter_by(email=current_user.email).first()
    return render_template("profile.html",userdata=userdata)

if __name__ == "__main__":
    app.run(debug=True)