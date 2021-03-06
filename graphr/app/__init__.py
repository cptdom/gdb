''' main app routes '''
from flask import Flask
from flask import render_template, request, session, redirect, url_for, flash
from .neo import Neo_client
from .forms import NewDeptForm, NewEmployeeForm, NewProjectForm
from wtforms import Form, StringField, validators, TextAreaField, SelectField


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# max age of the cached static files in seconds
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60
app.static_folder = './static'
app.secret_key = 'dumb_secret_key'

NAVBAR_ITEMS = ['employees', 'departments', 'projects', 'structure']

Neo = Neo_client()


@app.context_processor
def inject_routes():
    """
    Registers the routes for the navbar into the app context
    This is needed because the parent template does not have
    its own route and can't be passed arguments
    """
    links = [(item, item.capitalize()) for item in NAVBAR_ITEMS]
    return(dict(links=links))


@app.route("/")
def home():
    ''' 
    this will be an initial overview 
    once it gets designed
    '''

    return render_template('home.html')


##### EMPLOYEES

@app.route('/employees', methods=['POST', 'GET'])
def employees():
    page_data = {}
    page_data['table_header'] = ['name','department','position']
    page_data['employees'] = Neo.get_all_employees()

    return render_template('employees.html', page_data=page_data)


@app.route('/employees/add', methods=['POST', 'GET'])
def new_employee():
    choices = [dept['name'] for dept in Neo.get_all_depts()]

    form = NewEmployeeForm(request.form)
    form.department.choices = choices
    if request.method == 'POST' and form.validate():
        employee = {
            'name': form.name.data,
            'surname': form.surname.data,
            'department': form.department.data,
            'position': form.position.data,
            'skills': form.skills.data,
            'note': form.note.data
        }
        r = Neo.add_employee(employee)
        if not r:
            flash('An unexpected error occured while processing your request', 'error')
        else:
            flash('Employee successfully added', 'success')
            return redirect('/employees')

    return render_template('new_employee.html', form=form)


@app.route('/employees/<string:id>/edit', methods=['POST', 'GET'])
def edit_employee(id):
    dept_choices = [dept['name'] for dept in Neo.get_all_depts()]
    proj_choices = [proj['name'] for proj in Neo.get_all_projects()]
    initial_values = Neo.get_employee(id)
    #initial values hack
    class F(Form):
        pass
    
    F.surname = StringField('surname', [validators.length(min=3, max=20), validators.DataRequired()], default=initial_values['surname'])
    F.name = StringField('name', [validators.length(min=3, max=20), validators.DataRequired()], default=initial_values['name'])
    F.department = SelectField('department', validate_choice=False, choices=dept_choices, default=initial_values['department'])
    F.position = StringField('position', [validators.length(min=3, max=20), validators.DataRequired()], default=initial_values['position'])
    F.skills = StringField('skills', [validators.length(min=3, max=30), validators.DataRequired()], default=initial_values['skills'])
    F.project = SelectField('project', validate_choice=False, choices=proj_choices, default=initial_values['project'])
    F.note = TextAreaField('note', render_kw={'class': 'form-control', 'rows': 5, 'columns': 50}, default=initial_values['note'])

    form = F(request.form)
    if request.method == 'POST' and form.validate():
        employee = {
            'name': form.name.data,
            'surname': form.surname.data,
            'department': form.department.data,
            'position': form.position.data,
            'skills': form.skills.data,
            'note': form.note.data,
            'project': form.project.data,
        }
        r = Neo.edit_employee(id=id, employee=employee)
        if not r:
            flash('An unexpected error occured while processing your request', 'error')
        else:
            flash('Employee successfully added', 'success')
            return redirect('/employees')

    return render_template('edit_employee.html', form=form)
    pass


@app.route('/employees/<string:id>/delete', methods=['POST', 'GET'])
def delete_employee(id):
    ''' employee delete '''
    if request.method == 'POST':
        if Neo.delete_employee(id):
            flash(f'Successfully deleted employee ID #{id}','success')
            return redirect('/employees')

        flash('An unexpected error occured while processing your request', 'error')
        return


@app.route('/employees/<string:id>', methods=['POST', 'GET'])
def employee_detail(id):
    page_data = {}
    page_data['order'] = ['id','surname','name','department','assigned','position','started','skills','note','project']
    page_data['employee'] = Neo.get_employee(id)
    if not page_data:
        flash('An unexpected error occured while processing your request', 'error')
    
    return render_template('employee[id].html', page_data=page_data)


##### DEPARTMENTS

@app.route('/departments', methods=['POST', 'GET'])
def departments():
    page_data = {}
    page_data['table_header'] = ['name','description','Chief officer']
    page_data['depts'] = Neo.get_all_depts()

    return render_template('departments.html', page_data=page_data)


@app.route('/departments/new', methods=['POST', "GET"])
def new_dept():
    ''' department creation '''

    form = NewDeptForm(request.form)
    if request.method == 'POST' and form.validate():
        dept = {
            'name': form.name.data.replace(' ','').capitalize(),
            'description': form.description.data,
        }
        #name is used as identifier, watch out
        r = Neo.create_dept(dept)
        if not r:
            flash('An unexpected error occured while processing your request', 'error')
        else:
            flash('Department successfully added', 'success')
            return redirect('/departments')

    return render_template('new_dept.html', form=form)


@app.route('/departments/<string:name>', methods=['GET'])
def dept_detail(name):
    ''' dept detail '''

    page_data = {}
    page_data['employees_header'] = ['name','position']
    page_data['projects_header'] = ['id', 'name']
    page_data['employees'] = [employee for employee in Neo.get_all_employees() if employee['department']==name]
    page_data['dept'] = Neo.get_dept(name)
    if not page_data:
        flash('An unexpected error occured while processing your request', 'error')
    
    return render_template('dept[name].html', page_data=page_data)


@app.route('/departments/<string:name>/edit', methods=['GET','POST'])
def edit_dept(name):
    ''' dept edit '''

    #initial values hack
    class F(Form):
        pass

    initial_values = Neo.get_dept(name)
    if not initial_values:
        flash('An unexpected error occured while processing your request', 'error')

    F.name = StringField('surname', [validators.length(min=2, max=20), validators.DataRequired()], default=initial_values['name'],
                render_kw={'disabled': True})
    F.description = TextAreaField('description', [validators.length(min=10, max=160), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50}, default=initial_values['description'])
    
    form = F(request.form)
    if request.method == 'POST' and form.validate():
        dept = {
            'name': form.name.data,
            'description': form.description.data,
        }
        if not Neo.edit_dept(dept, initial_values['name']):
            flash('An unexpected error occured while processing your request', 'error')
            return

        flash('Edit successful', 'success')

        return redirect(f'/departments/{name}')

    return render_template('edit_dept.html', form=form)


@app.route('/departments/<string:name>/delete', methods=['POST'])
def delete_dept(name):
    ''' dept delete '''
    if request.method == 'POST':
        if Neo.delete_dept(name):
            flash(f'Successfully deleted department {name}', 'success')

            return redirect('/departments')

        flash('An unexpected error occured while processing your request', 'error')
        return


##### STRUCTURE

@app.route('/structure', methods=['POST', 'GET'])
def structure():
    '''
    very basic structure overview
    '''

    data = Neo.get_aggregates()
    data['saldo'] = data['newbies'] - data['terminated']
    
    return render_template('structure.html', page_data=data)


##### PROJECTS

@app.route('/projects', methods=['POST', 'GET'])
def projects():
    page_data = {}
    page_data['table_header'] = ['id','name','assigned']
    page_data['projects'] =  Neo.get_all_projects()

    return render_template('projects.html', page_data=page_data)


@app.route('/projects/new', methods=['POST', "GET"])
def new_project():
    ''' project creation '''


    choices = [dept['name'] for dept in Neo.get_all_depts()]

    form = NewProjectForm(request.form)
    form.department.choices = choices
    if request.method == 'POST' and form.validate():
        dept = {
            'name': form.name.data.replace(' ','').capitalize(),
            'client': form.client.data.replace(' ','').capitalize(),
            'department': form.department.data,
            'description': form.description.data,
        }
        r = Neo.create_project(dept)
        if not r:
            flash('An unexpected error occured while processing your request', 'error')
        else:
            flash('Department successfully added', 'success')
            return redirect('/projects')

    return render_template('new_project.html', form=form)


@app.route('/projects/<string:id>', methods=['GET'])
def project_detail(id):
    ''' dept detail '''

    page_data = {}
    page_data['employees_header'] = ['name','position']
    page_data['employees'] = [employee for employee in Neo.get_all_employees() if employee['project_id']==id]
    page_data['project'] = Neo.get_project(id)
    if not page_data:
        flash('An unexpected error occured while processing your request', 'error')
    
    return render_template('proj[id].html', page_data=page_data)


@app.route('/projects/<string:id>/delete', methods=['POST'])
def delete_project(id):
    ''' project delete '''
    if request.method == 'POST':
        if Neo.delete_project(id):
            flash(f'Successfully deleted project {id}', 'success')

            return redirect('/projects')

        flash('An unexpected error occured while processing your request', 'error')
        return