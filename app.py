import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, \
    RTCConfiguration
import av
import numpy as np
from threading import Thread, Lock
from main import init_state, process_frame, remove_images
from emailing import send_email
import os
from streamlit.components.v1 import html

# Configure WebRTC with TURN servers for better connectivity
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
    ],
    "iceTransportPolicy": "all",
})


# Shared email storage that works across threads
class EmailStorage:
    def __init__(self):
        self.email = ""
        self.timezone = "UTC"
        self.lock = Lock()

    def set_email(self, email):
        with self.lock:
            self.email = email

    def get_email(self):
        with self.lock:
            return self.email

    def set_timezone(self, timezone):
        with self.lock:
            self.timezone = timezone

    def get_timezone(self):
        with self.lock:
            return self.timezone


# Create GLOBAL email storage (not in session state)
GLOBAL_EMAIL_STORAGE = EmailStorage()


class MotionTransformer(VideoTransformerBase):
    def __init__(self):
        self.state = init_state()
        self.email_sent = False

    def recv(self, frame):
        try:
            img = frame.to_ndarray(format="bgr24")

            # Get email and timezone from global storage
            user_email = GLOBAL_EMAIL_STORAGE.get_email()
            user_timezone = GLOBAL_EMAIL_STORAGE.get_timezone()

            processed_frame, new_state, motion_ended, final_image, motion_time = process_frame(
                img,
                self.state,
                email=user_email,
                timezone=user_timezone
            )
            self.state = new_state

            # Reset email flag if motion is detected again
            if self.state["status_list"] and self.state["status_list"][
                -1] == 1:
                self.email_sent = False

            if motion_ended and not self.email_sent:
                if user_email.strip() != "":
                    Thread(
                        target=send_email,
                        args=(final_image, user_email, motion_time),
                        daemon=True
                    ).start()

                self.email_sent = True

            # Return processed frame (with green boxes)
            return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")

        except Exception as e:
            # Log error but don't crash the stream
            # Return original frame if processing fails
            return frame


# Initialize session state
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_timezone" not in st.session_state:
    st.session_state.user_timezone = "UTC"

# Page configuration
st.set_page_config(
    page_title="CamWatch AI | Jay K.C. Portfolio",
    layout="centered"
)

# Detect user's timezone using JavaScript
timezone_script = """
<script>
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: timezone}, '*');
</script>
"""

# Get timezone from browser
user_timezone = html(timezone_script, height=0)
if user_timezone:
    st.session_state.user_timezone = user_timezone
    GLOBAL_EMAIL_STORAGE.set_timezone(user_timezone)
else:
    # Fallback to session state timezone
    GLOBAL_EMAIL_STORAGE.set_timezone(st.session_state.user_timezone)

st.title("CamWatch AI")
st.markdown("Real-time motion detection using your webcam")

# Email input BEFORE webrtc_streamer
email_input = st.text_input(
    "Enter your email (optional)",
    value=st.session_state.user_email,
    help="Receive motion detection alerts with captured images",
    placeholder="example@email.com"
)

# Update email immediately when changed
if email_input != st.session_state.user_email:
    st.session_state.user_email = email_input
    GLOBAL_EMAIL_STORAGE.set_email(email_input)

# Always sync the global storage with session state
GLOBAL_EMAIL_STORAGE.set_email(st.session_state.user_email)

# WebRTC streamer
ctx = webrtc_streamer(
    key="motion-detection",
    video_transformer_factory=MotionTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# Check if camera is active
camera_active = ctx.state.playing if ctx.state else False

# Information message
if camera_active:
    if st.session_state.user_email.strip() != "":
        st.success(
            f"✅ Motion alerts will be sent to: {st.session_state.user_email}")
    else:
        st.info(
            "📧 No email provided - motion will be detected but no alerts will be sent")
else:
    if email_input.strip() == "":
        st.info(
            "💡 **Tip:** Provide an email to receive motion detection alerts with captured images. Images are automatically deleted when the session ends.")
    else:
        st.info(
            f"✅ Email configured: {email_input}. Click START to begin monitoring.")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Enter your email** (optional) before starting the camera
    2. **Allow camera access** when prompted by your browser
    3. Click **START** to begin monitoring
    4. The app will detect motion and draw green boxes around moving objects
    5. If motion is detected and stops, you'll receive an email with a captured image
    6. Click **STOP** when you're done

    **Note:** 
    - Email input is locked once the camera starts to prevent errors
    - Your camera feed is processed in real-time
    - Images are only saved if you provide an email address
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'><a href='https://www.linkedin.com/in/jaykcdev/' target='_blank' style='color: gray; text-decoration: none;'>Jay Karamchandani</a> | Portfolio Project</div>",
    unsafe_allow_html=True
)