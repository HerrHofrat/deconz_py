"""Module to represent a deCONZ Light"""

import asyncio

class DeCONZLight:
    """The platform class required by Home Asisstant."""

    COLOR_TEMPERATURE_LIGHT = 'Color temperature light'
    DIMMABLE_LIGHT = 'Dimmable light'
    EXTENDED_COLOR_LIGHT = 'Extended color light'
    LIGHT_GROUP = 'LightGroup'

    def __init__(self, dcz_id, name, state, device_type, api): #pylint: disable=too-many-arguments
        """Initialize a Light."""

        self._dcz_id = dcz_id
        self._name = name
        self._state = state
        self._device_type = device_type
        self._api = api
        group = False
        if self._device_type == self.COLOR_TEMPERATURE_LIGHT:
            current_state = self._state['on']
            reachable = self._state['reachable']
            dimmer = self._state['bri']
            ct_color = self._state['ct']
        elif self._device_type == self.DIMMABLE_LIGHT:
            current_state = self._state['on']
            reachable = self._state['reachable']
            dimmer = self._state['bri']
        elif self._device_type == self.EXTENDED_COLOR_LIGHT:
            current_state = self._state['on']
            reachable = True
            dimmer = self._state['bri']
            ct_color = self._state['ct']
            group = True
        elif self._device_type == self.LIGHT_GROUP:
            current_state = self._state['on']
            reachable = self._state['reachable']
            dimmer = self._state['bri']
            xy_color = self._state['xy']

        self._current_state = current_state
        self._reachable = reachable
        self._dimmer = dimmer
        self._is_group = group
        self._xy_color = xy_color
        self._ct_color = ct_color
        self._update_listeners = []


    @asyncio.coroutine
    def update(self, data):
        """Update the state of the device."""
        if 'state' in data:
            if 'on' in data['state'] and (self._device_type == self.DIMMABLE_LIGHT or
                                          self._device_type == self.COLOR_TEMPERATURE_LIGHT):
                self._current_state = data['state']['on']
            elif 'any_on' in data['state'] and self._device_type == self.LIGHT_GROUP:
                self._current_state = data['state']['any_on']
            elif 'bri' in data['state']:
                self.brightness = data['state']['bri']
            elif 'ct' in data['state']:
                self.color_temp = data['state']['ct']
            #elif 'x' in data:
            #    color_util.color_xy_brightness_to_RGB(self._xy_color[0], 1, 0)
            #    self._xy_color = data['x'],self._xy_color[1]
            #elif 'y' in data:
            #    color_util.color_xy_brightness_to_RGB(self._xy_color[0], 1, 0)
            #    self._xy_color = self._xy_color[0],data['y']

        for update_listener in self._update_listeners:
            yield from update_listener()

    def add_update_listener(self, update_listener):
        """update_listener is called as soon as the sensor receives an update"""
        self._update_listeners.append(update_listener)

    def remove_update_listener(self, update_listener):
        """remove an update_listener"""
        self._update_listeners.remove(update_listener)

    @property
    def xy_color(self):
        """Return the XY color value."""
        return self._xy_color


    @xy_color.setter
    def xy_color(self, value):
        self._xy_color = value

    @property
    def color_temp(self):
        """Return the color temperature value."""
        return self._ct_color

    @color_temp.setter
    def color_temp(self, value):
        self._ct_color = value

    @property
    def dcz_id(self):
        """Return the deconz id"""
        return self._dcz_id

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._dimmer

    @brightness.setter
    def brightness(self, value):
        self._dimmer = value

    @property
    def is_group(self):
        """Return the is_group of the light."""
        return self._is_group


    @property
    def is_on(self):
        """Return true if light is on."""
        return self._current_state

    @property
    def device_class(self):
        """The device class."""
        return self._device_type

    @asyncio.coroutine
    def turn_off(self):
        """Instruct the light to turn off."""
        self._current_state = False
        yield from self._api.set_light(self.is_on, self)

    @asyncio.coroutine
    def turn_on(self):
        """Instruct the light to turn on."""
        self._current_state = True
        yield from self._api.set_light(self.is_on, self)
