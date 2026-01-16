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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup",methods=['GET','POST'])
def signup():
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
