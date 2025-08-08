import cv2
import numpy as np
import time
import pygame
import threading
import os
from dotenv import load_dotenv
from Chatbot import start_bot_conversation, speak

load_dotenv()

net = cv2.dnn.readNetFromCaffe(os.getenv("DEPLOY_PROTOTXT"), os.getenv("CAFFEMODEL"))

class_labels = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
                "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
person_class_index = 15

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)

people_in_frame_1 = {}
people_in_frame_2 = {}

interaction_lock = threading.Lock()
interaction_in_progress = False

def is_same_person(box1, box2, threshold=0.5):
    x1, y1, x2, y2 = box1
    x1b, y1b, x2b, y2b = box2
    ix1 = max(x1, x1b)
    iy1 = max(y1, y1b)
    ix2 = min(x2, x2b)
    iy2 = min(y2, y2b)
    if ix2 <= ix1 or iy2 <= iy1:
        return False
    intersection = (ix2 - ix1) * (iy2 - iy1)
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x2b - x1b) * (y2b - y1b)
    iou = intersection / float(area1 + area2 - intersection)
    return iou > threshold

def is_off_screen(x1, y1, x2, y2, width, height):
    return x2 < 0 or x1 > width or y2 < 0 or y1 > height

def stop_ai_conversation(stop_event):
    stop_event.set()

def handle_interaction(stop_event):
    global interaction_in_progress
    with interaction_lock:
        if interaction_in_progress:
            return
        interaction_in_progress = True

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(os.getenv("NOTICE"))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if stop_event.is_set():
                pygame.mixer.music.stop()
                return
            time.sleep(0.1)

        if stop_event.is_set():
            return

        speak("Welcome! What would you like to know about UK music?")
        if not stop_event.is_set():
            start_bot_conversation(stop_event)

    finally:
        with interaction_lock:
            interaction_in_progress = False

def process_frame(frame, people_in_frame, camera_id):
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), (127.5,), False)
    net.setInput(blob)
    detections = net.forward()

    height, width = frame.shape[:2]
    current_frame_boxes = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.2:
            class_id = int(detections[0, 0, i, 1])
            if class_id == person_class_index:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (startX, startY, endX, endY) = box.astype("int")
                current_frame_boxes.append((startX, startY, endX, endY))

                matched_id = None
                for tracked_box in people_in_frame.keys():
                    if is_same_person((startX, startY, endX, endY), tracked_box):
                        matched_id = tracked_box
                        break

                if matched_id:
                    if is_off_screen(startX, startY, endX, endY, width, height):
                        people_in_frame[matched_id]["stop_event"].set()
                        del people_in_frame[matched_id]
                else:
                    stop_event = threading.Event()
                    people_in_frame[(startX, startY, endX, endY)] = {
                        "start_time": time.time(),
                        "interested": False,
                        "stop_event": stop_event
                    }

                for person_id, info in people_in_frame.items():
                    if is_same_person((startX, startY, endX, endY), person_id):
                        elapsed = time.time() - info["start_time"]
                        if elapsed >= 15 and not info["interested"]:
                            info["interested"] = True
                            stop_event = info["stop_event"]
                            threading.Thread(target=handle_interaction, args=(stop_event,), daemon=True).start()

                        box_color = (0, 0, 255) if elapsed >= 15 else (0, 255, 0)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), box_color, 2)
                        cv2.putText(frame, f"Time: {elapsed:.1f}s", (startX, startY - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

    for tracked_box in list(people_in_frame.keys()):
        if not any(is_same_person(tracked_box, box) for box in current_frame_boxes):
            people_in_frame[tracked_box]["stop_event"].set()
            del people_in_frame[tracked_box]

def handle_cameras():
    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        if not ret1 or not ret2:
            break

        process_frame(frame1, people_in_frame_1, 1)
        process_frame(frame2, people_in_frame_2, 2)

        cv2.putText(frame1, "Zone 5: 1975-1985", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame2, "Zone 8: 2004-Present", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        combined = np.hstack((frame1, frame2))
        cv2.imshow("Real-time UK Music Bot", combined)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()

# --- Main Application ---
if __name__ == "__main__":
    handle_cameras()
