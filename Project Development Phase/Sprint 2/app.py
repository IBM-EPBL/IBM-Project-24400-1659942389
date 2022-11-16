from flask import *
import ibm_db
import uuid
import hashlib
import os

con = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=psn93818;PWD=bnFxnbbGszyGKiLJ",'','')

app = Flask(__name__)
app.secret_key = '!@#GCEECE*&^'

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/profile/<name>')
def profile(name):
   users = []
   sql = f"SELECT * FROM USERS WHERE name='{escape(name)}'"
   stmt = ibm_db.exec_immediate(con, sql)
   dictionary = ibm_db.fetch_both(stmt)
   while dictionary != False:
      # print ("The Name is : ",  dictionary)
      users.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)

   if users:
      return render_template('profile.html', users=users)

@app.route('/about')
def about():
   return render_template('about.html')

@app.route("/dashboard",methods=["get"])
def dashboard():
    
   uid = str(session.get("uniqid")+'')
   sql = f"""select * from "PSN93818"."REQUEST" Where "UNIQID"!='{uid}' AND "STATUS"='waiting'"""

   sql += ";"



   arr = []
   larr = []
   barr = []
   harr = []


   stmt = ibm_db.exec_immediate(con, sql)
   tuple = ibm_db.fetch_tuple(stmt)
   while tuple != False:
      arr.append(tuple)
      tuple = ibm_db.fetch_tuple(stmt)

   print("arr")
   print(arr)
   print(larr)
   print(harr)
   print(barr)
   return render_template("dashboard.html",requestarray=arr,locarr=larr,bgarr=barr,hosarr=harr)

@app.route("/changestatus/<id>",methods=["get"])
def chngstatus(id):

    print(id)
    uid = str(session.get("uniqid"))+""
    name = str(session.get("name"))+""
    sql = f"""UPDATE "PSN93818"."REQUEST" SET "DONORID" = '{uid}', "DONORNAME" = '{name}',"STATUS"='accepted' WHERE "FUNIQID" = '{id}';"""
    stmt = ibm_db.prepare(con, sql)
    ibm_db.execute(stmt)
    print("suc")

    return "success"


@app.route("/signin",methods=["POST"])
def signin():

   username = request.form['email']
   password = request.form['password']

   sql = """SELECT * FROM "PSN93818"."USERS" where email = '{usr}' AND password = '{pas}';""".format(usr=username,pas=password)

   stmt = ibm_db.exec_immediate(con, sql)
   user = ""
   while ibm_db.fetch_row(stmt) != False:
      user = ibm_db.result(stmt, 1)

   name = ""
   if(user == username):

      sql1 = """SELECT * FROM "PSN93818"."USERS" where email = '{usr}';""".format(usr=username)
      stmt1 = ibm_db.exec_immediate(con, sql1)
      uniqid = ""
      while ibm_db.fetch_row(stmt1) != False:
         uniqid = ibm_db.result(stmt1, 7)
         name = ibm_db.result(stmt1, 0)
      print(name)
      session['username'] = username
      session['name'] = name
      session['uniqid'] = uniqid

      return redirect(url_for("profile",name=session["name"]))

   return render_template("signin.html")

@app.route("/signin",methods=["GET"])
def signin_get():

    print(con)
    return render_template("signin.html")

@app.route('/signup',methods = ["POST"])
def signup():
   if request.method == 'POST':
      name = request.form['name']
      email = request.form['email']
      phone = request.form['phone']
      city = request.form['city']
      blood_group = request.form['blood_group']
      password = request.form['password']
      password1 =request.form['password1']

      uniqid = uuid.uuid4().hex

      print(name,email,phone,city,blood_group,password,password1)

      sql = """INSERT INTO  "PSN93818"."USERS"  VALUES(?,?,?,?,?,?,?,?);"""
      stmt = ibm_db.prepare(con, sql)

      ibm_db.bind_param(stmt, 1, name)
      ibm_db.bind_param(stmt, 2, email)
      ibm_db.bind_param(stmt, 3, phone)
      ibm_db.bind_param(stmt, 4, city)
      ibm_db.bind_param(stmt, 5, blood_group)
      ibm_db.bind_param(stmt, 6, password)
      ibm_db.bind_param(stmt, 7, password1)
      ibm_db.bind_param(stmt, 8, uniqid)
      ibm_db.execute(stmt)

      return redirect("/signin")

   return render_template("signup.html")

@app.route("/signup",methods=["GET"])
def signup_get():
   return render_template("signup.html")

@app.route("/requestform",methods=["get"])
def reqform_get():
   return render_template("form.html")


@app.route("/requestform",methods=["post"])
def reqform_post():
   name = request.form['name']
   bg = request.form['bg']
   city = request.form['city']
   hosp = request.form['hosp']

   formid = (hashlib.sha1((uuid.uuid4().hex + session.get("uniqid")).encode())).hexdigest() + ""
   print(formid)
   uid = str(session.get("uniqid")) + ""
   
   sql = f"""INSERT INTO  "PSN93818"."REQUEST" ("UNIQID","FUNIQID","NAME","BG","CITY","HOSP","STATUS") VALUES('{uid}','{formid}','{name}','{bg}','{city}','{hosp}','waiting');"""

   stmt = ibm_db.prepare(con, sql)
   ibm_db.execute(stmt)

   return redirect("/dashboard")

@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for("signin"))


if __name__ == '__main__':
   app.run(debug = True)

