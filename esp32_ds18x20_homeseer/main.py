
"""3 x DS18B20 sensors on ESP32 updating Homeseer devices through HS JSON API.

Temperatures are read from the 3 connected DS18B20 sensors. It reports the
average across X cycles. Example: If amount of cycles is set to 5, script
will collect 5 readings and report the average of those 5.

Script also assumes 2 connected LEDs.

Author: Per Olav Svendsen
License: MIT
Sources: https://RandomNerdTutorials.com, https://docs.micropython.org/

"""

import machine
import onewire
import ds18x20
from time import sleep, sleep_ms
import network
import urequests
import gc

# Constants
DS18X20_PIN = 4  # Pin connected to temperature devices, change if needed
RED_PIN = 16     # Pin connected to red LED, change if needed
GREEN_PIN = 17   # Pin connected to green LED, change if needed

AVERAGE_CYCLES = 5   # how many cycles to average over before sending value

SSID = None  # your SSID. If None, script will not try to connect
WIFIPWD = "your-password-here"  # your password
HOST = "192.xxx.xxx.xxx"  # Homeseer IP adress
PORT = 1234  # Homeseer port

# List of devices connected to the ESP32. Run "initialize()" once to print the
# connected devices, then put corresponding bytestrings into dictionary below.
# Identify each device by manipulating the temperature while watching the
# readings. Recommend to do this without sending values to HS, by printing
# values and monitoring directly.

DEVICES = {
    "Nr 0": {"rom": b"<adress>", "hsdeviceref": 9999},  # device adress, and...
    "Nr 1": {"rom": b"<adress>", "hsdeviceref": 9999},  # ...hs device ref...
    "Nr 2": {"rom": b"<adress>", "hsdeviceref": 9999},  # to write to
}


class LED:
    """Class representation of a connected LED.

    Methods
    -------
    blink(count, interval_ms=200):
        Blinks the LED. Increase blink interval to slow blink down.
    
    """
    
    def __init__(self, pin):
        self.led = machine.Pin(pin, machine.Pin.OUT)
        self.led.value(0) # off
  
    def blink(self, count, interval_ms=200):
        """Blink myself."""
        for i in range(count):
            self.led.value(not self.led.value())
            sleep_ms(interval_ms)


def connect_to_wifi():
    """Connect ESP32 to WiFi using the global settings."""

    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        print(f"Connecting to Wifi: {SSID}")
        sta_if.active(True)
        sta_if.connect(SSID, WIFIPWD)
        while not sta_if.isconnected():
            print("Connecting...")
            RED.blink(1)
            sleep(5)
        GREEN.blink(3)
    
    ip, netmask, gateway, dns = sta_if.ifconfig()
    print(f"IP: {ip}")

    
def read_from_sensors(ds_sensor):
    """Read from the temperature sensors.
    
    Returns:
        readings (dict): Values as dictionary with devices as key
    """
    
    values = {d:[] for d in DEVICES}
    for cycle in range(AVERAGE_CYCLES):
        ds_sensor.convert_temp()
        for d in DEVICES:
            values[d].append(ds_sensor.read_temp(DEVICES[d]["rom"]))
        sleep_ms(750)
    
    # get averages
    readings = {d: (sum(values[d]) / len(values[d])) for d in values}

    for d in DEVICES:
        print(f"{d}: {values[d]} -> {readings[d]}")

    return readings


def initialize():
    """Initializing the temperature sensors.
    
    Returns:
      roms (list): List of found device adresses
      ds_sensor (ds18x20.DS18X20): ds_sensor object
    
    """

    print("initializing sensors...")

    ds_pin = machine.Pin(DS18X20_PIN)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = ds_sensor.scan()

    if not roms:
        RED.blink(1, interval_ms=2000)  # long blink
        raise RuntimeError("No sensors detected!")

    for d in DEVICES:
        if DEVICES[d]["rom"] not in roms:
            RED.blink(3)
            print(f"roms: {roms}")
            raise RuntimeError(f"Device {d} not found!")

    for adress in roms:
        if adress not in [d["rom"] for _, d in DEVICES.items()]:
            RED.blink(4)
            raise RuntimeError(f"Unknown device found: {adress}")

    print("Done!")
    return roms, ds_sensor


def run(roms, ds_sensor):
       
    while True:
     
        # free up memory to avoid OSError
        gc.collect()
        print(f"memory available: {gc.mem_free()}")

        # read
        try:
            readings = read_from_sensors(ds_sensor)
        except Exception:  # catch all. Want to keep trying no matter what.
            print("Error in reading")
            sleep(5)
            continue
  
        # send readings
        if SSID is None:
            print("==================")
            print("NOT SENDING VALUES")
            print("==================")

            continue

        # check if connected
        connect_to_wifi()

        for d in readings:
            hsdeviceref = DEVICES[d]["hsdeviceref"]
            value = readings[d]
            url = f"http://{HOST}:{PORT}/"
            url += "JSON?request=controldevicebyvalue"
            url += f"&ref={hsdeviceref}&value={value}"
            # print(f"url: {url}")
            try:
                response = urequests.get(url)
                # print(response.text)   # <- Print what Homeseer is returning to us, useful for debugging
                # print("response.status_code")  # <- 200 if OK
                GREEN.blink(2)  # write to HS OK
            except OSError as err:
                print(err)
                RED.blink(5)
                continue
            sleep(3)  # some delay to not spam HS
               

def main():

    print("STARTING!")
    print("=========")
    GREEN.blink(10, interval_ms=100)  # ESP has started
    roms, ds_sensor = initialize()
    GREEN.blink(2, interval_ms=500)  # Sensors are OK
    run(roms, ds_sensor)


if __name__ == "__main__":

    # initialize leds
    RED = LED(RED_PIN)
    GREEN = LED(GREEN_PIN)

    # run program
    main()
