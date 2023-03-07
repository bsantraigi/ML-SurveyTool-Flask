from datetime import datetime
import random
import json
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from forms import SurveyForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c60ab121a433e814649e0640e73c1f2f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prolific_id = db.Column(db.String(20), unique=True, nullable=False)
    ref_url = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submissions = db.relationship('Submission', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.prolific_id}', '{self.ref_url}')"


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

    def __repr__(self):
        return f"Submissions('{self.user_id}', '{self.question_id}', '{self.response}', '{self.date_added}')"


@app.route('/')
def index():
    # Show a basic html with a header and a link to /survey
    return render_template('home.html', title="Home")

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    # Show a form with the fields from SurveyForm
    form = SurveyForm()
    questions = Question.query.filter_by(is_active=True).all()
    question = questions[random.randint(0, len(questions)-1)]
    question.context = json.loads(question.context)
    return render_template('survey.html', title='Survey', form=form, question=question)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=20013)
