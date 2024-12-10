# Fingerprint-Based Attendance System
This is a fingerprint-based attendance system that allows students to mark their attendance by matching their fingerprint with stored registered fingerprints. The system automatically updates attendance in an Excel file, recording the student's status and timestamp.

## Features
- Fingerprint matching using Structural Similarity Index (SSIM).
- Automatic attendance marking with timestamp.
- Attendance data stored in an Excel sheet.
- Ability to upload fingerprint images for scanning.
- Mark attendance for multiple students.

## Usage

- Upload a fingerprint image from the frontend.
- The system will match the uploaded fingerprint with stored registered fingerprints.
- If a match is found, the attendance is marked as "Present" in the Excel sheet, along with the timestamp.
- If no match is found, an error message will be displayed.

The Excel file will be updated automatically with the status of each student (Present/Absent).

## Technologies Used

- Python
- OpenCV
- Streamlit
- pandas (for managing Excel files)
- scikit-image (for image processing)
