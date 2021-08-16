"""
    Read and save data from the openQCM microbalance
    by
    Szymon Jakubiak
    Twitter: @SzymonJakubiak
    LinkedIn: https://www.linkedin.com/in/szymon-jakubiak-495442127/
"""

import serial
from datetime import datetime

# Specify serial port
device_port = "COM34"

# Specify output file name, comment and header for data
output_file = "Test_QCM.txt"
comment = "Test QCM"
data_header = "date,time,frequency,temperature" # Separate data columns by commas
data_units = "yyyy.mm.dd,hh:mm:ss:msmsms,Hz,deg.C" # Separate data columns by commas

# Create object for serial port
device_ser = serial.Serial(device_port, baudrate=9600, stopbits=1, parity="N",  timeout=2)
device_ser.flushInput()

# Create data buffer and specify number of consecutive
# measurements to buffer before writing to the file
output_buffer = ""
buffer_len = 100

def quality_check(data):
    """
    Expects string, returns tuple with valid data
    or False when data was invalid
    """
    if data != False:
        if "RAWMONITOR" in data:
            data = data.replace("RAWMONITOR","")
            data = data.split("_")
            frequency = int(data[0])
            temperature = int(data[1]) / 10
            return "{0},{1:.1f}".format(frequency, temperature)
    else:
        return False

def ser_data(ser):
    """
    Expects serial port object as an input, returns data from serial device
    or False when there was no data to read
    """
    # Wait for the begginning of the message
    if ser.inWaiting() > 0:
        data = b""
        last_byte = b""
        # Loop untill the end character was read
        while last_byte != b"\xff":
            last_byte = ser.read()
            data += last_byte
        data = data[:-1].decode().rstrip()
        return quality_check(data)
    else:
        return False

def time_stamp():
    """
    Expects nothing, returns time stamp in format dd:mm:yyyy,hh:mm:ss:msmsms
    """
    date = datetime.now()
    stamp = "{0:4}.{1:02}.{2:02},{3:02}:{4:02}:{5:02}:{6:03.0f}".format(date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond / 1000)
    return stamp

def buffer_to_file(filename, data):
    """
    Expects two strings: filename and data which will be written to the file
    """
    file = open(filename, "a")
    file.write(data)
    file.close()

header = "\n* * * *\n" + comment + "\n* * * *\n"
header += data_header + "\n" + data_units
print(header)
file = open(output_file, "a")
file.write(header + "\n")
file.close()

try:
    while True:
        output = ser_data(device_ser)
        if output != False:
            formatted_output = time_stamp() + "," + output
            print(formatted_output)
            output_buffer += formatted_output + "\n"
            if output_buffer.count("\n") > buffer_len:
                buffer_to_file(output_file, output_buffer)
                output_buffer = ""

except KeyboardInterrupt:
    device_ser.close()
    buffer_to_file(output_file, output_buffer)
    print("Data logging stopped")
