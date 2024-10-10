import serial
import time
import logging

log = logging.getLogger(__name__)

def read_serial(port):
    if not port.inWaiting():
        return None
    try:
        line = port.readline().decode("utf-8").rstrip()
        log.info("read:%s", line)
        if "waiting" in line:
            return None
        values = line.split(",")
        if len(values) != 4:
            return None
        return [int(x) for x in values]
    except Exception as e:
        log.exception(e)
        return None    
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    port = serial.Serial('/dev/ttyUSB0',9600)
    while True:
        time.sleep(1)
        v = read_serial(port)
        if v is None:
            continue
        log.info("%s", v)

