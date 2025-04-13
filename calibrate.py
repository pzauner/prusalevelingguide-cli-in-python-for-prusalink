import serial
import time
import argparse
import ast

# Define the serial port for your printer
port = "/dev/ttyAMA0"  # Adjust this if necessary, based on your setup

screw_pitch = 0.5

def connect_to_printer(port, baudrate=115200, timeout=5):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Wait for the connection to establish
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to printer: {e}")
        return None

def send_gcode(ser, command):
    if ser:
        ser.write((command + '\n').encode())
        response = []
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode().strip()
                if line:
                    response.append(line)
                    if line == "ok":  # Wait for the printer to acknowledge completion
                        break
            else:
                time.sleep(0.1)

        return response
    else:
        print("Serial connection not established.")
        return []

def parse_mesh_data(response):
    # Extract floating-point numbers from the response
    points = []
    for line in response:
        if line and not line.startswith("echo:busy:"):
            try:
                # Split the line by spaces and convert to floats
                points.extend([float(x) for x in line.split()])
            except ValueError:
                continue  # Ignore lines that don't contain numbers
    return points

def read_filament_profiles(filename='filaments.txt'):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            filament_profiles = ast.literal_eval(data)
            return filament_profiles
    except (FileNotFoundError, SyntaxError) as e:
        print(f"Error reading filament profiles: {e}")
        return {}

def preheat(ser, filament_type, filament_profiles):
    if filament_type in filament_profiles:
        profile = filament_profiles[filament_type]
        bed_temp = profile.get('bed temp', 0)
        nozzle_temp = profile.get('nozzle temp', 0)
        send_gcode(ser, f"M140 S{bed_temp}")  # Set bed temperature
        send_gcode(ser, f"M104 S{nozzle_temp}")  # Set nozzle temperature
        send_gcode(ser, f"M190 S{bed_temp}")  # Wait for bed temperature to reach target
        send_gcode(ser, f"M109 S{nozzle_temp}")  # Wait for nozzle temperature to reach target
    else:
        print(f"Filament type '{filament_type}' not found in profiles.")

def convert_distance_to_fractional_turns(distance):
    rat = round(distance / screw_pitch, 1)
    direction = "CW" if rat > 0 else "CCW"
    return f"{abs(rat)} {direction}"

def convert_distance_to_degrees(distance):
    deg = round((distance / screw_pitch) * 360)
    direction = "CCW" if deg < 0 else "CW"
    return f"{abs(deg)}°{direction}"

def format_7x7_grid(points):
    grid_size = 7
    output = "Raw 7x7 Grid Values:\n"
    for i in range(grid_size):
        # Format each point with 3 decimal places
        row = "\t".join(f"{points[i * grid_size + j]:.3f}" for j in range(grid_size))
        output += row + "\n"
    return output

def format_3x3_screw_adjustments(points):
    center = points[24]  # Center point
    
    # Map points and subtract center value
    screw_indices = [0, 3, 6, 21, 27, 42, 45, 48]
    offsets = [round(x - center, 3) for x in [points[i] for i in screw_indices]]
    
    # Unpack values
    top_left, top_middle, top_right, middle_left, middle_right, bottom_left, bottom_center, bottom_right = offsets

    output = "3x3 Screw Adjustments:\n"

    output += "Raw values:\n"
    output += f"{top_left}\t{top_middle}\t{top_right}\n"
    output += f"{middle_left}\t0.00\t{middle_right}\n"
    output += f"{bottom_left}\t{bottom_center}\t{bottom_right}\n"

    output += "\nDegrees:\n"
    output += f"{convert_distance_to_degrees(top_left)}\t{convert_distance_to_degrees(top_middle)}\t{convert_distance_to_degrees(top_right)}\n"
    output += f"{convert_distance_to_degrees(middle_left)}\t0\t{convert_distance_to_degrees(middle_right)}\n"
    output += f"{convert_distance_to_degrees(bottom_left)}\t{convert_distance_to_degrees(bottom_center)}\t{convert_distance_to_degrees(bottom_right)}\n"

    return output

def main():
    parser = argparse.ArgumentParser(description="3D Printer Calibration Script")
    parser.add_argument('--preheat', type=str, help='Specify the filament type for preheating')
    args = parser.parse_args()

    filament_profiles = read_filament_profiles()
    ser = connect_to_printer(port)

    if ser:
        if args.preheat:
            preheat(ser, args.preheat, filament_profiles)

        # Send G-code commands for mesh bed leveling
        send_gcode(ser, "G28 W")  # Home all without mesh bed level
        send_gcode(ser, "M400")   # Wait for current moves to finish
        send_gcode(ser, "G80")    # Perform mesh bed leveling
        response = send_gcode(ser, "G81")  # Check mesh leveling results

        # Parse and calculate adjustments
        mesh_data = parse_mesh_data(response)
        if mesh_data:
            print(f"Num X,Y: {int(len(mesh_data) ** 0.5)},{int(len(mesh_data) ** 0.5)}")
            print("Measured points:")
            print(format_7x7_grid(mesh_data))  # Print the raw 7x7 grid
            print(format_3x3_screw_adjustments(mesh_data))  # Print the 3x3 screw adjustments

        # Move the printer head out of the way for manual adjustments
        send_gcode(ser, "G1 Z60 Y210 X70 F6000")  # Move Z up, Y back, and X +70mm so that the printer head is not in the way of the 0.0 screw.


        ser.close()
    else:
        print("Failed to connect to the printer.")

if __name__ == '__main__':
    main()