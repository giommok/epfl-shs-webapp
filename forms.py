from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, validators


class QuizForm(FlaskForm):
    question = RadioField('choice', [validators.Required()])
    submit = SubmitField('Submit')


class NameForm(FlaskForm):
    name = StringField('Team name', validators=[validators.DataRequired()])
    submit = SubmitField('Play')
