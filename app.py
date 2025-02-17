from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import subprocess
import git
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if the user isn't logged in

# User model (for authentication)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Developer profile model
class DeveloperProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(200), nullable=False)
    preferred_language = db.Column(db.String(50), nullable=False)
    learning_style = db.Column(db.String(50), nullable=False)

# Developer Profile form (for creating a profile)
class DeveloperProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    skills = StringField('Skills', validators=[DataRequired()])
    preferred_language = StringField('Preferred Language', validators=[DataRequired()])
    learning_style = StringField('Learning Style', validators=[DataRequired()])

# Create tables in the database (only once, before you start the app)
with app.app_context():
    db.create_all()

# User loader function (for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return 'Welcome to the Developer Onboarding App!'

# Profile creation route (with form)
@app.route('/profile', methods=['GET', 'POST'])
def create_profile():
    form = DeveloperProfileForm()
    if form.validate_on_submit():
        new_profile = DeveloperProfile(
            name=form.name.data,
            skills=form.skills.data,
            preferred_language=form.preferred_language.data,
            learning_style=form.learning_style.data
        )
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for('profile'))  # Redirect to profile page after creation
    return render_template('profile_form.html', form=form)

# Profile list route
@app.route('/profile')
@login_required  # Protect the route to be accessed by logged-in users only
def profile():
    profiles = DeveloperProfile.query.all()
    return render_template('profile_list.html', profiles=profiles)

# Code analysis function (using pylint)
def analyze_code(code):
    with open("temp_code.py", "w") as f:
        f.write(code)
    
    # Run Pylint to analyze the code
    result = subprocess.run(['pylint', 'temp_code.py'], capture_output=True, text=True)

    # Return the pylint output (warnings, suggestions)
    return result.stdout

# Submit code for analysis route
@app.route('/submit_code', methods=['POST'])
def submit_code():
    if request.method == 'POST':
        code = request.form['code']
        feedback = analyze_code(code)
        return render_template('feedback.html', feedback=feedback)

# Recommend learning path based on preferred language
def recommend_learning_path(preferred_language):
    resources = {
        'Python': ['Learn Python Basics', 'Advanced Python Programming'],
        'JavaScript': ['JavaScript for Beginners', 'Advanced JavaScript Techniques'],
        'Java': ['Introduction to Java', 'Advanced Java for Web Development']
    }

    return resources.get(preferred_language, ['General Programming Resources'])

# Learning path route
@app.route('/learning_path', methods=['POST'])
def learning_path():
    preferred_language = request.form['preferred_language']
    learning_path = recommend_learning_path(preferred_language)
    return render_template('learning_path.html', learning_path=learning_path)

# Clone repository function
def clone_repository(repo_url, clone_path):
    try:
        repo = git.Repo.clone_from(repo_url, clone_path)
        return f"Successfully cloned repo: {repo_url}"
    except Exception as e:
        return f"Error: {str(e)}"

# Clone repository route
@app.route('/clone_repo', methods=['POST'])
def clone_repo():
    repo_url = request.form['repo_url']
    clone_path = './dev_repo'
    result = clone_repository(repo_url, clone_path)
    return f"Cloning Result: {result}"

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Continue with saving the user to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login page after successful registration
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        # If user exists and password is correct, log the user in
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))  # Redirect to profile page after successful login

        return 'Login Failed. Check your credentials and try again.'

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required  # Protect the route so only logged-in users can log out
def logout():
    logout_user()  # Logout the user
    return redirect(url_for('login'))  # Redirect to login page after logout

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
