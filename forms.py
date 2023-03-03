from flask_wtf import FlaskForm
from flask import Markup
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, InputRequired 

class SurveyForm(FlaskForm):
    eng_label = Markup('<strong>Engagingness:</strong> Given the context, is the model-generated response <em>engaging</em>?')
    rel_label = Markup('<strong>Relevance:</strong> Given the context, is the model-generated response <em>relevant</em>?')
    flu_label = Markup('<strong>Fluency:</strong> Given the context, is the model-generated response <em>fluent</em>?')
    coh_label = Markup('<strong>Coherence:</strong> Given the context, is the model-generated response <em>coherent</em>?')
    q1 = RadioField(eng_label, 
                    choices=[(0, 'No'), (1, 'Somewhat'), (2, 'Yes')], 
                    description="Engaging: The response can be followed-up on by the user.", 
                    validators=[DataRequired()])

    q2 = SelectField(rel_label, 
                     choices=[(0, 'No'), (1, 'Somewhat'), (2, 'Yes')], 
                     description='Relevant: Response is on topic and a valid/reasonable continuation of the conversation.', 
                     validators=[DataRequired()])
    q3 = SelectField(flu_label, 
                     choices=[(0, 'No'), (1, 'Somewhat'), (2, 'Yes')], 
                     description='Fluent: Response follows all the rules of English grammar.', 
                     validators=[DataRequired()])

    q4 = SelectField(coh_label, 
                     choices=[(0, 'No'), (1, 'Somewhat'), (2, 'Yes')], 
                     description='Coherent: The response is logically connected and easy to understand in the context of the conversation. It presents a clear and organized train of thought.', 
                     validators=[DataRequired()])
    submit = SubmitField('Submit')

