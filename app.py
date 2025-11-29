import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, \
    RTCConfiguration
import av
import numpy as np
from threading import Thread
from main import init_state, process_frame, remove_images
from emailing import send_email
import os

# Configure WebRTC with STUN server for better connectivity
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


class MotionTransformer(VideoTransformerBase):
    def __init__(self):
        self.state = init_state()
        self.email_sent = False
        self.user_email = ""

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        processed_frame, new_state, motion_ended, final_image, motion_time = process_frame(
            img,
            self.state,
            email=self.user_email
        )
        self.state = new_state

        # Reset email flag if motion is detected again
        if self.state["status_list"] and self.state["status_list"][-1] == 1:
            self.email_sent = False

        if motion_ended and not self.email_sent:
            if self.user_email.strip() != "":
                Thread(
                    target=send_email,
                    args=(final_image, self.user_email, motion_time),
                    daemon=True
                ).start()

            self.email_sent = True

        # Return processed frame (with green boxes)
        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


# Initialize session state
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# Page configuration
st.set_page_config(
    page_title="CamWatch AI | Jay K.C. Portfolio",
    layout="centered"
)

st.title("CamWatch AI")
st.markdown("Real-time motion detection using your webcam")

# Create transformer instance first (before email input)
transformer = MotionTransformer()

# WebRTC streamer (placed before email input to check state)
ctx = webrtc_streamer(
    key="motion-detection",
    video_transformer_factory=lambda: transformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# Check if camera is active
camera_active = ctx.state.playing if ctx.state else False

# Email input - disabled when camera is active
email_input = st.text_input(
    "Enter your email (optional)",
    value=st.session_state.user_email,
    help="Receive motion detection alerts with captured images",
    disabled=camera_active,
    placeholder="example@email.com" if not camera_active else "Stop camera, to enter the email"
)

# Update session state only if camera is not active
if not camera_active:
    st.session_state.user_email = email_input

# Set the email for the transformer
transformer.user_email = st.session_state.user_email

# Information message
if camera_active:
    st.warning(
        "🔒 **Camera is active** - Email input is locked to prevent disruptions")
    if st.session_state.user_email.strip() != "":
        st.success(
            f"✅ Motion alerts will be sent to: {st.session_state.user_email}")
    else:
        st.info(
            "📧 No email configured - motion will be detected but no alerts will be sent")
elif email_input.strip() == "":
    st.info(
        "💡 **Tip:** Provide an email to receive motion detection alerts with captured images. Images are automatically deleted when the session ends.")
else:
    st.success(f"✅ Motion alerts will be sent to: {email_input}")

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