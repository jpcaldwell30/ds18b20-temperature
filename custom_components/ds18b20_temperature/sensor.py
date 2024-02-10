"""Platform for sensor integration."""
from homeassistant.helpers.restore_state import RestoreEntity

import os
import glob
import time

DOMAIN = "ds18b20_temperature"

def setup_platform(hass, config, add_entities, discovery_info=None) -> None:
    """Set up the DS18B20 sensor platform."""
    add_entities([DS18B20Sensor()])

class DS18B20Sensor(RestoreEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'   
        self._state = None
        self._last_valid_state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'DS18B20 Temperature Sensor'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "°F"

    def update(self):
        """Fetch new state data for the sensor."""
        new_state = self._tempcheck()
        if self._last_valid_state is None or abs(float(new_state) - float(self._last_valid_state)) <= 20:
            self._state = new_state
            self._last_valid_state = new_state

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def _tempcheck(self):
        temp_f = 0
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            temp_f = round(temp_f, 2)
        return str(temp_f)
