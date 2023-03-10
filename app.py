from datetime import datetime
import random
import json
from flask import request, flash, redirect, url_for
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from forms import SurveyForm, LoginForm
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c60ab121a433e814649e0640e73c1f2f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    prolific_pid = db.Column(db.String(20), unique=True, nullable=False)
    ref_url = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submissions = db.relationship('Submission', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.prolific_pid}', '{self.ref_url}')"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Main fields from our dataset
    sample_id = db.Column(db.Integer, nullable=False)
    context = db.Column(db.JSON, nullable=False)
    response_a = db.Column(db.Text, nullable=False)
    response_b = db.Column(db.Text, nullable=False)
    response_a_src = db.Column(db.String(100), nullable=False)
    response_b_src = db.Column(db.String(100), nullable=False)
    # To track question versions
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False)
    submissions = db.relationship('Submission', backref='question', lazy=True)

    def __repr__(self):
        return f"Question('sid:{self.sample_id}', '{self.response_a_src}' vs. '{self.response_b_src}', '{self.date_added}', active:'{self.is_active}')"


class Submission(db.Model):
    """
    This table will store the submissions from the survey. One row corresponds to each question
    submitted by an user.
    """
    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submission_json = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    is_submitted = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Submissions('{self.user_id}', '{self.question_id}', '{self.response}', '{self.date_added}')"


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    # Check if there's any get parameters
    if request.args:
        print(request.args)
        prolific_pid = request.args.get('PROLIFIC_PID')
        session_id = request.args.get('SESSION_ID')
        study_id = request.args.get('STUDY_ID')
        url_args = {
            'PROLIFIC_PID': prolific_pid,
            'SESSION_ID': session_id,
            'STUDY_ID': study_id
        }
    else:
        url_args = {}

    login_form = LoginForm()
    if login_form.validate_on_submit():
        # Create user if it doesn't exist
        user = User.query.filter_by(prolific_pid=login_form.prolific_pid.data).first()
        if user is None:
            user = User(prolific_pid=login_form.prolific_pid.data, ref_url="test")
            db.session.add(user)
            db.session.commit()
            # Create entries for submissions
            questions = Question.query.filter_by(is_active=True).all()
            for q in questions:
                submission = Submission(user_id=user.id, question_id=q.id, submission_json={}, is_submitted=False)
                db.session.add(submission)
            db.session.commit()
            flash(f'Account created for {login_form.prolific_pid.data}!', 'success')
        else:
            flash(f'Logging in with existing account for {login_form.prolific_pid.data}!', 'success')
        login_user(user, remember=login_form.remember_me.data)
        return redirect(url_for('dashboard'))

    # Show a basic html with a header and a link to /survey
    return render_template('login.html', title="Login", login_form=login_form, url_args=url_args)


@app.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # User info and submissions
    user = User.query.filter_by(prolific_pid=current_user.prolific_pid).first()
    user_info = {
        'prolific_pid': user.prolific_pid,
        'ref_url': user.ref_url,
        'date_added': user.date_added
    }
    # Submission progress
    submissions = Submission.query.filter_by(user_id=user.id).all()
    submission_progress = {
        'total': len(submissions),
        'submitted': len([s for s in submissions if s.is_submitted])
    }

    # Show a basic html with a header and a link to /survey
    return render_template('dashboard.html', title="Dashboard", user_info=user_info, submission_progress=submission_progress)


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Show a form with the fields from SurveyForm
    form = SurveyForm()
    questions = Question.query.filter_by(is_active=True).all()
    question = questions[random.randint(0, len(questions)-1)]
    print("Context: ")
    print(question.context)
    question.context = json.loads(question.context)
    return render_template('survey.html', title='Survey', form=form, question=question)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=20013)
