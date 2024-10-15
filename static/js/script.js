    // JavaScript for Generating and Printing PDF Report
    document.getElementById('generate-report-btn').addEventListener('click', function () {
        // Open the PDF report in a new tab
        let pdfWindow = window.open('/report/top-employees-pdf');

        // After the PDF loads, automatically trigger the print dialog
        pdfWindow.onload = function() {
            pdfWindow.print();
        };
    });
