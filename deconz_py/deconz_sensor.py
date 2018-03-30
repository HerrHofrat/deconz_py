"""Module to represent a deCONZ Sensor"""

import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class DeCONZSensor:
    """Represents a sensor based on an DeConz Sensor."""

    ZHATEMPERATURE = 'ZHATemperature'
    ZHAHUMIDITY = 'ZHAHumidity'
    ZHAPRESSURE = 'ZHAPressure'
    ZHALIGHTLEVEL = 'ZHALightLevel'
    ZHASWITCH = 'ZHASwitch'
    ZHAPRESENCE = 'ZHAPresence'
    ZHAOPENCLOSE = 'ZHAOpenClose'
    CLIPSWITCH = 'CLIPSwitch'
    CLIPOPENCLOSE = 'CLIPOpenClose'
    CLIPPRESENCE = 'CLIPPresence'
    CLIPTEMPERATURE = 'CLIPTemperature'
    CLIPHUMIDITY = 'CLIPHumidity'
    CLIPGENERICFLAG = 'CLIPGenericFlag'
    CLIPGENERICSTATUS = 'CLIPGenericStatus'

    def __init__(self, dcz_id, name, device_type):
        """Initialize the sensor device."""
        self._dcz_id = dcz_id
        self._name = name
        self._state = None
        self._config = None
        self._device_type = device_type
        self._unit_of_measurement = None
        self._current_state = None
        self._update_listeners = []

    @asyncio.coroutine
    def update(self, data):
        """Update the state of the device."""

        if 'state' in data:
            try:
                self._state = data['state']
                if self._device_type == self.ZHATEMPERATURE or \
                   self._device_type == self.CLIPTEMPERATURE:
                    current_state = self._state['temperature']/float(100)
                elif self._device_type == self.ZHAHUMIDITY or \
                     self._device_type == self.CLIPHUMIDITY:
                    current_state = self._state['humidity']/float(100)
                elif self._device_type == self.ZHAPRESSURE:
                    current_state = self._state['pressure']
                elif self._device_type == self.ZHALIGHTLEVEL:
                    current_state = round(10 ** (float(self._state['lightlevel'] - 1) / 10000), 0)
                elif self._device_type == self.ZHASWITCH or \
                     self._device_type == self.CLIPSWITCH:
                    current_state = self._state['buttonevent']
                elif self._device_type == self.ZHAPRESENCE or \
                     self._device_type == self.CLIPPRESENCE:
                    current_state = self._state['presence']
                elif self._device_type == self.ZHAOPENCLOSE or \
                     self._device_type == self.CLIPOPENCLOSE:
                    current_state = self._state['open']
                elif self._device_type == self.CLIPGENERICFLAG:
                    current_state = self._state['flag']
                elif self._device_type == self.CLIPGENERICSTATUS:
                    current_state = self._state['status']
                else:
                    _LOGGER.warning(data)
                    current_state = "unknown"
            except KeyError:
                current_state = "unknown"

            self._current_state = current_state
        if 'config' in data:
            self._config = data['config']
            if 'battery' not in self._config:
                self._config['battery'] = 'unknown'
        for update_listener in self._update_listeners:
            yield from update_listener(data)

    def add_update_listener(self, update_listener):
        """update_listener is called as soon as the sensor receives an update"""
        self._update_listeners.append(update_listener)

    def remove_update_listener(self, update_listener):
        """remove an update_listener"""
        self._update_listeners.remove(update_listener)

    @property
    def dcz_id(self):
        """Return the deconz id"""
        return self._dcz_id

    @property
    def name(self):
        """The name of the device."""
        return self._name

    @property
    def state(self):
        """The state of the sensor."""
        return self._state

    @property
    def config(self):
        """The config of the sensor."""
        return self._config

    @property
    def current_state(self):
        """The current state of the sensor."""
        return self._current_state

    @property
    def type(self):
        """The type of the sensor."""
        return self._device_type

    @property
    def attributes(self):
        """Return the device state attributes."""
        attr = {}

        if self._config:
            for key, value in self._config.items():
                attr[key] = value

        if 'battery' not in attr:
            attr['battery'] = "unkown"

        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement
