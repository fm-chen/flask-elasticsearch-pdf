"""Form object declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FileField, TextAreaField, SubmitField, SelectField, StringField, MultipleFileField
from wtforms.validators import DataRequired, Length, InputRequired, EqualTo


class UploadForm(FlaskForm):
    """Contact form."""
    options = SelectField(u'File Type',
                          choices=[('pdf', 'Upload a PDF file'),
                                   ('excel', 'Upload a EXCEL file'),
                                   ('others', 'Upload a general file')],
                          validators=[InputRequired()])
    files = MultipleFileField(
        'File(s) Upload',
        [DataRequired()]
    )
    desc = TextAreaField(
        'Description',
        [
            DataRequired(),
            Length(min=10,
                   message='Your description is too short.')
        ]
    )

    thrust = SelectField(u'Thrust',
                          choices=[('0', 'THRUST 1'),
                                   ('1', 'THRUST 2'),
                                   ('2', 'THRUST 3'),
                                   ('3', 'ANY THRUST')],
                          validators=[InputRequired()])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    options = SelectField(u'Search Options',
                          choices=[('basic', 'Search ALL by filename and description'),
                                   ('opt1', 'Search PDF by content'),
                                   ('opt2', 'Search CSV by column names'),
                                   #('opt3', 'Search Solr Test')
                                   ],
                          validators=[InputRequired()])
    search = StringField('Enter search term(s)')

class LoginForm(FlaskForm):
    username = TextAreaField(
        'Username',
        [
            DataRequired()
        ]
    )

    password = TextAreaField(
        'Password',
        [
            DataRequired()
        ]
    )

class addLoginForm(FlaskForm):
    username = TextAreaField(
        'Username',
        [
            DataRequired(),
            Length(min=8,
                   message='Your username is too short.')
        ]
    )

    password = TextAreaField(
        'Password',
        [
            DataRequired(),
            Length(min=8,
                   message='Your password is too short.')
        ]
    )

    confirmPassword = TextAreaField(
        'Confirm Password',
        [
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )