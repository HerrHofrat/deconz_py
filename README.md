# deconz_py

### Status
Work in progress

### Installation
```
pip3 install deconz_py
```

### History
| Version | Comment |
|---------|---------|
| 1.0.0.dev8 | Make websocket port configurable |
| 1.0.0.dev7 | Added ZHAWater and ZHAAlarm support |
| 1.0.0.dev6 | Fixed color light support |
| 1.0.0.dev5 | Fixed sensor component for not supported sensor types |
| 1.0.0.dev4 | Fixed sensor when state is not available |
| 1.0.0.dev3 | Lights fixed - thx [abmantis](https://github.com/abmantis) |
| 1.0.0.dev2 | Pressure sensor added - thx [tseel](https://github.com/tseel) |
| 1.0.0.dev1 | First version - sensors tested |

### Examples
```
>>> from deconz_py import DeCONZApi
>>>
>>> api = DeCONZApi('192.168.1.16', 80, 8080, 'api_key')
>>> api.load() # loads all devices from the server and sets up a websocket for updates
>>> api.get_devices('category') # returns all devices from a category, or raise an AttributeError if the category is not supported
>>> api.stop() # shuts down the websocket connection to deconz and removes all devices
```

### TODO/Contribute
Contributions and Pull Requests always welcome.

### Contributors
[tseel](https://github.com/tseel)
[abmantis](https://github.com/abmantis)
