# CamWatch AI - Webcam Motion Detector

A real-time motion detection application built with Python, OpenCV, and Streamlit. This project demonstrates advanced computer vision techniques, asynchronous programming with threading, and modern web application development.

> **Portfolio Project**: This project showcases my technical expertise and skillset in Python, Artificial Intelligence, Machine Learning, Computer Vision, and full-stack application development.

## 🎯 Project Overview

CamWatch AI is an intelligent webcam monitoring system that detects motion in real-time, captures images of detected activities, and sends email notifications. The application uses WebRTC for browser-based video streaming, features a responsive web interface built with Streamlit, and uses Python threading to keep the UI non-blocking for smooth performance.

## ✨ Key Features

- **Real-Time Motion Detection**: Advanced frame differencing algorithm with adaptive background subtraction
- **WebRTC Video Streaming**: Browser-based video capture using WebRTC for better compatibility and performance
- **Visual Feedback**: Green bounding boxes around detected motion areas
- **Email Notifications**: Automated email alerts with timestamped images when motion is detected
- **Timezone Support**: Automatic timezone detection with timestamps in your local timezone
- **Non-Blocking UI**: Threading implementation ensures smooth video streaming without UI freezes
- **Adaptive Background**: Automatic baseline reset every 5 seconds to adapt to lighting changes
- **User-Specific Storage**: Organized image storage per user email address
- **Automatic Cleanup**: Images are automatically deleted after email sending or when camera stops

## 🛠️ Technical Stack

- **Python 3.x**: Core programming language
- **OpenCV (cv2)**: Computer vision and image processing
- **Streamlit**: Web application framework for UI
- **streamlit-webrtc**: WebRTC integration for browser-based video streaming
- **aiortc**: WebRTC library for real-time communication
- **Pillow (PIL)**: Image manipulation and processing
- **pytz**: Timezone handling and conversion
- **SMTP**: Email notification system
- **Threading**: Asynchronous operations for non-blocking UI

## 📚 References & Documentation

The following documentation and articles were helpful during development:

1. [Streamlit API Reference](https://docs.streamlit.io/develop/api-reference) - Comprehensive guide to Streamlit's API for building interactive web applications
2. [OpenCV Color Conversions](https://docs.opencv.org/3.4/d8/d01/group__imgproc__color__conversions.html) - Documentation for color space conversions including BGR to grayscale
3. [OpenCV Thresholding Tutorial](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) - Guide to image thresholding techniques used for motion detection
4. [GeeksforGeeks - OpenCV Video Capture](https://www.geeksforgeeks.org/python/python-opencv-capture-video-from-camera/) - Tutorial on capturing video from camera using OpenCV
5. [OpenCV Erosion & Dilation](https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html) - Documentation on morphological operations (dilation) for image processing
6. [OpenCV Image Filtering](https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c) - Reference for Gaussian blur and other image filtering functions

## 🔬 Technical Implementation

### WebRTC Video Processing

The application uses WebRTC for video streaming, which allows direct browser-to-browser communication. A custom `MotionTransformer` class processes video frames in real-time using the `VideoTransformerBase` interface. This approach provides better performance and compatibility compared to traditional server-side video capture.

### Motion Detection Algorithm

The motion detection uses a frame differencing approach:

1. **Frame Preprocessing**: Frames are converted to grayscale and Gaussian blur (21x21 kernel) is applied to reduce noise
2. **Background Subtraction**: Current frame is compared against a baseline frame using absolute difference
3. **Thresholding**: Binary threshold (60) is applied to identify significant changes
4. **Morphological Operations**: The thresholded image is dilated to fill gaps in detected objects
5. **Contour Detection**: Contours are found and filtered by area (minimum 10,000 pixels) to reduce false positives
6. **Visualization**: Green bounding boxes are drawn around detected motion regions

### Threading Architecture

Python's `threading` module is used to keep the UI responsive:

- **Thread-Safe Email Storage**: An `EmailStorage` class with locks ensures safe access to email and timezone data across threads
- **Email Sending Thread**: Email notifications are sent asynchronously without blocking the video processing loop
- **Image Cleanup Thread**: User image folders are deleted after email delivery in the background
- **Daemon Threads**: Ensures proper cleanup when the application exits

### State Management

The state management system tracks:

- Motion status across frames (0 = no motion, 1 = motion detected)
- 2-frame history to detect motion end events
- Adaptive baseline reset mechanism (every 5 seconds)
- User-specific image storage
- Timezone information for accurate timestamp generation

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- Webcam/camera device
- Gmail account (for email notifications)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/JayKCDev/webcam-motion-detector.git
   cd webcam-motion-detector
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure email credentials**

   You can set up email credentials in two ways:

   **Option 1: Environment variables** (for local development)

   Create a `.env` file in the project root:

   ```env
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-gmail-app-password
   ```

   **Option 2: Streamlit secrets** (for deployed apps)

   Configure secrets in Streamlit deployment platform (Streamlit Cloud, etc.)

   > **Note**: For Gmail, you'll need to generate an [App Password](https://support.google.com/accounts/answer/185833) instead of using your regular password. The app will try Streamlit secrets first, then fall back to environment variables.

## 🚀 Usage

1. **Start the Streamlit application**

   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**

   - The application will open in your default browser at `http://localhost:8501`

3. **Configure email (optional)**

   - Enter your email address in the input field before starting the camera
   - Your timezone will be automatically detected from your browser
   - If no email is provided, motion will still be detected but no email notifications will be sent

4. **Start monitoring**

   - Click "START" to begin motion detection
   - Allow camera access when prompted by your browser
   - The live video feed will display with green boxes around detected motion
   - When motion ends, an email notification will be sent with a timestamped image (if email is configured)

5. **Stop monitoring**
   - Click "STOP" when you're done
   - All captured images will be automatically cleaned up

## 📁 Project Structure

```
webcam-motion-detector/
├── app.py                 # Streamlit web application with WebRTC integration
├── main.py                # Core motion detection logic
├── emailing.py            # Email notification system
├── requirements.txt       # Python dependencies
├── packages.txt           # System packages (for deployment)
├── .env                   # Environment variables (not in repo)
├── .gitignore            # Git ignore rules
├── images/               # Captured images storage (user-specific folders)
└── README.md             # Project documentation
```

## 🔧 Configuration

### Email Credentials

The application supports two methods for email configuration:

**Environment Variables** (`.env` file):

- `SENDER_EMAIL`: Gmail address for sending notifications
- `SENDER_PASSWORD`: Gmail app password (not regular password)

**Streamlit Secrets** (for deployed apps):

- `SENDER_EMAIL`: Gmail address
- `SENDER_PASSWORD`: Gmail app password

The app checks Streamlit secrets first, then falls back to environment variables if secrets aren't available.

## 🎓 Skills Demonstrated

This portfolio project demonstrates expertise in:

- **Computer Vision**: Frame differencing, background subtraction, contour detection
- **Image Processing**: Grayscale conversion, Gaussian blur, thresholding, morphological operations
- **WebRTC Integration**: Real-time video streaming using WebRTC protocols
- **Asynchronous Programming**: Threading with thread-safe data structures for non-blocking operations
- **Web Development**: Streamlit framework for interactive web applications
- **State Management**: Efficient state tracking and management across threads
- **Timezone Handling**: Automatic timezone detection and conversion using JavaScript and pytz
- **Email Integration**: SMTP protocol implementation with flexible credential management
- **File Management**: Organized storage and automatic cleanup
- **Software Architecture**: Modular design with separation of concerns
- **Error Handling**: Robust exception handling and graceful degradation

## 🔒 Security Notes

- Gmail App Passwords are used instead of regular passwords
- Images are stored locally and automatically cleaned up
- Email credentials can be stored securely using environment variables or Streamlit secrets
- WebRTC uses STUN servers for connectivity without exposing sensitive data
