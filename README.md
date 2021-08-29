# pyLOOKinRemote
Unofficial Python module for interacting with LOOKin Remote devices, largely using LOOKin's API:

- https://documenter.getpostman.com/view/11774062/SzzkddLg?version=latest#b583e8ee-912c-46db-b294-18578c4333a5

## To Install

1. Download the repository files (or at least "pylookinremote.py").
2. Install Python 3.8 or newer (older versions might work, but not guaranteed).
3. Vanilla Python is fine for most functions, but if you want to use device discovery, install the ["zeroconf"](https://pypi.org/project/zeroconf/) library:
    i. Open a command line interface.
    ii. Run the command `pip install zeroconf`.
        a. Windows: `py -3.8 -m pip install zeroconf`
        b. Linux: `python3.8 -m pip install zeroconf`
4. Download the "pyLOOKinRemote" repository files to your computer, or at least its "pylookinremote.py" file.

## To Uninstall

1. Delete the "pyLOOKinRemote" repository files from your computer.
2. If you installed "zeroconf", you may want to uninstall that as well.
    i. Open a command line interface.
    ii. Run the command `pip uninstall zeroconf`.
        a. Windows: `py -3.8 -m pip uninstall zeroconf`
        b. Linux: `python3.8 -m pip uninstall zeroconf`

## To Use

Use this class to interact with a LOOKin Remote device.  For example:

      import sys
      sys.path.append('/path/to/pyLOOKinRemote
      from pylookinremote import LOOKinRemote

      devs = LOOKinRemote.findInNetwork()
      for dev in devs:
          meteoSensorMeas = dev.sensor('Meteo')
          temp_C = meteoSensorMeas['Temperature']
          temp_F = LOOKinRemote.celsius2Fahrenheit(meteoSensorMeas['Temperature'])
          humidityRel = meteoSensorMeas['Humidity']
          print(f'{dev!s} is reporting: {temp_C}°C/{temp_F:0.1f}°F and {humidityRel}%RH')

This generates the output:

      Starting search for available LOOKinRemote devices...
      ...Device Found at 192.168.0.123...
      ...Device Found at 192.168.0.234...
      ...Search complete!  Found 2 LOOKin Remote devices.
      LOOKinRemote(192.168.0.123) is reporting: 20.7°C/69.3°F and 53.6%RH
      LOOKinRemote(192.168.0.234) is reporting: 21.0°C/69.8°F and 61.3%RH

## Available Methods

Everything is centered around the `LOOKinRemote` class, instantiated either by `LOOKinRemote('192.168.0.123')` or the class method `LOOKinRemote.findInNetwork()`.

I strongly recommend looking at the source code in "pylookinremote.py" for the most accurate documentation, but here is the list at the time of this writing:

### Class `pylookinremote.LOOKinRemote`

`LOOKinRemote.findInNetwork(cls, timeout_sec=10)`
:   Class method.  Searches the network for `timeout_sec` seconds for available LOOKin Remote devices and returns a list of `LOOKinRemote` objects.  Requires that `zeroconf` library be installed.

`LOOKinRemote.celsius2Fahrenheit(temp_C)`
:   Static Method.  Returns `temp_C` in degrees Fahrenheit.

`LOOKinRemote.fahrenheit2Celsius(temp_F)`
:   Static Method.  Returns `temp_F` in degrees Celsius.

`LOOKinRemote('192.168.0.123').device()
:   Returns the "device" information.

`LOOKinRemote('192.168.0.123').deviceSet(name=None, timeVal=None, timezone=None, sensormode=None, bluetoothmode=None)`
:   Sets the "device" values.  `None` parameters will not be modified.

`LOOKinRemote('192.168.0.123').network()`
:   Returns the device's network information.

`LOOKinRemote('192.168.0.123').networkScannedSSIDList()`
:   Returns the network SSID's the device found last time it booted up.

`LOOKinRemote('192.168.0.123').networkSavedSSID()`
:   Returns the device's internal list of saved networks.  Use `networkAdd` and `networkDel` to modify this list.

`LOOKinRemote('192.168.0.123').networkAdd(ssid, password)`
:   Adds the network `ssid` and `password` to the remote's internal list of supported WiFi hotspots.

`LOOKinRemote('192.168.0.123').networkDel(ssid)`
:   Deletes the network `ssid` from the remote's internal list of supported WiFi hotspots.

`LOOKinRemote('192.168.0.123').networkConnect(ssid=None)`
:   Tells the remote to connect to `ssid`, or the strongest available WiFi if `ssid` is `None`.

`LOOKinRemote('192.168.0.123').networkKeepWifi()`
:   Tells the remote to keep the WiFi connection while "sensor mode" is on.

`LOOKinRemote('192.168.0.123').networkRemoteControlStop()`
:   Tells the remote to use the "stop" RemoteControl state.

`LOOKinRemote('192.168.0.123').networkRemoteControlReconnect()`
:   Tells the remote to use the "reconnect" RemoteControl state.

`LOOKinRemote('192.168.0.123').sensorNames()`
:   Returns the remote's available sensors.

`LOOKinRemote('192.168.0.123').sensor(name)`
:   Returns the remote's sensor information.

`LOOKinRemote('192.168.0.123').sensorDump(name, period, duration)`
:   Polls the `name` sensor for `duration` seconds and `period` seconds between calls.  Use `period` of `<=0` seconds to poll as fast as possible.

`LOOKinRemote('192.168.0.123').commands()`
:   Returns the remote's available command classes.

`LOOKinRemote('192.168.0.123').commandEvents(command)`
:   Returns the remote's available events for `command`.

`LOOKinRemote('192.168.0.123').data()`
:   Alias for `LOOKinRemote.remotes` to match the API call.

`LOOKinRemote('192.168.0.123').remotes()`
:   Returns the remote's saved IR remotes.

`LOOKinRemote('192.168.0.123').remoteData(uuid)`
:   Returns the data specific to the remote with the given `uuid`.

`LOOKinRemote('192.168.0.123')._remoteGet(rootData, remoteData)`
:   Returns the appropriate `IRRemote` object for the given data.  `rootData` is the remote's data from "data/" and `remoteData` is the remote's data from "data/<UUID>".

### Class `pylookinremote.LOOKinRemote.IRRemote`

Base class for objects returned by `pylookinremote.LOOKinRemote.remotes()`.  Users will rarely instantiate this class themselves.

`LOOKinRemote.IRRemote.TYPE`
:   `Enum` of possible remote types.

`LOOKinRemote.IRRemote(...).uuid`
:   Attribute.  `str` UUID of the remote.

`LOOKinRemote.IRRemote(...).name`
:   Attribute.  `str` name of the remote.

`LOOKinRemote.IRRemote(...).rType`
:   Attribute.  Value from the enum `LOOKinRemote.IRRemote.TYPES`.

`LOOKinRemote.IRRemote(...).updated`
:   Attribute.  `datetime.datetime` object.

`LOOKinRemote.IRRemote(...).functions`
:   Attribute.  `list` of `str` function names.

### Class `pylookinremote.LOOKinRemote.ACRemote`

Subclass of `pylookinremote.LOOKinRemote.IRRemote` that provides air conditioner/heat pump functions.

`LOOKinRemote.IRRemote.OPERATINGMODE`
:   `Enum` of available operating modes:  `OFF`, `AUTO`, `COOL`, and `HEAT`.

`LOOKinRemote.IRRemote.FANSPEEDMODE`
:   `Enum` of available fan speeds:  `MINIMUM`, `MEDIUM`, `MAXIMUM`, and `AUTO`.

`LOOKinRemote.IRRemote.SWINGMODE`
:   `Enum` of available swing modes.

`LOOKinRemote.IRRemote(...).operatingModeSet(operatingMode)`
:   Tells the device to use operate in `operatingMode`.

`LOOKinRemote.IRRemote(...).tempSet(temp_C)`
:   Tells the device to use target the Celsius temperature `temp_C`.

`LOOKinRemote.IRRemote(...).tempSetF(temp_F)`
:   Tells the device to use target the Fahrenheit temperature `temp_F`.

`LOOKinRemote.IRRemote(...).fanSpeedModeSet(fanSpeedMode)`
:   Tells the device to use `fanSpeedMode`.

`LOOKinRemote.IRRemote(...)._remoteDataSet(remoteData)`
:   Updates this object with the data in `remoteData`.

`LOOKinRemote.IRRemote(...).swingModeSet(swingMode)`
:   Tells the device to use `swingMode`.

`LOOKinRemote.IRRemote(...).statusGet(refresh=False)`
:   Returns the current status of the device.

`LOOKinRemote.IRRemote(...).statusRefresh()`
:   Requests the current status from the device.

`LOOKinRemote.IRRemote(...).statusSet(status)`
:   Modifies the device's status to match `status`.

### Class `pylookinremote.LOOKinRemote.ACRemote.Status`

Class representing a status of the air conditioner/heat pump device.  Users can pass an instance of this object to `LOOKinRemote.IRRemote(...).statusSet(status)`.

`pylookinremote.LOOKinRemote.ACRemote.Status(operatingMode, tempTarget_C, fanSpeedMode, swingMode)`
:   Constructor.

`pylookinremote.LOOKinRemote.ACRemote.Status.fromStatusBytes(cls, statusBytes)`
:   Class method.  Alternate constructor using the status bytes reported by the LOOKin Remote.

`pylookinremote.LOOKinRemote.ACRemote.Status(...).operatingModeSet(operatingMode)`
:   Sets this object's operating mode to `operatingMode`.

`pylookinremote.LOOKinRemote.ACRemote.Status(...).tempTargetSet(tempTarget_C)`
:   Sets this object's target temperature to `tempTarget_C` (Celsius).

`pylookinremote.LOOKinRemote.ACRemote.Status(...).tempTargetSet_F(tempTarget_F)`
:   Sets this object's target temperature to `tempTarget_F` (Fahrenheit).

`pylookinremote.LOOKinRemote.ACRemote.Status(...).toStatusBytes()`
:   Returns the 16-bit integer with the appropriate status bytes for this object.

`pylookinremote.LOOKinRemote.ACRemote.Status(...).fanSpeedModeSet(fanSpeedMode)`
:   Sets this object's fan speed to `fanSpeedMode`.

`pylookinremote.LOOKinRemote.ACRemote.Status(...).swingModeSet(swingMode)`
:   Sets this object's swing mode to `swingMode`.
