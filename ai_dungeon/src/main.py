import serial
import pyautogui

# Replace 'COM3' with your actual port (e.g., '/dev/ttyACM0' or '/dev/tty.usbmodemXXXX')
ser = serial.Serial('/dev/tty.usbmodem143101', 9600)

# Map Arduino output to actual keyboard keys
key_map = {
    "W": "w",
    "A": "a",
    "S": "s",
    "D": "d",
    "SPACE": "space"
}

print("Listening for button presses from Arduino...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print(f"Received: {line}")
        if line in key_map:
            pyautogui.press(key_map[line])
            