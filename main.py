import os
import cv2
import time
import glob
import shutil

def init_state():
    state = {
        "first_frame": None,
        "status_list": [],
        "count": 1,
        "detected_image": None,
        "last_reset_time": time.time()
    }
    return state

def process_frame(frame, state, email=None):
    status = 0
    # Turn frame into grayscale for simplification and comparison
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply blur to greyscaled frame
    grey_frame_gauss = cv2.GaussianBlur(grey_frame, (21, 21), 0)

    # store first ever frame in variable for future comparison
    if state["first_frame"] is None:
        state["first_frame"] = grey_frame_gauss

    current_time = time.time()
    if current_time - state["last_reset_time"] > 5:
        state["first_frame"] = grey_frame_gauss
        state["last_reset_time"] = current_time

    # Calculate abs diff between first_frame V/S current frame
    delta_frame = cv2.absdiff(state["first_frame"], grey_frame_gauss)

    # Apply threshold to the frame to reduce picking static objects
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

    # Dilate the threshold
    dilated_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # find contours in dilated_frame to apply green box around the moving object
    contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
                                  3)
        if rectangle.any():
            status = 1
            if email:  # Only store images if email is provided
                os.makedirs(f"images/{email}", exist_ok=True)
                cv2.imwrite(f"images/{email}/{state['count']}.png", frame)
                state["count"] += 1
                all_images = sorted(glob.glob(f"images/{email}/*.png"))
                if all_images:
                    index = len(all_images) // 2
                    state["detected_image"] = all_images[index]

    state["status_list"].append(status)
    state["status_list"] = state["status_list"][-2:]

    # Detect motion end event (NO STATE MUTATION)
    motion_ended = False
    final_image = None

    if len(state["status_list"]) == 2:
        if state["status_list"][0] == 1 and state["status_list"][1] == 0:
            motion_ended = True
            final_image = state["detected_image"]

    if motion_ended:
        state["first_frame"] = grey_frame_gauss

    return frame, state, motion_ended, final_image

def remove_images(user_email):
    if not user_email:
        return
    user_folder = f"images/{user_email}"

    if not os.path.exists(user_folder):
        return

    try:
        shutil.rmtree(user_folder)
    except Exception as e:
        print("Error deleting folder:", e)
