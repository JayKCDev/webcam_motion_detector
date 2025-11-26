import cv2
import time
from emailing import send_email

camera = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []

while True:
    status = 0
    check, frame = camera.read()
    # Turn frame into grayscale for simplification and comparison
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply blur to greyscaled frame
    grey_frame_gauss = cv2.GaussianBlur(grey_frame, (21, 21), 0)
    # store first ever frame in variable for future comparison
    if first_frame is None:
        first_frame = grey_frame_gauss
    # Calculate abs diff between first_frame V/S current frame
    delta_frame = cv2.absdiff(first_frame, grey_frame_gauss)
    # Apply threshold to the frame to reduce picking static objects
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    # Dilate the threshold
    dilated_frame = cv2.dilate(thresh_frame, None, iterations=2)
    # pass delta_frame to .imshow method instead of colored frame

    contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1

    status_list.append(status)
    status_list = status_list[-2:]
    
    if status_list[0] == 1 and status_list[1] == 0:
        send_email()

    cv2.imshow("My Video", frame)
    # Wait for the key press from the user
    key = cv2.waitKey(1)

    # If key pressed by user is 'q' exit the program
    if key == ord("q"):
        break

camera.release()
