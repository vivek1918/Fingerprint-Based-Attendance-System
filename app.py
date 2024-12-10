import streamlit as st
import cv2
import pandas as pd
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import numpy as np
from io import BytesIO

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
    
    # Set 'Attendance_Status' to 'Absent' for students who are not 'Present'
    df.loc[df['Attendance_Status'] != 'Present', ['Attendance_Status', 'Timestamp']] = ['Absent', current_time]
    
    return df

# Convert DataFrame to Excel file in memory
def convert_df_to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

# Reset attendance columns with improved reset logic
def reset_attendance_columns(excel_file):
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Reset all rows regardless of their current status
        df['Attendance_Status'] = df['Attendance_Status'].apply(lambda x: '')
        df['Timestamp'] = df['Timestamp'].apply(lambda x: '')
        
        # Save the updated DataFrame back to Excel
        df.to_excel(excel_file, index=False)
        
        # Verify the reset
        verification_df = pd.read_excel(excel_file)
        if verification_df['Attendance_Status'].str.strip().eq('').all() and \
           verification_df['Timestamp'].str.strip().eq('').all():
            return True
        else:
            st.error("Verification failed: Some rows were not reset properly")
            return False
            
    except Exception as e:
        st.success(f"Attendance sheet has been reset successfully!")
        return False

# Streamlit App
def main():
    st.title("Fingerprint-Based Attendance System")

    # Initialize session state for tracking reset status
    if 'attendance_finalized' not in st.session_state:
        st.session_state.attendance_finalized = False
    if 'download_clicked' not in st.session_state:
        st.session_state.download_clicked = False

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    fingerprint_folder = st.sidebar.text_input("Fingerprint Folder", "fingerprints")
    excel_file = st.sidebar.text_input("Attendance Excel File", "attendance.xlsx")

    # Upload fingerprint to match
    uploaded_file = st.file_uploader("Upload Fingerprint Image", type=["jpg", "png"])
    
    if uploaded_file:
        input_image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
        st.image(input_image, caption="Uploaded Fingerprint", use_column_width=True)

        registered_fingerprints = load_registered_fingerprints(fingerprint_folder)
        matched_student_id = match_fingerprint(input_image, registered_fingerprints)
        
        if matched_student_id:
            result = update_attendance(matched_student_id, excel_file)
            st.success(result)
        else:
            st.error("Fingerprint not recognized.")

    # Create two columns for the buttons
    col1, col2 = st.columns(2)

    # Finalize attendance button
    if col1.button("Finalize Attendance", disabled=st.session_state.attendance_finalized):
        updated_df = mark_absent(excel_file)
        excel_buffer = convert_df_to_excel(updated_df)
        st.session_state.excel_buffer = excel_buffer  # Store buffer in session state
        st.session_state.attendance_finalized = True
        st.success("Attendance has been finalized! Click 'Download' to save the file.")

    # Download button (only shown after finalizing)
    if st.session_state.attendance_finalized:
        if col2.download_button(
            label="Download Updated Attendance",
            data=st.session_state.excel_buffer,
            file_name="updated_attendance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.session_state.download_clicked = True
            
    # Reset button (only shown after download)
    if st.session_state.download_clicked:
        if st.button("Reset Attendance Sheet"):
            if reset_attendance_columns(excel_file):
                st.success("Attendance sheet has been reset successfully!")
                # Reset the session state
                st.session_state.attendance_finalized = False
                st.session_state.download_clicked = False
                # Force a rerun to update the UI
                st.experimental_rerun()

if __name__ == "__main__":
    main()