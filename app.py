import streamlit as st
import cv2
import pandas as pd
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Load registered fingerprints
def load_registered_fingerprints(fingerprint_folder):
    fingerprints = {}
    for student_id in range(101, 110):  # Example range
        image_path = f"{fingerprint_folder}/{student_id}.jpg"
        fingerprints[student_id] = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return fingerprints

# Compare fingerprints using SSIM
def match_fingerprint(input_image, registered_fingerprints):
    input_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    input_resized = cv2.resize(input_gray, (200, 200))
    
    for student_id, registered_image in registered_fingerprints.items():
        registered_resized = cv2.resize(registered_image, (200, 200))
        
        score, _ = ssim(input_resized, registered_resized, full=True)
        if score > 0.8:  # Threshold for matching
            return student_id
    return None

# Update attendance in Excel
def update_attendance(student_id, excel_file):
    df = pd.read_excel(excel_file)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.loc[df['Fingerprint_ID'] == student_id, ['Attendance_Status', 'Timestamp']] = ['Present', current_time]
    df.to_excel(excel_file, index=False)
    return f"Attendance marked for Student ID: {student_id}"

# Mark all students as absent who have not been marked present
def mark_absent(excel_file):
    df = pd.read_excel(excel_file)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.loc[df['Attendance_Status'] != 'Present', ['Attendance_Status', 'Timestamp']] = ['Absent', current_time]
    df.to_excel(excel_file, index=False)
    return "All attendance finalized, absent students marked."

# Streamlit App
def main():
    st.title("Fingerprint-Based Attendance System")

    # Sidebar for fingerprint dataset and attendance file
    st.sidebar.header("Configuration")
    fingerprint_folder = st.sidebar.text_input("Fingerprint Folder", "fingerprints")
    excel_file = st.sidebar.text_input("Attendance Excel File", "attendance.xlsx")

    # Upload fingerprint to match
    uploaded_file = st.file_uploader("Upload Fingerprint Image", type=["jpg", "png"])
    
    if uploaded_file:
        input_image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
        st.image(input_image, caption="Uploaded Fingerprint", use_column_width=True)

        # Load registered fingerprints
        registered_fingerprints = load_registered_fingerprints(fingerprint_folder)

        # Match fingerprint
        matched_student_id = match_fingerprint(input_image, registered_fingerprints)
        if matched_student_id:
            result = update_attendance(matched_student_id, excel_file)
            st.success(result)
        else:
            st.error("Fingerprint not recognized.")

    # Button to finalize attendance and mark absent students
    if st.button("Finalize Attendance"):
        result = mark_absent(excel_file)
        st.success(result)

if __name__ == "__main__":
    main()
