import streamlit as st
import tempfile
import os
from verification import register_user, predict_verification

# Page Configuration
st.set_page_config(page_title="Speaker Verification", page_icon="🎙️", layout="centered")

# App Header
st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>🎙️ Speaker Verification App</h1>
    <p style='text-align: center; color: gray;'>Register and verify speakers with voice samples</p>
    <hr style='margin-top: 0px;'>
""", unsafe_allow_html=True)

# Session State Init
if "username" not in st.session_state:
    st.session_state.username = ""
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False

# Reset Form on Successful Registration
if st.session_state.registration_success:
    st.session_state.username = ""
    st.session_state.registration_success = False
    st.rerun()

# --- Tabs Layout ---
tab1, tab2 = st.tabs(["📝 Register", "🔍 Verify"])

# --- Tab 1: Registration ---
with tab1:
    st.markdown("### Step 1: Register a New User")
    username = st.text_input("👤 Enter a username", key="username")

    enrol_files = st.file_uploader(
        "🎧 Upload 3 enrollment audio files (.flac or .wav)",
        type=["flac", "wav"],
        accept_multiple_files=True,
        key="enrol"
    )

    register_button = st.button("✅ Register", key="register_btn")

    if register_button:
        if username and len(enrol_files) == 3:
            temp_files = []
            try:
                for file in enrol_files:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".flac")
                    temp_file.write(file.read())
                    temp_file.close()
                    temp_files.append(temp_file.name)

                register_user(username, *temp_files)
                st.success(f"🎉 User **{username}** registered successfully!")
                st.session_state.registration_success = True

            except ValueError as e:
                st.error(f"⚠️ {str(e)}")
            except Exception as e:
                st.error(f"🚨 An unexpected error occurred: {str(e)}")
            finally:
                for path in temp_files:
                    if os.path.exists(path):
                        os.remove(path)
        else:
            st.warning("⚠️ Please upload exactly 3 files and enter a username.")

# --- Tab 2: Verification ---
with tab2:
    st.markdown("### Step 2: Verify a Speaker")
    verify_username = st.text_input("👤 Username to verify", key="verify_username")

    test_file = st.file_uploader("🎤 Upload a test audio file", type=["flac", "wav"], key="test")

    verify_button = st.button("🔍 Verify", key="verify_btn")

    if verify_button:
        if verify_username and test_file:
            try:
                temp_test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".flac")
                temp_test_file.write(test_file.read())
                temp_test_file.close()
                test_path = temp_test_file.name

                verified, score = predict_verification(verify_username, test_path)
                if verified:
                    st.success(f"✅ Speaker verified! Confidence Score: {score:.2f}")
                else:
                    st.error(f"❌ Speaker not verified. Confidence Score: {score:.2f}")
            except ValueError as e:
                st.error(f"⚠️ {str(e)}")
            except Exception as e:
                st.error(f"🚨 An unexpected error occurred: {str(e)}")
            finally:
                if os.path.exists(test_path):
                    os.remove(test_path)
        else:
            st.warning("⚠️ Please enter a username and upload a test file.")
