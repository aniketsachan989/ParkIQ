import cv2
import numpy as np
import json
from datetime import datetime
from openpyxl import Workbook
import os

# ----------------------------
# Load slot coordinates from JSON
# ----------------------------
with open("slots.json", "r") as f:
    slots = json.load(f)
slots = {int(k): tuple(v) for k, v in slots.items()}

# ----------------------------
# Setup video
# ----------------------------
video_path = r"C:\Users\anike\Downloads\check01.mp4"  # Change as needed
cap = cv2.VideoCapture(video_path)
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50)

# ----------------------------
# Setup Excel file with timestamp
# ----------------------------
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
excel_file = f"occupied_slots_{timestamp}.xlsx"

wb = Workbook()
ws = wb.active
ws.append(["Slot_No", "Date", "Time"])  # header

# Track previous status to avoid duplicate entries
prev_status = {sid: "Empty" for sid in slots.keys()}

# ----------------------------
# Main Loop
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(gray)

    for sid, (x1, y1, x2, y2) in slots.items():
        roi = fgmask[y1:y2, x1:x2]
        white_pixels = cv2.countNonZero(roi)
        total_pixels = roi.size
        fill_ratio = white_pixels / total_pixels if total_pixels > 0 else 0

        if fill_ratio > 0.2:
            status = "Occupied"
            color = (0, 0, 255)
        else:
            status = "Empty"
            color = (0, 255, 0)

        # Draw rectangle & slot status
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{sid}:{status}", (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # If slot changed from Empty → Occupied, log to Excel
        if status == "Occupied" and prev_status[sid] == "Empty":
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")   # Date as string
            time_str = now.strftime("%H:%M:%S")   # Time as string
            ws.append([sid, date_str, time_str])
            try:
                wb.save(excel_file)
            except PermissionError:
                print(f"Cannot save {excel_file}. Please close it if it’s open.")
            print(f"Logged Slot {sid} at {date_str} {time_str}")

        prev_status[sid] = status  # update previous status

    cv2.imshow("Parking Slot Detection", frame)
    if cv2.waitKey(30) & 0xFF == ord("q"):
        break

# Auto-adjust column width for better Excel display
for column_cells in ws.columns:
    length = max(len(str(cell.value)) for cell in column_cells)
    ws.column_dimensions[column_cells[0].column_letter].width = length + 2

cap.release()
cv2.destroyAllWindows()
wb.save(excel_file)
print(f"Excel log saved as {excel_file}")
