# blissclient

A python client for the BLISS REST API, the high-level client is fully typed ready for auto-completion in any modern IDE.

## Getting Started

Set the `BLISSAPI_URL`

```bash
export BLISSAPI_URL=http://localhost:5000
```

Then:

```python
from blissclient import BlissClient

client = BlissClient()

omega = client.hardware.get("omega")
print(omega.position)

future = omega.move(100)
# Wait for the call to temrinate, blocking
future.get()
```

Execute calls in the session:

```python
import time
from blissclient import BlissClient, get_object

client = BlissClient()

test_session = client.session
future = test_session.call("ascan", get_object("omega"), 0, 10, 10, 0.1, get_object("diode"))

# Ask for the current future state
print(future.state)

# Block until terminated
result = future.get()

# The redis scan key, can be used with `blissdata``
print(result["key"])
```

`get_object("<name>")` are translated to the relevant beacon objects.

See the test suite for more examples.

# Events

Events are propagated via a websocket using socket.io. blissclient provides a helper function to create connect functions to instantiate the socket.io connection in either threaded or asyncio forms:

```python
connect = self._client.create_connect()
connect()

connect = self._client.create_connect(async_client=True)
await connect()
```

This function should be run somewhere in the background to ensure event reception. After that objects will be set in evented mode to limit polling.

The client can then subscribe to hardware object events:

```python
omega = client.hardware.get("omega")

def property_event(data: dict[str, any]):
    for key, value in data.items():
        # for example position
        logger.info(f"property event key=`{key}` value=`{value}`")

def online_event(online: bool):
    logger.info(f"onine event {online}")

def locked_event(reason: str):
    logger.info(f"locked event {reason}")

omega.subscribe("property", property_event)
omega.subscribe("online", online_event)
omega.subscribe("locked", locked_event)
```

Events also allow stdout to be captured from a session call:

```python
connect = client.create_connect(async_client=True)
task = asyncio.create_task(connect())

future = test_session.call(
    "ascan",
    get_object("robx"),
    0,
    5,
    5,
    0.2,
    get_object("diode1"),
    in_terminal=True,
    emit_stdout=True,
)

response = future.get()
print(future.stdout)
```

# Future API

The `future` returned by each call tries to emulate a celery future.

```python
future = test_session.call(...)

# Any progress if the task supports it
future.progress

# Assume the called function returns a bliss `Scan` object
future = test_session.call(
    "ascan",
    ...
    has_scan_factory=True,
)

# Wait for the scan to start
progress = future.wait_scan()

# Now access the bliss `Scan` key that can be used with blissdata
print(progress["scan"]["key"])


# Ask for the current state (a single REST call)
future.state

# Blocking until terminated (polls the REST API in the background)
# default `monitor_interval` = 5s
future.get(monitor_interval=1)

# Kill the current task
future.kill()

# If socketio was connected and the call requested `emit_stdout=True`
print(future.stdout)
```
