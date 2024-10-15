// Sample employee data
const employees = [
    { name: 'Alice Johnson', department: 'HR', bradfordFactor: 35 },
    { name: 'Bob Smith', department: 'IT', bradfordFactor: 20 },
    { name: 'Charlie Brown', department: 'Finance', bradfordFactor: 45 },
    { name: 'Diana Prince', department: 'Marketing', bradfordFactor: 30 },
    { name: 'Ethan Hunt', department: 'IT', bradfordFactor: 50 }
];

// Function to sort employees by Bradford Factor and display them
function displayEmployeeRecords() {
    const sortedEmployees = employees.sort((a, b) => b.bradfordFactor - a.bradfordFactor); // Sort descending by Bradford Factor
    const tableBody = document.getElementById('employeeTableBody');

    sortedEmployees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${employee.name}</td>
            <td>${employee.department}</td>
            <td>${employee.bradfordFactor}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Call the function to display records when the page loads
window.onload = displayEmployeeRecords;
