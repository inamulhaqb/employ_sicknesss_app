from flask import flash

from flask import Flask, make_response
import pandas as pd
from flask import jsonify
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
from flask import request, redirect, url_for, render_template
from datetime import datetime
from models import db, Employee, SicknessAbsence  # Import db and models
from xhtml2pdf import pisa
import io

app = Flask(__name__)

app.secret_key = '123@ufk'  # Set a unique and secret key
# Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:inam@localhost:5432/hr_employee'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

# go to home page
@app.route("/")
def index():
    return render_template("index.html")

# add_employee page route
@app.route('/go_employee_page')
def go_employee_page():
    return render_template('add_employee.html')

# add_employee page route
@app.route('/employee_details_page')
def employee_details_page():
    return render_template('employee_details.html')

# Route to handle form submission and save data to the database
# @app.route('/submit', methods=['POST'])

# add sick leave page route
@app.route('/add_sick_leave')
def add_sick_leave():
    return render_template('add_sick_leave.html')

# to get employee records from employee tale
@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    employee_list = [{'employee_id': emp.employee_id, 'name': emp.name} for emp in employees]
    return jsonify(employee_list)

# add absent list
@app.route('/add_absence', methods=['POST'])
def add_absence():
    employee_rel = request.form['employee_rel']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    reason = request.form['reason']

    # Create the new SicknessAbsence record
    new_absence = SicknessAbsence(employee_rel=employee_rel, start_date=start_date, end_date=end_date, reason=reason)

    # Save to the database
    db.session.add(new_absence)
    db.session.commit()
    # Flash a success message
    flash(f"leave for {employee_rel} added successfully!", "success")

    # Redirect to the same page (or anywhere you prefer)

    return redirect(url_for('add_absence_form'))

# url to pass add_absence function
@app.route('/add_absence_form', methods=['GET'])
def add_absence_form():
    employees = Employee.query.all()  # Fetch employees for the dropdown
    return render_template('add_sick_leave.html', employees=employees)

# add employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()

    name = data.get('name')
    department = data.get('department')

    print(f"Received data: Name: {name}, Department: {department}")  # Debugging print

    if not name or not department:
        return jsonify({'success': False, 'message': 'Name and Department are required!'}), 400

    # Create a new employee record
    new_employee = Employee(name=name, department=department)

    try:
        db.session.add(new_employee)
        db.session.commit()
        print("Employee added successfully")  # Debugging print
        return jsonify({'success': True, 'message': 'Employee added successfully!'})
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")  # Debugging print
        return jsonify({'success': False, 'message': str(e)})

# To show employee data
@app.route('/show_employee_details', methods=['GET'])
def show_employee_details():
    # Get list of employee IDs from the query parameter
    employee_ids = request.args.get('employee_id')

    if employee_ids:
        # Split the string of IDs and convert to a list of integers
        employee_ids = [int(employee_id) for employee_id in employee_ids.split(',')]
        # Fetch the specified employees
        employees = Employee.query.filter(Employee.employee_id.in_(employee_ids)).all()
    else:
        # If no IDs provided, fetch all employees
        employees = Employee.query.all()

    if not employees:
        return jsonify({'error': 'No employees found'}), 404

    # Prepare the employee data for JSON response
    employee_data_list = []
    for employee in employees:
        employee_data = {
            'name': employee.name,
            'department': employee.department,
            'bradford_factor': employee.calculate_bradford_factor(),
            'absences': [
                {
                    'sickness_absence_id': absence.sickness_absence_id,
                    'start_date': absence.start_date.strftime('%Y-%m-%d'),
                    'end_date': absence.end_date.strftime('%Y-%m-%d'),
                    'reason': absence.reason,
                    'duration_days': absence.duration_days
                }
                for absence in employee.absences
            ]
        }
        employee_data_list.append(employee_data)

    # Return the list of employee data to the template
    return render_template('employee_details.html', employee=employee, employee_data_list=employee_data_list)


# To Generate Pdf Report department wise
@app.route('/generate_report/<department>', methods=['GET'])
def generate_pdf_report(department):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, f"Sickness Absence Report for {department}")

    # Draw a line
    p.setStrokeColorRGB(0, 0, 0)  # Black color for line
    p.setLineWidth(1.5)
    p.line(50, 740, 550, 740)

    # Subtitle
    p.setFont("Helvetica", 14)
    p.drawString(100, 720, "List of Employees who are absent Absences with :")
    p.line(50, 715, 550, 715)  # Underline the subtitle

    # Query for employees with absences in the specified department
    try:
        employees_with_absences = (
            db.session.query(Employee)
            .join(SicknessAbsence, Employee.employee_id == SicknessAbsence.employee_rel)
            .filter(Employee.department == department)
            .distinct()
            .all()
        )
    except Exception as e:
        p.setFont("Helvetica", 10)
        p.drawString(100, 700, f"Error fetching data: {str(e)}")
        p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"{department}_report.pdf", mimetype='application/pdf')

    y_position = 690

    if not employees_with_absences:
        p.setFont("Helvetica", 10)
        p.drawString(100, y_position, "No absences recorded for any employees in this department.")
    else:
        # Iterate through employees with absences
        for employee in employees_with_absences:
            p.setFont("Helvetica-Bold", 12)
            p.setFillColorRGB(0, 0, 1)  # Blue color for employee names
            p.drawString(100, y_position, f"Employee Name: {employee.name}")

            # Calculate Bradford Factor
            bradford_factor = employee.calculate_bradford_factor()
            p.setFont("Helvetica", 10)
            p.setFillColorRGB(0, 0, 0)  # Reset color to black for scores
            p.drawString(120, y_position - 15, f"Bradford Factor Score: {bradford_factor}")

            # Draw a line
            y_position -= 30
            p.setStrokeColorRGB(0.7, 0.7, 0.7)  # Gray color for line
            p.line(100, y_position, 550, y_position)
            y_position -= 10

            # Get absences for this employee
            absences = SicknessAbsence.query.filter_by(employee_rel=employee.employee_id).all()
            p.setFont("Helvetica", 10)

            if not absences:
                p.drawString(120, y_position, "No absences recorded.")
                y_position -= 20  # Space for next employee
                continue

            for absence in absences:
                p.drawString(120, y_position,
                             f"Absence: {absence.reason} from {absence.start_date} to {absence.end_date}")
                y_position -= 15  # Move down for the next line

            # Ensure y_position does not fall below the page bottom
            if y_position < 50:
                p.showPage()  # Create a new page
                y_position = 750  # Reset position for the new page

            y_position -= 20  # Extra space between employees

    # Draw a line at the bottom
    p.setStrokeColorRGB(0, 0, 0)  # Black color for bottom line
    p.line(50, y_position + 10, 550, y_position + 10)

    # Add footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, y_position - 20, "Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{department}_report.pdf", mimetype='application/pdf')

@app.route('/api/departments', methods=['GET'])
def get_departments():
    # Fetch distinct departments from the Employee model
    departments = db.session.query(Employee.department).distinct().all()

    # Convert to a simple list of department names
    department_list = [dept[0] for dept in departments]

    return jsonify(department_list)

# Print report of top 10 employee with the highest brand factor score
@app.route('/report/top-employees-pdf')
def top_employees_pdf():
    # Fetch top 10 employees based on Bradford Factor
    employees = Employee.query.all()
    # Filter out employees with Bradford Factor <= 0
    employees_with_bradford = [emp for emp in employees if emp.calculate_bradford_factor() > 0]

    # Sort employees by Bradford Factor (assuming method calculate_bradford_factor exists)
    sorted_employees = sorted(employees_with_bradford, key=lambda emp: emp.calculate_bradford_factor(), reverse=True)[:10]

    # Render HTML template for the report
    rendered = render_template('top_employees_bradford_factor_report.html', employees=sorted_employees)

    # Convert HTML to PDF
    pdf = convert_html_to_pdf(rendered)

    # Serve the PDF file inline, so it opens in the browser
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=top_employees.pdf'

    return response

# Convert HTML to PDF using xhtml2pdf
def convert_html_to_pdf(source_html):
    output = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(source_html), dest=output)
    # If error occurred during PDF generation, return None
    if pisa_status.err:
        return None
    # Move pointer to start of file and return PDF data
    output.seek(0)
    return output.read()

@app.route('/employee_records')
def employee_records():
    return render_template('employee_records.html')

# print excel reports for top 10 employees
@app.route('/generate_top_10_excel_report')
def generate_top_10_excel_report():
    # Query all employees
    employees = Employee.query.all()
    top_10_data = []

    # Loop through employees and calculate Bradford Factor
    for employee in employees:
        bradford_factor = employee.calculate_bradford_factor()

        # Only include employees with Bradford Factor greater than 0
        # Collecting only those with a Bradford factor greater than 0
        if bradford_factor > 0:
            top_10_data.append({
                'Name': employee.name,
                'Department': employee.department,
                'Bradford Factor': bradford_factor
            })

    # Convert the data to a DataFrame
    df_10 = pd.DataFrame(top_10_data)

    # Sort by Bradford Factor in descending order and limit to top 10
    df_10 = df_10.sort_values(by='Bradford Factor', ascending=False).drop_duplicates(subset=['Name']).head(10)

    # Create a BytesIO object to save the Excel file in memory
    result = BytesIO()

    # Create an Excel writer object using the BytesIO object
    with pd.ExcelWriter(result, engine='openpyxl') as writer:
        df_10.to_excel(writer, index=False, sheet_name='Top 10 Employees')

    # Save the file and reset the buffer position
    result.seek(0)

    # Return the file as a response
    return send_file(result, as_attachment=True, download_name='top10_bradford_factor_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# multiple date and reason
# @app.route('/generate_excel_report')
# def generate_excel_report():
#     # Query all employees
#     employees = Employee.query.all()
#     employee_data = []
#
#     # Loop through employees and calculate Bradford Factor
#     for employee in employees:
#         bradford_factor = employee.calculate_bradford_factor()
#
#         # Only include employees with Bradford Factor greater than 0
#         if bradford_factor > 0:
#             # Append employee and their Bradford Factor to a list
#             employee_data.append({
#                 'employee': employee,
#                 'bradford_factor': bradford_factor
#             })
#
#     # Sort employees by Bradford Factor in descending order and limit to top 10
#     top_employees = sorted(employee_data, key=lambda x: x['bradford_factor'], reverse=True)[:10]
#
#     data = []
#     # Loop through the top 10 employees and gather their absences
#     for item in top_employees:
#         employee = item['employee']
#         bradford_factor = item['bradford_factor']
#
#         # Include all absences for each employee
#         for absence in employee.absences:
#             data.append({
#                 'Name': employee.name,
#                 'Department': employee.department,
#                 'Start Date': absence.start_date,
#                 'End Date': absence.end_date,
#                 'Reason': absence.reason,
#                 'Duration (Days)': absence.duration_days,
#                 'Bradford Factor': bradford_factor  # Same Bradford Factor for each row of the same employee
#             })
#
#     # Convert the data to a DataFrame
#     df = pd.DataFrame(data)
#
#     # Create a BytesIO object to save the Excel file in memory
#     result = BytesIO()
#
#     # Create an Excel writer object using the BytesIO object
#     with pd.ExcelWriter(result, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Top 10 Employees')
#
#     # Save the file and reset the buffer position
#     result.seek(0)
#
#     # Return the file as a response
#     return send_file(result, as_attachment=True, download_name='top10_bradford_factor_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# to go to print report department wise

#print exel report department wise
@app.route('/generate_excel_report', methods=['GET'])
def generate_excel_report():
    department = request.args.get('department')

    # Query employees by department
    employees = Employee.query.filter_by(department=department).all()
    data = []

    for employee in employees:
        bradford_factor = employee.calculate_bradford_factor()

        # Collecting only those with a Bradford factor greater than 0
        if bradford_factor > 0:
            data.append({
                'Name': employee.name,
                'Department': employee.department,
                'Bradford Factor': bradford_factor
            })

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)


    # Create a BytesIO object to save the Excel file in memory
    result = BytesIO()

    # Create an Excel writer object using the BytesIO object
    with pd.ExcelWriter(result, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f"{department} Employees")

    # Save the file and reset the buffer position
    result.seek(0)

    # Return the file as a response
    return send_file(result, as_attachment=True, download_name=f'{department} Employees  Bradford Factor Report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/pdf_report_form')
def pdf_report_form():
    return render_template('pdf_report_form.html')

@app.route('/exel_report_farm')
def exel_report_farm():
    return render_template('exel_report_farm.html')

if __name__ == "__main__":
    app.run(debug=True)
