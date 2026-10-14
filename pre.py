from flask import Flask, render_template, redirect, url_for,session,request
import os,json
from dotenv import load_dotenv
from src.generate_kundali import get_output
from collections import Counter

from src.user_authantication import valid_user
from src.lushogrid import loshu_grid_from_dob


load_dotenv()

app = Flask(__name__)



app.config['SECRET_KEY'] = os.getenv("FLASK_API_KEY")




# ---------- MAIN LOGIN ----------
@app.route("/",methods=["POST","GET"])
def login():
    if request.method =="POST":
        email =request.form["email"]
        password = request.form["password"]
        
        print("email:",email)
        print("password:",password)

        if valid_user(email,password):
            return redirect(url_for("home"))
        else:
            # and add message user is not valid
            render_template("login.html")
    return render_template("login.html")

# ---------- SIGN UP ----------
@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        session['user'] = name

        print("name:",name)
        print("email:",email)
        print("password:",password)

        return redirect(url_for("home"))
    
    return render_template("signup.html")

# ---------- main  ----------
@app.route("/home",methods =["POST","GET"])
def home():
    # if request.method=="POST":
    #     return redirect(url_for("kundali"))
    
    user = session.get('user')
    return render_template("home.html",name = user)


@app.route("/kundali",methods =["POST","GET"])
def kundali():
    if request.method=="POST":
        dob = request.form.get("dob")
        time = request.form.get("time")
        place = request.form.get("place")


        print (dob)
        print(time)
        print(place)
        return redirect(
            url_for("show_kundali", dob=dob, time=time, place=place)
        )
    return render_template("home.html")


@app.route("/show_kundali")
def show_kundali():
    dob = request.args.get("dob")
    time = request.args.get("time")
    place = request.args.get("place")
    result = get_output(dob,time,place) 
    grid, driver, conductor = loshu_grid_from_dob(dob)
    show_grid = any(grid.values())


    

    
    cleaned = result.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        kundali = json.loads(cleaned)
    except Exception as e:
        print("JSON ERROR:", e)
        print("RAW OUTPUT:", result)
        kundali = {"Error": "Invalid response from AI"}
    return render_template(
        "show_kundali.html",
        dob=dob,
        time=time,
        place=place,
        output=result,
        grid=grid,
        driver=driver,
        conductor=conductor,
        show_grid=show_grid ,
        kundali=kundali 
    )



# ---------- GOOGLE LOGIN ----------
@app.route("/login/google")
def google_login():
    return render_template("google_login.html")

# ---------- OTP LOGIN ----------
@app.route("/login/otp")
def otp_login():
    return render_template("otp_login.html")








# ---------- FORGOT PASSWORD ----------
@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")




if __name__ == "__main__":
    app.run(debug=True)
