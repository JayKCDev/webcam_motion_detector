import time
import streamlit as st
import cv2
from threading import Thread
from main import init_state, process_frame, remove_images
from emailing import send_email

if "motion_state" not in st.session_state:
    st.session_state.motion_state = init_state()

if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

if "camera" not in st.session_state:
    st.session_state.camera = None

if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# Placeholder for video frames
frame_placeholder = st.empty()

st.title("CamWatch AI")

email_input = st.text_input("Enter your email (optional)")
st.session_state.user_email = email_input

if email_input.strip() == "":
    st.info("If you provide an email, the app will capture an image of the detected motion and send it to you. The captured image will be automatically deleted when you close the tab, stop the camera, or when no new motion is detected.")

start_button = st.button("Start Camera")
stop_button = st.button("Stop Camera")


# Start camera
if start_button and not st.session_state.camera_active:
    st.session_state.camera = cv2.VideoCapture(0)
    st.session_state.camera_active = True
    st.session_state.motion_state = init_state()

# Stop camera
if stop_button and st.session_state.camera_active:
    st.session_state.camera_active = False
    st.session_state.camera.release()
    remove_images(st.session_state.user_email)

if st.session_state.camera_active:

    # Real-time loop
    while st.session_state.camera_active:
        # Read a frame
        success, frame = st.session_state.camera.read()
        if not success:
            st.warning("Failed to read from camera.")
            break

        # Process the frame through main.py logic
        processed_frame, new_state, motion_ended, final_image = process_frame(
            frame, st.session_state.motion_state, email=st.session_state.user_email
        )

        if st.session_state.motion_state["status_list"][-1] == 1:
            st.session_state.email_sent = False

        # Update the state
        st.session_state.motion_state = new_state

        # Display the processed frame
        frame_placeholder.image(processed_frame, channels="BGR")

        if motion_ended and not st.session_state.email_sent:

            if st.session_state.user_email.strip() != "":
                Thread(target=send_email,
                       args=(final_image, st.session_state.user_email),
                       daemon=True).start()
                Thread(target=remove_images, args=(st.session_state.user_email,)).start()

            st.session_state.email_sent = True

        # Sleep to control FPS (smoothness)
        time.sleep(0.03)