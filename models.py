from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta

db = SQLAlchemy()

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    absences = db.relationship('SicknessAbsence', backref='employee', lazy=True)

    def calculate_bradford_factor(self):
            one_year_ago = datetime.now() - timedelta(days=365)

            # Query absences to only include those within the last year
            absences = SicknessAbsence.query.filter(
                SicknessAbsence.employee_rel == self.employee_id,
                SicknessAbsence.start_date >= one_year_ago
            ).all()

            spells = len(absences)  # Total number of absences (spells)

            # Total duration of absences
            total_duration = sum(absence.duration_days for absence in absences)

            # Unique start dates for frequency
            frequency = len(set(absence.start_date for absence in absences))

            # Calculate Bradford Factor
            if spells > 0:
                return (spells * frequency) * total_duration  # Correct formula
            return 0


class SicknessAbsence(db.Model):
    sickness_absence_id = db.Column(db.Integer, primary_key=True)
    employee_rel = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    duration_days = db.Column(db.Integer)  # Store the duration in a column

    def __init__(self,employee_rel, start_date, end_date, reason):
        self.employee_rel = employee_rel  # Corrected foreign key usage
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.duration_days = (end_date - start_date).days + 1  # Calculate and set duration here

