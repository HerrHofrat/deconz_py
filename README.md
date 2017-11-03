# deconz_py

### Status
Work in progress

### Installation
```
pip3 install deconz_py
```

### Examples
```
>>> from deconz_py import DeCONZApi
>>>
>>> api = DeCONZApi('192.168.1.16', 80, 'api_key')
>>> api.load() # loads all devices from the server and sets up a websocket for updates
>>> api.get_devices('category') # returns all devices from a category, or raise an AttributeError if the category is not supported
>>> api.stop() # shuts down the websocket connection to deconz and removes all devices
```

### TODO/Contribute
Contributions and Pull Requests always welcome.

