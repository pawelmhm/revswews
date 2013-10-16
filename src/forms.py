from wtforms import *

class ReviewThis(Form):
    title = TextField('Title', [validators.Length(min=4, max=25)])
    content = TextAreaField('Review', [validators.Length(min=6, max=300)])
    rating = SelectField('Rating',choices=[('good','good'), ('bad','bad')])
    request_id = HiddenField('request_id')
    reviewed = HiddenField(label=None)

class Register(Form):
    newUsername = TextField('Username', [validators.Required(),validators.Length(min=4, max=25, message='Your user name is either slightly too short or too long')])
    email = TextField('E-mail', [validators.Length(min=10, max=35, message='Is this really a correct e-mail addres?')])
    newPassword = PasswordField('Password', [validators.Required(), validators.Length(min=8,message="Password must be at least 8 characters"),
                                          validators.EqualTo('confirm', message="passwords must match")])
    confirm  = PasswordField('Repeat password')

class Login(Form):
    username = TextField('Username',[validators.Required()] )
    password = PasswordField('Password', [validators.Required()])


class ReviewRequest(Form):
    title = TextField('Title', [validators.Length(min=4, max=120)])
    content = TextAreaField('Request content', [validators.Length(min=20)])
    category = SelectField('Category', choices=[('academic', 'academic'), ('other', 'other')])
    deadline = TextField('Deadline',[validators.Required()], id="datepicker")
    username = HiddenField(label=None)
    user_id= HiddenField(label=None)

class Profile(Form):
    about_me = TextAreaField('About Me', [validators.Optional()])
    email  = TextField('E-mail', [validators.Optional()])
    password = PasswordField('Password',[validators.Optional()])
    password = PasswordField('Confirm password', [validators.Optional()])
