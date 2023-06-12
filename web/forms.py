"""Form object declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FileField, TextAreaField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, Length, InputRequired


class UploadForm(FlaskForm):
    """Contact form."""
    options = SelectField(u'File Type',
                          choices=[('pdf', 'Upload a PDF file'),
                                   ('excel', 'Upload a EXCEL file'),
                                   ('others', 'Upload a general file')],
                          validators=[InputRequired()])
    file = FileField(
        'Select a file to upload',
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
                                   ('3', 'THRUST 4'),
                                   ('4', 'THRUST 5'),
                                   ('5', 'THRUST 6')],
                          validators=[InputRequired()])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    options = SelectField(u'Search Options',
                          choices=[('basic', 'Search ALL by filename and description'),
                                   ('opt1', 'Search PDF by content'),
                                   ('opt2', 'Search CSV by column names'),
                                   ('opt3', 'Search Solr Test')],
                          validators=[InputRequired()])
    search = StringField('Enter search term(s)')
