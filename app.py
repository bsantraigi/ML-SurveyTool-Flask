from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Show a basic html with a header and a link to /survey
    return render_template('index.html')

@app.route('/survey')
def survey():
    # Show a form to fill out
    return render_template('survey.html')


app.run(debug=True, host='0.0.0.0', port=20013)
