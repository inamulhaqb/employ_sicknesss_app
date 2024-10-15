document.getElementById('addEmployeeForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Retrieve form values
    const name = document.getElementById('name').value;
    const department = document.getElementById('department').value;
    const email = document.getElementById('email').value;
    const position = document.getElementById('position').value;

    // Here you would typically send the data to your server
    // For this example, we'll just log it to the console
    console.log('Employee added:', { name, department, email, position });

    // Show success message
    document.getElementById('successMessage').style.display = 'block';

    // Clear the form
    document.getElementById('addEmployeeForm').reset();
});
