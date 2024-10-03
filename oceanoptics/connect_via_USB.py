# import serial



# ser = serial.Serial('WinUSB', 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, xonxoff=False, rtscts=False, dsrdtr=False)

# import seabreeze.spectrometers as sb
# spec = sb.Spectrometer.from_serial_number()
# spec.integration_time_micros(100)
# spec.wavelengths()
# # array([  340.32581   ,   340.70321186,   341.08058305, ...,  1024.84940994,
# #         1025.1300678 ,  1025.4106617 ])
# # spec.intensities()
# # array([  1.58187931e+01,   2.66704852e+04,   6.80208103e+02, ...,
# #          6.53090172e+02,   6.35011552e+02,   6.71168793e+02])

# import seabreeze.cseabreeze as csb
# api = csb.SeaBreezeAPI()
# api.supported_models()
# # [u'FlameNIR', ..., u'Ventana']
# import seabreeze.pyseabreeze as psb
# api = psb.SeaBreezeAPI()
# api.supported_models()

# import seabreeze
# seabreeze.use('pyseabreeze')
# import seabreeze.spectrometers as sb
# # import pyusb
# import usb

# dev = usb.core.find(find_all=True)

# for cfg in dev:
#     print(cfg)

# print(sb.list_devices())


# import seabreeze
# seabreeze.use('pyseabreeze')
# import seabreeze.spectrometers as sb

# spec = sb.Spectrometer.from_serial_number()

# import seabreeze
# seabreeze.use('pyseabreeze')
# import seabreeze.spectrometers as sb

# devices = sb.list_devices()
# print(devices)

# if devices:
#     spec = sb.Spectrometer(devices[0])
#     spec.integration_time_micros(1000)
#     intensities = spec.intensities()
#     print(intensities)
# import usb.core

# # Find all connected USB devices
# dev = usb.core.find(find_all=True)

# # List all USB devices
# for device in dev:
#     print(f"Device found: {device}")


# import usb.core
# import usb.util

# # Find the spectrometer
# dev = usb.core.find(idVendor=0x2457, idProduct=0x100a)

# if dev is None:
#     raise ValueError("Spectrometer not found")


import usb.core
import usb.util

# Find the spectrometer
dev = usb.core.find(idVendor=0x2457, idProduct=0x100a)

if dev is None:
    raise ValueError("Spectrometer not found")

# Set the active configuration. This is required for USB devices.
dev.set_configuration()

# On Windows, there’s no need to detach kernel drivers, so skip this part
# Claim the interface (on Windows this might not be necessary, but safe to include)
usb.util.claim_interface(dev, 0)

# Example of sending a command to the spectrometer
# This is device-specific, the command might vary for your spectrometer.
# You might need to send initialization or integration time settings, 
# consult the Ocean Optics HR2000 documentation.

# Use appropriate endpoint addresses from your descriptor: 
# For example, Endpoint 0x02 is OUT (command to spectrometer)
# Endpoint 0x82 is IN (response from spectrometer)

# Sending a dummy command (modify based on your command set)
# dev.write(0x02, b'COMMAND HERE')
def turn_into_bytes(value):
    return value.to_bytes(2, byteorder='big')

value = 0x05
bye = turn_into_bytes(value)
breakpoint()

def query_serial(dev):
    dev.write(0x05, turn_into_bytes(0x00))
    response = dev.read(0x82, 64)
    return response

# integer to byte conversion
# value = 1000
# value_bytes = value.to_bytes(2, byteorder='big')
resp = query_serial(dev)
print(resp)
# dev.write(0x02, 0x00)
breakpoint()

# Reading response from the spectrometer
# response = dev.read(0x82, 64)  # Read 64 bytes (modify size based on expected response)
# print(response)

# Release the device when done
usb.util.release_interface(dev, 0)
