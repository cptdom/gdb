''' forms using WTForms '''
from wtforms import Form, StringField, validators, TextAreaField

class NewDeptForm(Form):

    name = StringField('name', [validators.length(min=3, max=20), validators.DataRequired()])
    description = TextAreaField('description', [validators.length(min=10, max=160), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50})


class NewEmployeeForm(Form):

    surname=StringField('surname', [validators.length(min=3, max=20), validators.DataRequired()])
    name=StringField('name', [validators.length(min=3, max=20), validators.DataRequired()])
    position=StringField('position', [validators.length(min=3, max=20), validators.DataRequired()])
    skills=StringField('skills', [validators.length(min=3, max=30), validators.DataRequired()])
    note=TextAreaField('note', [validators.length(min=10, max=150), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50})

