"""Module to control deCONZ over the REST Api"""

import logging
import asyncio
import json

import aiohttp
import async_timeout

from .deconz_sensor import DeCONZSensor
from .deconz_light import DeCONZLight

_LOGGER = logging.getLogger(__name__)

class DeCONZApi:
    """Simple binding for the Lundix SPC Web Gateway REST API."""
    def __init__(self, host, port, api_key):
        """Initialize the web gateway client."""
        self._host = host
        self._port = port
        self._api_key = api_key
        self._ws_port = 0
        self._ws = None
        self._device_list = {'sensors':{}, 'lights':{}, 'groups':{}}

    @asyncio.coroutine
    def load(self):
        """Retrieve all available sensors."""
        data = yield from self.get_data('')

        for dcz_id, data in data['sensors'].items():
            sensor = DeCONZSensor(dcz_id,
                                  name=data['name'],
                                  device_type=data['type'])
            sensor.update(data)
            self._add_device('sensors', dcz_id, sensor)

        for dcz_id, data in data['lights'].items():
            light = DeCONZLight(dcz_id,
                                name=data['name'],
                                device_type=data['type'],
                                state=data['state'],
                                api=self)
            self._add_device('lights', dcz_id, light)
        for dcz_id, data in data['groups'].items():
            group = DeCONZLight(dcz_id,
                                name=data['name'],
                                device_type=data['type'],
                                state=data['state'],
                                api=self)
            self._add_device('groups', dcz_id, group)

        self._ws_port = data['config']['websocketport']
        try:
            from asyncio import ensure_future
        except ImportError:
            from asyncio import async as ensure_future

        ensure_future(self._ws_listen(self._async_process_message))

    def get_devices(self, category):
        """Retrieve all available devices in this category."""
        if category in self._device_list:
            return self._device_list[category]
        else:
            raise AttributeError('Category not supported')

    @asyncio.coroutine
    def set_light(self, light):
        """Retrieve all available sensors."""
        return (yield from self._set_state(light))

    @asyncio.coroutine
    def get_data(self, resource):
        """Get data from the gateway"""
        data = yield from self._call_web_gateway(resource)
        if not data:
            return False

        return data

    def _add_device(self, category, dcz_id, device):
        self._device_list[category][dcz_id] = device

    @asyncio.coroutine
    def _async_process_message(self, message):
        _LOGGER.debug(message)

        devices = self._device_list.get(message['r']).get(message['id'], None)

        if message['e'] == 'changed' and devices:
            for device in devices:
                yield from device.update(message)
        #elif message['e'] == 'added':
        #elif message['e'] == 'deleted' and devices:
        else:
            _LOGGER.warning("Unsuccessful websocket message delivered, ignoring: %s", message)

    @asyncio.coroutine
    def _set_state(self, light):
        action_string = None
        if light.isGroup:
            resource = 'groups'
            action_string = 'action'
        else:
            resource = 'lights'
            action_string = 'state'
        url = 'http://{a}:{b}/api/{c}/{d}/{e}/{f}'.format(a=self._host,
                                                          b=self._port,
                                                          c=self._api_key,
                                                          d=resource,
                                                          e=light.id,
                                                          f=action_string
                                                         )

        data = {}
        data['on'] = light.is_on
        data['transitiontime'] = 0

        if light.is_on: #turn on lights
            data['bri'] = light.brightness
            if light.color_temp is not None:
                data['ct'] = light.color_temp
            elif light.xy_color is not None:
                data['xy'] = light.xy_color

        json_data = json.dumps(data)
        try:
            session = aiohttp.ClientSession()
            with async_timeout.timeout(10):
                action = session.put
                response = yield from action(url, data=json_data)
            if response.status != 200:
                _LOGGER.error("DeConz Gateway returned http "
                              "status %d, response %s.",
                              response.status, (yield from response.text()))
                return False
            result = yield from response.json()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout getting DeConz data from %s.", url)
            return False
        except aiohttp.ClientError:
            _LOGGER.exception("Error getting DeConz data from %s.", url)
            return False
        finally:
            if session:
                yield from session.close()
            if response:
                yield from response.release()
        return result

    @asyncio.coroutine
    def _call_web_gateway(self, resource, use_get=True):
        response = None
        session = None
        url = 'http://{a}:{b}/api/{c}/{d}'.format(a=self._host,
                                                  b=self._port,
                                                  c=self._api_key,
                                                  d=resource)
        try:
            _LOGGER.debug("Attempting to retrieve DeConz data from %s.", url)
            session = aiohttp.ClientSession()
            with async_timeout.timeout(10):
                action = session.get if use_get else session.put
                response = yield from action(url)
            if response.status != 200:
                _LOGGER.error("DeConz Gateway returned http "
                              "status %d, response %s.",
                              response.status, (yield from response.text()))
                return False
            result = yield from response.json()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout getting DeConz data from %s.", url)
            return False
        except aiohttp.ClientError:
            _LOGGER.exception("Error getting DeConz data from %s.", url)
            return False
        finally:
            if session:
                yield from session.close()
            if response:
                yield from response.release()
        _LOGGER.debug("Data from Deconz: %s", result)
        return result

    @asyncio.coroutine
    def _ws_read(self):
        import websockets as wslib

        try:
            if not self._ws:
                url = 'ws://{a}:{b}'.format(a=self._host, b=self._ws_port)
                self._ws = yield from wslib.connect(url)
                yield from self._ws.ping()
                _LOGGER.info("Connected to websocket at %s.", url)
        except Exception as ws_exc:    # pylint: disable=broad-except
            _LOGGER.error("Failed to connect to websocket: %s", ws_exc)
            _LOGGER.error("Failed to connect to websocket: %s", url)
            return

        result = None

        try:
            result = yield from self._ws.recv()
            _LOGGER.debug("Data from websocket: %s", result)
        except Exception as ws_exc:    # pylint: disable=broad-except
            _LOGGER.error("Failed to read from websocket: %s", ws_exc)
            try:
                yield from self._ws.close()
            finally:
                self._ws = None

        return result

    @asyncio.coroutine
    def _ws_listen(self, async_callback):
        try:
            while True:
                result = yield from self._ws_read()

                if result:
                    try:
                        yield from async_callback(json.loads(result))
                    except:    # pylint: disable=bare-except
                        _LOGGER.exception("Exception in callback, ignoring.")
                else:
                    _LOGGER.info("Trying again in 30 seconds.")
                    yield from asyncio.sleep(30)


        finally:
            if self._ws:
                yield from self._ws.close()
