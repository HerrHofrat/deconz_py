# deconz_py

### Status
Work in progress, not tested!!

### Installation
```
python3 setup.py install
```

### Examples
```
>>> from deconz_py import DeCONZApi
>>>
>>> api = DeCONZApi('192.168.1.16', 80, 'admin', 'password')
>>> api.load() # loads all devices from the server and sets up a websocket for updates
>>> api.get_devices('category') # returns all devices from a category, or raise an AttributeError if the category is not supported
```

### LICENSE
MIT

### TODO/Contribute
Contributions and Pull Requests always welcome.

