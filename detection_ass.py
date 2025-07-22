import matplotlib
matplotlib.use('TkAgg')  # Ensure GUI backend works properly
import matplotlib.pyplot as plt
import serial
import time
import csv
import os
from collections import deque
import threading
import numpy as np
from scipy.ndimage import label

# === Configuration ===
SERIAL_PORT = '/dev/cu.usbmodem101'  # Update to your device
BAUD_RATE = 115200
CSV_FILENAME = "sensor_log.csv"
MAX_POINTS = 200  # Number of points to show on the plot

# === Serial Setup ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  # Give time for Arduino to reset

# === CSV Setup ===
file_exists = os.path.isfile(CSV_FILENAME)
csvfile = open(CSV_FILENAME, mode='a', newline='')
writer = csv.writer(csvfile)
if not file_exists:
    writer.writerow(["Timestamp (ms)", "Sensor1 (mm)", "Sensor2 (mm)", "Width (mm)"])

# === Data Buffers for Plot ===
timestamps = deque(maxlen=MAX_POINTS)
widths = deque(maxlen=MAX_POINTS)

# === Matplotlib Plot Setup ===
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', label="Width (mm)")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Width (mm)")
ax.set_title("Real-Time Width Plot")
ax.grid(True)
ax.legend()
fig.show()
fig.canvas.draw()

# === Classification Flag ===
classify_flag = threading.Event()

def wait_for_enter():
    input("Press Enter to classify current data...\n")
    classify_flag.set()

# Start initial key wait thread
threading.Thread(target=wait_for_enter, daemon=True).start()

# === Tire Detection Function ===
def detect_tires_flat(signal, title="Signal", threshold=5):
    binary = np.array(signal) > threshold
    labeled, num_features = label(binary)

    tire_widths = []
    tire_positions = []

    for i in range(1, num_features + 1):
        idx = np.where(labeled == i)[0]
        width = np.max(np.array(signal)[idx])  # width in mm
        tire_widths.append(width)
        tire_positions.append(np.mean(idx))

    print(f"\n📊 {title}")
    print(f"Detected {num_features} tires.")
    for i, w in enumerate(tire_widths, 1):
        tire_type = "Front" if i == 1 else "Rear" if i == 2 else f"Tire {i}"
        print(f"{tire_type} tire width: {w:.2f} mm")

    # Simulated time base for plotting
    fake_time = np.linspace(0, len(signal)/50, len(signal))
    
    # Plot classification result
    plt.figure(figsize=(12, 4))
    plt.plot(fake_time, signal, label='Width Signal')
    for pos, w in zip(tire_positions, tire_widths):
        plt.plot(fake_time[int(pos)], w, 'ro')
        plt.text(fake_time[int(pos)], w + 5, f'{w:.1f} mm', ha='center', color='red')
    plt.title(f"Tire Detection - {title}")
    plt.xlabel("Time (s)")
    plt.ylabel("Tire Width (mm)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

# === Main Loop ===
try:
    while True:
        line_serial = ser.readline().decode('utf-8').strip()
        if line_serial:
            try:
                ts, d1, d2, width = map(int, line_serial.split(","))
                width = max(0, width)
                print(f"Time: {ts} ms | Sensor1: {d1} mm | Sensor2: {d2} mm | Width: {width} mm")

                # Save to CSV
                writer.writerow([ts, d1, d2, width])

                # Update data
                timestamps.append(ts)
                widths.append(width)

                # Update plot data
                line.set_data(timestamps, widths)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()

                # Trigger classification on Enter
                if classify_flag.is_set():
                    print("\nRunning tire classification on current data...")
                    detect_tires_flat(list(widths), "Live Sensor Data")
                    classify_flag.clear()
                    threading.Thread(target=wait_for_enter, daemon=True).start()

            except ValueError:
                print(f"Malformed line: {line_serial}")
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()
    csvfile.close()
    plt.ioff()
    plt.show()
