from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi database MySQL
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="flask_app")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        if user and user[2] == form.password.data:
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    cursor = db.cursor()
    cursor.execute("SELECT nama, nilai FROM grades")
    grades = cursor.fetchall()
    return render_template('home.html', grades=grades)

@app.route('/detail')
@login_required
def detail():
    return render_template('detail.html')

if __name__ == '__main__':
    app.run(debug=True)
