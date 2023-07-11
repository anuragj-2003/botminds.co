import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.csrf import CSRFProtect
from flask import session
from wtforms import StringField, PasswordField
import re
import smtplib
import random
import string
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify
from werkzeug.security import generate_password_hash
import time
from datetime import datetime
import platform
import pandas as pd
from flask_cors import CORS
import ast
import wikipedia

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config["WTF_CSRF_SECRET_KEY"] = os.urandom(24)
SECRET_KEY = os.urandom(24)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "MYSQL_PASSWORD"
app.config["MYSQL_DB"] = "DATABASE_NAME"

mysql = MySQL(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RegistrationForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired()])
    email = StringField("Email", [validators.Email(), validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])


class VerifyOTPForm(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired(message="Please enter the OTP.")])
    submit = SubmitField("Verify OTP")


class LoginForm(FlaskForm):
    email = StringField(
        "email",
        [validators.DataRequired(), validators.Email()],
        render_kw={
            "placeholder": "Enter Email-ID",
            "style": "text-align:center;",
            "autofocus": True,
            "type": "email",
        },
    )
    password = PasswordField(
        "password",
        [validators.DataRequired()],
        render_kw={"placeholder": "Enter Password", "style": "text-align:center;"},
    )

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

class OtpForm(FlaskForm):
    otp = StringField("otp", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("submit")


class ChangePasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    user_id = StringField("User ID", validators=[DataRequired()])
    user_pass1 = PasswordField("New Password", validators=[DataRequired()])
    user_pass2 = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("user_pass1")]
    )
    submit = SubmitField("Change Password")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        session["name"] = name
        session["password"] = password

        otp = random.randint(1000, 9999)

        sender_email = "business@example.com"
        sender_password = "ACCOUNT_PASSWORD"
        receiver_email = email

        message = MIMEMultipart("alternative")
        message["Subject"] = "Registration Confirmation"
        message["From"] = sender_email
        message["To"] = receiver_email

        welcome_message = "<b>Welcome to BotMinds!</b>"
        confirmation_message = "Please enter the otp to Register."
        otp_message = f"Your OTP is: {otp}"
        message_with_welcome = (
            f"{welcome_message}<br/><br/>{confirmation_message}<br/>{otp_message}"
        )

        message.attach(MIMEText(message_with_welcome, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()

        session["email"] = email
        session["otp"] = otp
        time.sleep(2)
        return redirect(url_for("verify_otp"))

    return render_template("register.html", form=form)


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    form = VerifyOTPForm()
    if request.method == "POST" and form.validate_on_submit():
        entered_otp = form.otp.data
        email = session.get("email")
        session_otp = session.get("otp")

        if str(entered_otp) == str(session_otp):
            name = session.get("name")
            password = session.get("password")

            try:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO userTable (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password),
                )
                mysql.connection.commit()
                cursor.close()
                session.pop("email", None)
                session.pop("otp", None)
                session.pop("name", None)
                session.pop("password", None)
                time.sleep(3)
                return redirect(url_for("login"))
            except Exception as e:
                logging.error(f"Error inserting data into userTable: {e}")
                mysql.connection.rollback()
                cursor.close()
                flash("An error occurred during registration.", "error")
                return redirect(url_for("verify_otp"))
        else:
            flash("Invalid OTP! Please try again.", "error")
            return redirect(url_for("verify_otp"))

    otp = session.get("otp")

    return render_template("verifyOtp.html", form=form, otp=otp)


def send_alert_on_login(email):
    sender_email = "business@example.com"
    sender_password = "ACCOUNT_PASSWORD"
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Login Notification"
    message["From"] = sender_email
    message["To"] = receiver_email

    confirmation_message = "Your account has been logged in to BotMinds."
    logged_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_info = f"Logged-in Device: {platform.node()} ({platform.system()} {platform.release()})"
    message_with_alert = f"""
        <html>
            <head></head>
            <body>
                <h1 style="color: red;">Alert!</h1>
                <p>{confirmation_message}</p>
                <p>Logged-in Time: {logged_in_time}</p>
                <p>{device_info}</p>
            </body>
        </html>
    """

    message.attach(MIMEText(message_with_alert, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = form.password.data
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM userTable WHERE email = %s", [email])
        if result > 0:
            data = cur.fetchone()
            stored_password = data[3]
            if password == stored_password:
                session["user_id"] = data[0]
                session["user_email"] = data[1]
                session["logged_in"] = True
                send_alert_on_login(email)
                time.sleep(1)
                return redirect(url_for("chat"))
            else:
                return render_template(
                    "login.html", form=form, error="Incorrect email or password"
                )
        else:
            error = "User with email {} not registered.".format(email)
            return render_template("login.html", form=form, error=error)
    return render_template("login.html", form=form)


@app.route("/chat")
def chat():
    if "user_id" not in session or not session["logged_in"]:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, avatar FROM userTable WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    name = user_data[0]
    avatar_value = user_data[1]
    cur.close()

    image_names = [
        "avatar-m1.png",
        "avatar-m2.png",
        "avatar-m3.png",
        "avatar-m4.png",
        "avatar-m5.png",
        "avatar-f1.png",
        "avatar-f2.png",
        "avatar-f3.png",
        "avatar-f4.png",
        "avatar-f5.png",
    ]

    if (
        avatar_value is not None
        and avatar_value.isdigit()
        and 1 <= int(avatar_value) <= 10
    ):
        avatar_value = int(avatar_value)
        image_name = image_names[avatar_value - 1]
        image_path = url_for("static", filename=f"images/{image_name}")
    else:
        image_path = None

    return render_template("home.html", name=name, image_path=image_path)



data = pd.read_csv("newdataset.csv")
print(data.head())

@app.route('/response', methods=['POST'])
def bot_response():
    global tag
    user_input = request.form['user_input']
    tag_matches = data[data['patterns'].apply(lambda x: isinstance(x, str) and user_input.lower() in x.lower())]
    if not tag_matches.empty:
        tag = tag_matches.iloc[0]['tag']
        responses = tag_matches.iloc[0]['responses']
        responses = ast.literal_eval(responses)
        response = random.choice(responses)
        if isinstance(response, list):
            response = random.choice(response)
        return jsonify({'response': response})
    else:
        return jsonify({'response': "I'm sorry, I don't have a response for that."})







@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if "user_id" not in session or not session["logged_in"]:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    if request.method == "POST":
        name = request.form.get("user_name")
        avatar_value = request.form.get("avatar_value")

        if avatar_value is not None and avatar_value != "":
            avatar_value = int(avatar_value)
            cur.execute(
                "UPDATE userTable SET name = %s, avatar = %s WHERE id = %s",
                (name, avatar_value, user_id),
            )
        else:
            cur.execute("UPDATE userTable SET name = %s WHERE id = %s", (name, user_id))

        mysql.connection.commit()

    cur.execute("SELECT name, avatar FROM userTable WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    name = user_data[0]
    avatar_value = user_data[1]

    if avatar_value is not None:
        avatar_value = int(avatar_value)
    else:
        avatar_value = 0

    cur.close()

    image_names = [
        "avatar-m1.png",
        "avatar-m2.png",
        "avatar-m3.png",
        "avatar-m4.png",
        "avatar-m5.png",
        "avatar-f1.png",
        "avatar-f2.png",
        "avatar-f3.png",
        "avatar-f4.png",
        "avatar-f5.png",
    ]

    if 1 <= avatar_value <= 10:
        image_name = image_names[avatar_value - 1]
        image_path = url_for("static", filename=f"images/{image_name}")
    else:
        image_path = None

    return render_template(
        "profile.html", name=name, image_path=image_path, avatar_value=avatar_value
    )


@app.route("/validate_password_page")
def validate_password_page():
    return render_template("validate_password.html")


@app.route("/validate_password", methods=["POST"])
def validate_password():
    entered_password = request.form.get("user_pass1", "")

    cur = mysql.connection.cursor()
    user_id = session.get("user_id")
    if user_id:
        cur.execute("SELECT password FROM userTable WHERE id = %s", (user_id,))
        stored_password = cur.fetchone()
        if stored_password and entered_password == stored_password[0]:
            return redirect(url_for("change_email"))
        else:
            error_message = "Incorrect password"
            return render_template("validate_password.html", error=error_message)

    else:
        return render_template("not_logged_in.html")


@app.route("/change_password_profile", methods=["GET", "POST"])
def change_password1():
    return render_template("change_password_profile.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM userTable WHERE email = %s", [email])
        result = cur.fetchone()

        if result is None:
            error = "Email does not exist."
            return render_template("forgot_password.html", form=form, error=error)

        otp = random.randint(1000, 9999)
        session["email"] = email
        session["otp"] = otp
        user_id = result[0]
        session["user_id"] = user_id
        sender_email = "business@example.com"
        sender_password = "ACCOUNT_PASSWORD"
        receiver_email = email

        message = MIMEText(f"Your OTP is {otp}.")
        message["Subject"] = "OTP for password reset"   
        message["From"] = sender_email
        message["To"] = receiver_email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            return render_template("otp.html", email=email)
        except Exception as e:
            print(f"Error: {e}")
            return render_template("otp.html", form=form, user_id=user_id, email=email)
    else:
        return render_template("forgot_password.html", form=form)


@app.route("/otp", methods=["POST"])
def otp():
    form = OtpForm()
    email = session.get("email")
    user_id = session.get("user_id")
    password = form.password.data

    try:
        user_otp = request.form["otp"]
    except KeyError:
        error_message = "Invalid OTP, please try again."
        return render_template(
            "otp.html",
            form=form,
            email=email,
            password=password,
            error=error_message,
            user_id=user_id,
        )

    actual_otp = str(session.get("otp"))
    if user_otp == actual_otp:
        return render_template("change_password.html", email=email, user_id=user_id)

    error_message = "Invalid OTP, please try again."
    return render_template(
        "otp.html",
        form=form,
        email=email,
        password=password,
        error=error_message,
        user_id=user_id,
    )


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = request.form.get("email")
        user_id = request.form.get("user_id")
        user_pass1 = request.form.get("user_pass1")
        user_pass2 = request.form.get("user_pass2")

        form = ChangePasswordForm(request.form)
        if form.validate():
            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE userTable SET password = %s WHERE email = %s",
                (user_pass1, email),
            )
            mysql.connection.commit()
            cursor.close()

            flash("Password changed successfully!", "success")
            time.sleep(3)
            return redirect(url_for("login"))

    else:
        email = request.args.get("email")
        user_id = request.args.get("user_id")
        form = ChangePasswordForm()

    return render_template(
        "change_password.html", email=email, user_id=user_id, form=form
    )


@app.route("/change_email", methods=["GET", "POST"])
def change_email():
    if request.method == "POST":
        new_email = request.form.get("email")
        user_id = session.get("user_id")
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "UPDATE userTable SET email = %s WHERE id = %s", (new_email, user_id)
            )
            mysql.connection.commit()
            flash("Email updated successfully", "success")
            time.sleep(3)
            return redirect(url_for("profile"))
        except Exception as e:
            flash(f"Error updating email: {str(e)}", "error")
        finally:
            cursor.close()

    return render_template("change_email.html")


@app.route("/not_logged_in")
def not_logged_in():
    return render_template("not_logged_in.html")


@app.route("/seeking_password")
def seeking_password():
    return render_template("validate_password_profile.html")


@app.route("/checking_password", methods=["POST"])
def checking_password():
    entered_password = request.form.get("user_pass1", "")

    cur = mysql.connection.cursor()
    user_id = session.get("user_id")
    if user_id:
        cur.execute("SELECT password FROM userTable WHERE id = %s", (user_id,))
        stored_password = cur.fetchone()
        if stored_password and entered_password == stored_password[0]:
            return redirect(url_for("update_password"))
        else:
            error_message = "Incorrect password"
            return render_template(
                "validate_password_profile.html", error=error_message
            )
    else:
        return render_template("not_logged_in.html")


@app.route("/update_password", methods=["GET", "POST"])
def update_password():
    if request.method == "POST":
        user_pass1 = request.form.get("user_pass1")
        user_id = session.get("user_id")
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE userTable SET password = %s WHERE id = %s", (user_pass1, user_id)
        )
        mysql.connection.commit()
        cursor.close()
        time.sleep(3)
        return redirect(url_for("profile"))

    return render_template("change_password_profile.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_email", None)
    session["logged_in"] = False
    time.sleep(3)
    return redirect(url_for("login"))


def send_alert_on_delete_account(email):
    sender_email = "business@example.com"
    sender_password = "ACCOUNT_PASSWORD"
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Account Deleted"
    message["From"] = sender_email
    message["To"] = receiver_email

    email_body = """
        <html>
            <head></head>
            <body>
                <h1>Your account has been deleted.</h1>
                <p>We're sorry to see you go!</p>
            </body>
        </html>
    """

    message.attach(MIMEText(email_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


@app.route("/delete_account")
def delete_account():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM userTable WHERE id = %s", (user_id,))
    data = cur.fetchone()
    if data is None:
        return redirect(url_for("login"))

    email = data[0]
    cur.execute("DELETE FROM userTable WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    send_alert_on_delete_account(email)

    time.sleep(1)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False)