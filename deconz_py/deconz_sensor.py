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
    ZHAWATER = 'ZHAWater'
    ZHAALARM = 'ZHAAlarm'
    CLIPSWITCH = 'CLIPSwitch'
    CLIPOPENCLOSE = 'CLIPOpenClose'
    CLIPWATER = 'CLIPWater'
    CLIPALARM = 'CLIPAlarm'
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
        self._current_state = None
        self._ep = None
        self._etag = None
        self._manufacturername = None
        self._modelid = None
        self._swversion = None
        self._uniqueid = None
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
                elif self._device_type == self.ZHAWATER or \
                     self._device_type == self.CLIPWATER:
                    current_state = self._state['water']
                elif self._device_type == self.ZHAALARM or \
                     self._device_type == self.CLIPALARM:
                    current_state = self._state['alarm']
                elif self._device_type == self.CLIPGENERICFLAG:
                    current_state = self._state['flag']
                elif self._device_type == self.CLIPGENERICSTATUS:
                    current_state = self._state['status']
                else:
                    current_state = "unknown"
            except KeyError:
                current_state = "unknown"

            self._current_state = current_state
        if 'config' in data:
            self._config = data['config']
            if 'battery' not in self._config:
                self._config['battery'] = 'unknown'
                
        if 'ep' in data:
            self._ep = data['ep']
        if 'etag' in data:
            self._etag = data['etag']
        if 'manufacturername' in data:
            self._manufacturername = data['manufacturername']
        if 'modelid' in data:
            self._modelid = data['modelid']
        if 'swversion' in data:
            self._swversion = data['swversion']
        if 'uniqueid' in data:
            self._uniqueid = data['uniqueid']
        
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
    def ep(self):
        """The ep of the sensor."""
        return self._ep

    @property
    def etag(self):
        """The etag of the sensor."""
        return self._etag

    @property
    def manufacturername(self):
        """The manufacturername of the sensor."""
        return self._manufacturername

    @property
    def modelid(self):
        """The modelid of the sensor."""
        return self._modelid

    @property
    def swversion(self):
        """The swversion of the sensor."""
        return self._swversion

    @property
    def uniqueid(self):
        """The uniqueid of the sensor."""
        return self._uniqueid
