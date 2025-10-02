import cv2
import json

slot_coordinates = {}
drawing = False
ix, iy = -1, -1
slot_id = 1

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, slot_id, frame_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        slot_coordinates[slot_id] = (ix, iy, x, y)
        print(f"Slot {slot_id} saved: {(ix, iy, x, y)}")
        slot_id += 1
        cv2.rectangle(frame_copy, (ix, iy), (x, y), (255, 0, 0), 2)
        cv2.imshow("Select Slots", frame_copy)

# Load video
cap = cv2.VideoCapture(r"C:\Users\anike\Downloads\check01.mp4")
ret, frame = cap.read()
frame_copy = frame.copy()

cv2.namedWindow("Select Slots")
cv2.setMouseCallback("Select Slots", draw_rectangle)

print("Click top-left and bottom-right corners of each slot. Press ESC when done.")

while True:
    cv2.imshow("Select Slots", frame_copy)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cv2.destroyAllWindows()
cap.release()

# Save coordinates to JSON
with open("slots.json", "w") as f:
    json.dump(slot_coordinates, f)

print("Slot coordinates saved to slots.json")
