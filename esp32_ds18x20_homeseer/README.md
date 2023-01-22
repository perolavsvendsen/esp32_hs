MicroPython implementation of 3 x DS28B20 temperature sensors on an ESP32
that updates corresponding devices in Homeseer.

## Contents
- boot.py
- main.py

## Setup instructions

- Wire the DS18X20 and the LEDs to the ESP32. Instructions:
  https://randomnerdtutorials.com/esp32-ds18b20-temperature-arduino-ide/
  Script assumes DS18B20 conneted to GPIO4 and LEDS to GPIO16 and 17.
- If you use less than 3 sensors, manipulate DEVICES accordingly.
- Flash the ESP32 with MicroPython. Instructions:
  https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
- Download boot.py and main.py to the board, run and confirm wiring. Script should 
  print the three physical adresses of the devices. Copy/paste them into
  DEVICES.
- Run script, monitor and manipulate temperatures one by one, and label the
  sensors.
- Create three devices in Homeseer, note reference IDs and insert them into DEVICES.
- Insert SSID and password, confirm that ESP32 is connecting by monitoring
  the printed network configuration. Confirm that ESP is updating Homeseer
  devices by monitoring device values.

## Troubleshooting
- Value is not received by Homeseer
    - Print the response from HS. It should be a dictionary, and the response
      code should be 200. If not, check device reference.
    - Print the url used, and try it directly with a web browser.
    - Check device settings. Value must be covered by the control.
- Value is shown without decimals in Homeseer
    - In Homeseer, check that decimals is set to 2 in Edit Controls options on the device settings.
