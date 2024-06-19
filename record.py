from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Create Flask instance
rec = Flask(__name__)
rec.config['SECRET_KEY'] = "mykey"
rec.config['SQLALCHEMY_ECHO'] = True
rec.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users_rec'

# Initialize database and migration
db = SQLAlchemy(rec)
migrate = Migrate(rec, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(rec)
login_manager.login_view = 'signin'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Forms
class SignUpForm(FlaskForm):
    fname = StringField("What is your first name:", validators=[DataRequired()])
    lname = StringField("What is your last name:", validators=[DataRequired()])
    uname = StringField("What is your preferred username:", validators=[DataRequired()])
    email = StringField("What is your email:", validators=[DataRequired(), Email()])
    pass_hash = PasswordField('Enter Password:', validators=[DataRequired(), EqualTo('pass_hash2', message='Passwords must match')])
    pass_hash2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class SignInForm(FlaskForm):
    email = StringField("Enter email:", validators=[DataRequired(), Email()])
    password = PasswordField("Enter password:", validators=[DataRequired()])
    submit = SubmitField("Sign In")

# DB Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(200), nullable=False)
    lname = db.Column(db.String(200), nullable=False)
    uname = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    pass_hash = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Password hashing
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pass_hash, password)

    def __repr__(self):
        return f'<User {self.uname}>'

# Routes and Functions
@rec.route('/home')
def home():
    return render_template("home.html")

@rec.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect('/dash')
        else:
            flash('Invalid email or password.', 'danger')
    return render_template("signin.html", form=form)

@rec.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = Users(
                fname=form.fname.data,
                lname=form.lname.data,
                uname=form.uname.data,
                email=form.email.data,
                password=form.pass_hash.data  # Use password setter
            )
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully.', 'success')
            return redirect('/signin')
        else:
            flash('Email already registered.', 'danger')
    return render_template("signup.html", form=form)

@rec.route('/dash')
@login_required
def dash():
    return render_template("dash.html")

@rec.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = Users.query.get_or_404(id)
    form = SignUpForm()
    if form.validate_on_submit():
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.uname = form.uname.data
        user.email = form.email.data
        if form.pass_hash.data:
            user.password = form.pass_hash.data
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect('/dash')
    elif request.method == 'GET':
        form.fname.data = user.fname
        form.lname.data = user.lname
        form.uname.data = user.uname
        form.email.data = user.email
    return render_template("update.html", form=form, user=user)

@rec.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect('/dash')

@rec.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@rec.route('/settings')
@login_required
def settings():
    return render_template("settings.html")

@rec.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@rec.route('/notifications')
@login_required
def notifications():
    return render_template("notifications.html")

@rec.route('/records')
@login_required
def records():
    return render_template("records.html")

@rec.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Error Handlers
@rec.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@rec.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@rec.after_request 
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Debug
if __name__ == '__main__':
    rec.run(debug=True)
