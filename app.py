from flask import Flask
from flask import render_template
from forms import SurveyForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/')
def index():
    # Show a basic html with a header and a link to /survey
    return render_template('home.html', title="Home")

@app.route('/survey')
def survey():
    # Show a form with the fields from SurveyForm
    form = SurveyForm()
    return render_template('survey.html', title='Survey')

app.run(debug=True, host='0.0.0.0', port=20013)
