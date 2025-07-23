import matplotlib
matplotlib.use('TkAgg')  # Ensure GUI backend works properly
import matplotlib.pyplot as plt
import serial
import time
import csv
import os
from collections import deque
from nusa_indah import *

def read(
    SERIAL_PORT: str = '/dev/cu.usbmodem101',  # Update to your device
    BAUD_RATE: int = 115200,
    CSV_FILENAME: str = "sensor_log.csv",
    MAX_POINTS: int = 200  # Number of points to show on the plot
  ):
  
  # === Configuration ===
  SERIAL_PORT = SERIAL_PORT
  BAUD_RATE = BAUD_RATE
  CSV_FILENAME = CSV_FILENAME
  MAX_POINTS = MAX_POINTS

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

  tire_width_arr = []

  def on_key(event):
    if event.key == 'enter':
      global tire_width_arr 

      print("\n================================================================")
      print("Enter key pressed → Running classification...")

      tire_data, num_features = detect_tires_enhanced(tire_width_arr)

      vehicle_type = classify_vehicle_type(tire_data=tire_data)

      print(f"Classification Type: {vehicle_type}")
      ax.set_title(vehicle_type)

      # === Clear the plot ===
      timestamps.clear()
      widths.clear()
      line.set_data([], [])
      ax.relim()
      ax.autoscale_view()
      fig.canvas.draw()
      fig.canvas.flush_events()

      tire_width_arr = []
      print("================================================================\n")

  # === Main Loop ===
  try:
    while True:
      line_serial = ser.readline().decode('utf-8').strip()

      fig.canvas.mpl_connect('key_press_event', on_key)

      if line_serial:
        try:
          ts, d1, d2, width = map(int, line_serial.split(","))
          width = max(0, width)
          print(f"Time: {ts} ms | Sensor1: {d1} mm | Sensor2: {d2} mm | Width: {width} mm")

          tire_width_arr.append(width)

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

        except ValueError:
          print(f"Malformed line: {line_serial}")
  except KeyboardInterrupt:
    print("Stopped by user.")
  finally:
    ser.close()
    csvfile.close()
    plt.ioff()
    plt.show()  # Keep the window open after stopping