// Fetch Employee Profile
function loadEmployeeProfile(employeeId) {
    fetch(`/api/employee/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            const profileDiv = document.getElementById('employee-profile');
            const employee = data.employee;
            const absences = data.absences;

            // Construct employee profile HTML
            profileDiv.innerHTML = `
                <h3>${employee.username} (Department: ${employee.department})</h3>
                <p><strong>Bradford Factor:</strong> ${employee.bradford_factor}</p>
                <h4>Absence Records</h4>
                <ul>
                    ${absences.map(absence => `
                        <li>${absence.start_date} to ${absence.end_date} (${absence.duration} days): ${absence.reason}</li>
                    `).join('')}
                </ul>
                <button onclick="printReport()">Print Report</button>
            `;
        })
        .catch(err => console.error('Error loading employee profile:', err));
}

// Fetch Sickness Report
function loadSicknessReport() {
    fetch('/api/sickness-report')
        .then(response => response.json())
        .then(data => {
            const reportDiv = document.getElementById('sickness-report');
            const top10 = data.top_10_employees;
            const departmentStats = data.department_stats;

            // Construct sickness report HTML
            reportDiv.innerHTML = `
                <h4>Top 10 Employees by Bradford Factor</h4>
                <ul>
                    ${top10.map(employee => `
                        <li>${employee.employee.username} - Bradford Factor: ${employee.bradford_factor}</li>
                    `).join('')}
                </ul>

                <h4>Department Statistics</h4>
                <table>
                    <tr><th>Department</th><th>Total Absences</th><th>Total Days Absent</th></tr>
                    ${departmentStats.map(stat => `
                        <tr>
                            <td>${stat.department}</td>
                            <td>${stat.total_absences}</td>
                            <td>${stat.total_days}</td>
                        </tr>
                    `).join('')}
                </table>
                <button onclick="printReport()">Print Report</button>
            `;
        })
        .catch(err => console.error('Error loading sickness report:', err));
}

// Function to print the report
function printReport() {
    const printContents = document.querySelector('.container').innerHTML;
    const originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    // Example: Load employee profile for employee ID 1
    document.getElementById('view-profile').addEventListener('click', (event) => {
        event.preventDefault();
        loadEmployeeProfile(1);  // Hardcoded for demo; could be dynamic
    });

    // Load sickness report when the user clicks "View Sickness Report"
    document.getElementById('view-report').addEventListener('click', (event) => {
        event.preventDefault();
        loadSicknessReport();
    });
});
// Add event listener to form submission
document.getElementById('absence-form').addEventListener('submit', (event) => {
    event.preventDefault();

    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const reason = document.getElementById('reason').value;
    const employeeId = 1; // Example employee ID; adjust accordingly

    // Send data to the Flask API
    fetch(`/api/employee/${employeeId}/absence`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
            reason: reason,
        }),
    })
    .then(response => response.json())
    .then(data => {
        alert('Sickness absence added successfully');
        // Optionally reload employee profile after submission
        loadEmployeeProfile(employeeId);
    })
    .catch(err => console.error('Error adding sickness absence:', err));
});
