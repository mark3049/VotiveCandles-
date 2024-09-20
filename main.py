import time
import logging
import serial
import serial.tools.list_ports
import argparse
import leds

log = logging.getLogger(__name__)

LED_Width = 5
LED_Height = 6
LED_Total = LED_Width * LED_Height

def show_power_on(led):
    for y in range(LED_Height):
        led.clear()
        for level in range(0,128,8):
            for x in range(LED_Width):
                led.setXY(x, y, (level, level, level))
            led.show()
            time.sleep(0.1)
    for x in range(LED_Width):
        led.clear()
        for level in range(0, 128, 8):
            for y in range(LED_Height):
                led.setXY(x, y, (level, level, level))
            led.show()
            time.sleep(0.1)

def serial_port_exist():
    for p in list(serial.tools.list_ports.comports()):
        if "ttyUSB0" in p.device:
            log.info("serail port exist %s", p)
            return True
    log.debug("not exist")
    return False


def wait_serial_online(led):
    while not serial_port_exist():
        led.fill((127,0,0))
        led.show()
        time.sleep(1)
        led.fill((0,0,0))
        led.show()
        time.sleep(1)
    

def main(led, argc):
    pass

def parser_opt():
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--debug", action="store_true", default=False, help="enable debug mode")
    p.add_argument("-s", "--skip", action="store_true", default=False, help="skip power on led")
    return p.parse_args()


if __name__ == "__main__":
    argc = parser_opt()
    logging.basicConfig(level=logging.DEBUG if argc.debug else logging.INFO)
    log.debug("opt:%s", argc)
    if argc.debug: 
        led = leds.LEDs_Dummy(LED_Width, LED_Height)
    else:
        led = leds.LEDs(LED_Width, LED_Height)
    try:
        if not argc.skip:
            show_power_on(led)
        wait_serial_online(led)
        
        time.sleep(1)
    except Exception as ex:
        log.exception(ex)
    finally:
        led.clear()
        led.show()