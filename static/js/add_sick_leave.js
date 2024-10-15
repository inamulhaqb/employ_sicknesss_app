document.getElementById('sickLeaveForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get form values
    const employeeName = document.getElementById('employeeName').value;
    const leaveStartDate = document.getElementById('leaveStartDate').value;
    const leaveEndDate = document.getElementById('leaveEndDate').value;
    const reason = document.getElementById('reason').value;

    // Here you would typically send this data to your backend via an API
    // For demonstration, we'll just log it to the console
    console.log({
        employeeName,
        leaveStartDate,
        leaveEndDate,
        reason
    });

    // Show success message
    const successMessage = document.getElementById('successMessage');
    successMessage.style.display = 'block';

    // Clear the form after submission
    this.reset();
});
