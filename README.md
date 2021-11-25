# pyLOOKinRemote
Unofficial Python module for interacting with LOOKin Remote devices, largely using LOOKin's API:

- https://look-in.club/en/support/api

## To Use

Use this class to interact with a LOOKin Remote device.  For example:

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

## To Install

1. Install from PyPI using `pip`:
    - Linux:  `pip install pyLOOKinRemote`
    - Windows:  `py -m pip install pyLOOKinRemote`

## To Uninstall

1. Uninstall using `pip`:
    - Linux:  `pip uninstall pyLOOKinRemote`
    - Windows:  `py -m pip uninstall pyLOOKinRemote`

## Auxiliary Data File

On-device function storage doesn't appear to be working right now, so this
script allows you to save and load function data through a JSON file instead.

## Learning Remote Commands

This module offers an automated IR command learning method.

      from pylookinremote import LOOKinRemote

      auxDataFilePath='./auxData.json'  #File to save function data in.
      dev = LOOKinRemote('192.168.0.123', auxDataFilePath)
      remoteUUID = '1234'  #ID of the IR remote on the LOOKin Remote.
      newIRFunction = IRRemoteFunction.fromIRSensor(dev, 'myNewFunctionName')  #The "Learn IR Command" routine.
      if newIRFunction is not None:  #Capture was successful.
          try:  #The LOOKin Remote can get unstable during captures of long IR sequences, throwing connection errors.
              remote = dev.remoteFromUUID(remoteUUID)
              remote.functionUpdate(newIRFunction)
          except:  #Dump the JSON on error so it can be manually added and all that effort isn't lost.
              print(f'ERROR while saving function:  newIRFunction = {newIRFunction.toJSON()!r}')

Executing the above script will generate something like the following (IR sequences have been shortened for this example):

      Learning new IR remote function 'myNewFunctionName'...
      ...Please trigger the desired IR remote function repeatedly on the target LOOKin Remote...
      Running sensor dump for 300 seconds...
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': '00', 'Raw': '470 -390 470 -390 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '0'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1630995857'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 440 -420 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1631003614'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1631009781'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      Connection Reset!  The device might be restarting due to a crash.
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 440 -420 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1631017192'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      Connection Reset!  The device might be restarting due to a crash.
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': '00', 'Raw': '470 -390 440 -420 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '0'}
      _get - url='http://192.168.0.123/sensors/IR'
      Connection Reset!  The device might be restarting due to a crash.
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '3510 -1690 470 -1260 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1630870829'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      Connection Reset!  The device might be restarting due to a crash.
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': '00', 'Raw': '470 -390 470 -390 470 -390 470 -390 440 -410 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '0'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 470 -390 470 -390 440 -410 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1630892222'}
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      _get - url='http://192.168.0.123/sensors/IR'
      {'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 470 -390 470 -390 440 -420 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1630900942'}
      ...Sensor dump finished.  10 signals detected.
      ...capture complete!  You can stop triggering the IR remote.
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 584<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 584<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 100% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 100% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 584<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 100% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 584<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 584<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 38% SIMILAR; LENGTH 144<=>308 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 100% SIMILAR; LENGTH 144<=>144 IS SAME; MATCH!
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 144<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 144<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 38% SIMILAR; LENGTH 308<=>144 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 308<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 41% SIMILAR; LENGTH 308<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 144<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 24% SIMILAR; LENGTH 144<=>584 IS DIFFERENT; NOT A MATCH
      IR COMMANDS ARE 100% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!
      Found 2 groups of commands.



      SUCCESS capturing command!  Command selected with 6 matches out of 10 total signals detected.
      _get - url='http://192.168.0.123/data'
      _get - url='http://192.168.0.123/data/2345'
      _get - url='http://192.168.0.123/data/3456'
      _get - url='http://192.168.0.123/data/1234'
      _get - url='http://192.168.0.123/data/4567'
      Error writing function to device; saving to auxiliary data file...
      ...Done!
      _get - url='http://192.168.0.123/data/1234'

What's happening here is that the Python code is monitoring the data being captured by the LOOKin Remote's IR sensor and then processes the data to generate what it believes is the desired remote function.

- `Running sensor dump for 300 seconds...`
    - Monitors the LOOKin Remote's IR sensor for 5 minutes or until 10 IR signals have been captured.
- `_get - url='http://192.168.0.123/sensors/IR'`
    - This is a debug message printed every time the script talks to the device.  It is currently enabled to help the user visually see that the device is or is not responding.
- `Connection Reset!  The device might be restarting due to a crash.`
    - Indicates the communications with the LOOKin Remote failed, either from a timeout or from the connection being reset.  Usually, this is caused by the LOOKin Remote becoming unstable; long IR sequences seemed to be especially good at causing the LOOKin Remote grief.
- `{'IsRepeated': '0', 'Protocol': 'FF', 'Raw': '470 -390 470 -390 470 -390 470 -390 470 -390 470 -45000', 'RepeatPause': '0', 'RepeatSignal': '', 'Signal': '0', 'Updated': '1630995857'}`
    - The raw IR sensor data received from the LOOKin Remote.  The length of this will vary significantly depending on the type of command/remote you're using.
- `...Sensor dump finished.  10 signals detected.` & `...capture complete!  You can stop triggering the IR remote.`
    - Indicates the IR sensor monitoring has concluded, either due to 300 seconds having passed or 10 IR signals found.
- `IR COMMANDS ARE 99% SIMILAR; LENGTH 584<=>584 IS SAME; MATCH!` & `IR COMMANDS ARE 24% SIMILAR; LENGTH 584<=>144 IS DIFFERENT; NOT A MATCH`
    - This is the debug output of the IR signal correlation routine.  Similar/identical IR signals are grouped together to help the script determine what is the most likely IR signal.
- `Found 2 groups of commands.`
    - Indicates how many groupings of similar commands were found.  In this case, the Python code has determined that 2 different types of IR commands were read by the IR sensor.  Groups below a certain size (e.g. just 1 signal) will be ignored.
- `SUCCESS capturing command!  Command selected with 6 matches out of 10 total signals detected.`
    - Indicates success/failure in identifying the IR command.  `10` indicates the total number of commands captured, and `6` indicates how many signals out of those `10` were similar.  Ultimately, the IR command selected is the one with the largest grouping.
- `_get - url='http://192.168.0.123/data'` & `_get - url='http://192.168.0.123/data/1234'`
    - Debug statements from the script trying to write the function to the LOOKin Remote.
- `Error writing function to device; saving to auxiliary data file...`
    - Indicates the writing of the function to the LOOKin Remote failed.  This is usually due to a `500 Internal Server Error` being returned by the LOOKin Remote in response to the "Create Function" call.
    - As indicated, if you supplied an auxiliary data file then the remote command will be stored there instead.
- `...Done!`
    - Indicates the process of storing the learned IR command has completed.

## Using Remote Commands

This module can trigger remote functions both on the LOOKin Remote device and stored in an auxiliary data file:

      from pylookinremote import LOOKinRemote

      auxDataFilePath='./auxData.json'  #File that saved function data is in.
      dev = LOOKinRemote('192.168.0.123', auxDataFilePath)
      remoteUUID = '1234'  #ID of the IR remote on the LOOKin Remote.
      remoteFunctionName = 'myFunctionName'  #`str` name of the function to trigger.
      remote = dev.remoteFromUUID(remoteUUID)
      remote.functionTrigger(remoteFunctionName)

Functions defined on the LOOKin Remote device will take precedence over the auxiliary data file.

## Available Methods

Everything is centered around the `LOOKinRemote` class, instantiated either by `LOOKinRemote('192.168.0.123')` or the class method `LOOKinRemote.findInNetwork()`.

I strongly recommend using `help(LOOKinRemote)` in Python and/or looking at the source code in "pylookinremote.py" for the most accurate documentation, but here is the list at the time of this writing:

### Class `pylookinremote.LOOKinRemote`

The core class.  Each instance of this object represents a single LOOKin Remote device.

The most common way to get these objects is either by:

      auxDataFilePath='./auxData.json'  #File that saved function data is/will-be in.
      remotes = LOOKinRemote.findInNetwork(auxDataFilePath=auxDataFilePath)  #`list` of `LOOKinRemote` objects.
      remote = remotes[0]

...or by:

      auxDataFilePath='./auxData.json'  #File that saved function data is/will-be in.
      ipOrDNSAddr = '192.168.0.123'
      remote = remote.LOOKinRemote(ipOrDNSAddr, auxDataFilePath)  #Single `LOOKinRemote` object.

#### Public Attributes/Methods

`temp_F = LOOKinRemote.celsius2Fahrenheit(temp_C)`
:   Static Method.  Returns `temp_C` in degrees Fahrenheit.

`temp_C = LOOKinRemote.fahrenheit2Celsius(temp_F)`
:   Static Method.  Returns `temp_F` in degrees Celsius.

`remotes = LOOKinRemote.findInNetwork(timeout_sec=10, auxDataFilePath=None)`
:   Class method.  Searches the network for `timeout_sec` seconds for available LOOKin Remote devices and returns a list of `LOOKinRemote` objects.  Requires that `zeroconf` library be installed.  If `auxDataFilePath` is defined, a file will be opened/created there to store/retrieve IR function data.

`remote = LOOKinRemote('192.168.0.123', auxDataFilePath=None)
:   Constructor accepting an `str` IP or DNS address.  If `auxDataFilePath` is defined, a file will be opened/created there to store/retrieve IR function data.

`remote.api_*_DEL`
:   Methods that map directly to LOOKin Device API `DEL` calls as defined by LOOKin:  https://look-in.club/en/support/api .

`remote.api_*_GET`
:   Methods that map directly to LOOKin Device API `GET` calls as defined by LOOKin:  https://look-in.club/en/support/api .

`remote.api_*_POST`
:   Methods that map directly to LOOKin Device API `POST` calls as defined by LOOKin:  https://look-in.club/en/support/api .

`remote.api_*_PUT`
:   Methods that map directly to LOOKin Device API `PUT` calls as defined by LOOKin:  https://look-in.club/en/support/api .

`remote.commandEventLocalRemote(uuid, functionCode, signalID=0xFF)`
:   Triggers a "localremote" command event with `functionCode` and `signalID`.

`remote.commandEventNEC1(uuid, functionCode, signalID=0xFF)`
:   Triggers an "NEC1" command event with `signal`.

`remote.commandEventNECX(signal)`
:   Triggers an "NECx" command event with `signal`.

`remote.commandEventProntoHEX(signal)`
:   Triggers a "ProntoHEX" command event.

`remote.commandEventRaw(signal, freqCarrier_Hz=38000)`
:   Triggers a "raw" command event.

`remote.commandEvents(command)`
:   Returns the remote's available events for `command`.

`remote.commandEventSaved(signalID)`
:   Triggers a "saved" command event with `signalID`.

`remote.commands()`
:   Returns the remote's available command classes.

`remote.remoteCreate(name, irRemoteType, extra='', uuid=None)`
:   Creates a new IR remote definition on the device.

`remote.remoteFromUUID(uuid)`
:   Returns a new `IRRemote` object for the remote matching `uuid`.

`remote.remotes()`
:   Returns the remote's saved IR remotes.

`remote.remotesData()`
:   Returns the general data for all saved remotes.

`remote.remotesDelete(uuids)`
:   Deletes the IR remotes `uuids` from the device.

`remote.remotesDeleteAll(*, yesIWantToDoThis=False)`
:   Deletes all saved IR remotes from the device.

`remote.sensor(name)`
:   Returns the remote's sensor information.

`remote.sensorDump(name, period, duration, maxSignals=None)`
:   Polls the `name` sensor for `duration` seconds and `period` seconds between calls.  Terminates early if `maxSignals` have been received.  Returns a `list` of data for all the non-empty captures (only "IR" sensor supported right now).

`remote.sensorNames()`
:   Returns the remote's available sensors.

### Class `pylookinremote.IRRemote`

Base class for objects returned by `pylookinremote.LOOKinRemote.remotes()`.  Users will rarely instantiate this class themselves.

The most common way to get these objects is either by:

      irRemotes = remote.remotes()  #`list` of `IRRemote` objects.

...or by:

      uuid = '1234'
      irRemote = remote.remoteFromUUID(uuid)  #Single `IRRemote` object, or `None` if `uuid` didn't match.

#### Public Attributes/Methods

`irRemote.uuid`
:   `str` UUID of the remote on the LOOKin Remote device.

`irRemote.name`
:   `str` name of the remote on the LOOKin Remote device.

`irRemote.rType`
:   Type of the remote as an instance of `pylookinremote.IRRemote.TYPE`.

`irRemote.updated`
:   `datetime.datetime` object reprenting the last time the remote was modified on the LOOKinRemote device.

`irRemote.functions`
:   `dict` mapping `str` function names to `pylookinremote.IRRemoteFunction` objects.

`irRemote = pylookinremote.IRRemote(lookinRemote, uuid, rootData=None, auxDataFilePath=None)`
:   Constructor initializing the object.  `lookinRemote` is a `LOOKinRemote` object.  `uuid` is the `str` UUID of this remote on `lookinRemote`.

`irRemote.details()`
:   Returns this remote's details.

`irRemote.delete()`
:   Deletes this IR remote from the device.

`irRemote.functionCreate(irRemoteFunction)`
:   Creates a function on the remote device using the data in `irRemoteFunction`.  `irRemoteFunction` should be a `pylookinremote.IRRemoteFunction` object.

`irRemote.functionDelete(functionName)`
:   Deletes the function `functionName` from the device.

`irRemote.functionExists(functionName)`
:   Returns `True` if a function named `functionName` is defined.

`irRemote.functionTrigger(functionName)`
:   Triggers the function `functionName`.  The exact behavior depends on the type of function.

`irRemote.functionUpdate(irRemoteFunction, upsert=True)`
:   Updates the function definition for `irRemoteFunction`, a `pylookinremote.IRRemoteFunction` object.  If `upsert` is true, will create the function if it doesn't currently exist.

`irRemote.toJSON()`
:   Returns a JSON-compatible data structure that represents this object.

`irRemote.update(name=None, irRemoteType=None, extra=None)`
:   Updates the IR remote definition for `uuid` on the device.  `None` values will be unmodified.

### Class `pylookinremote.IRRemote.TYPE`

Enum of possible IR Remote Types.

#### Public Attributes/Methods

`pylookinremote.IRRemote.TYPE.CUSTOM`
:   `CUSTOM` remote type.

`pylookinremote.IRRemote.TYPE.TV`
:   `TV` remote type.

`pylookinremote.IRRemote.TYPE.MEDIA`
:   `MEDIA` remote type.

`pylookinremote.IRRemote.TYPE.LIGHT`
:   `LIGHT` remote type.

`pylookinremote.IRRemote.TYPE.HUMIDIFIER_DEHUMIDIFIER`
:   `HUMIDIFIER_DEHUMIDIFIER` remote type.

`pylookinremote.IRRemote.TYPE.AIRPURIFIER`
:   `AIRPURIFIER` remote type.

`pylookinremote.IRRemote.TYPE.ROBOVACUUMCLEANER`
:   `ROBOVACUUMCLEANER` remote type.

`pylookinremote.IRRemote.TYPE.DATADEVICEFAN`
:   `DATADEVICEFAN` remote type.

`pylookinremote.IRRemote.TYPE.AIRCONDITIONER`
:   `AIRCONDITIONER` remote type.  Remotes of this type should always be instances of `pylookinremote.ACRemote`, a subclass of `pylookinremote.IRRemote`.

### Class `pylookinremote.ACRemote`

Subclass of `pylookinremote.IRRemote` that provides air conditioner/heat pump functions.

Obtain the same way as `pylookinremote.IRRemote` objects:

      irRemotes = remote.remotes()  #Any remotes with type `pylookinremote.IRRemote.TYPE.AIRCONDITIONER` will `ACRemote` objects instead of standard `IRRemote` objects.
      acRemotes = [irRemote for irRemote in irRemotes if isinstance(irRemote, pylookinremote.ACRemote]

...or by:

      uuid = '1234'
      irRemote = remote.remoteFromUUID(uuid)  #Will be an `ACRemote` object if the target remote has the type `pylookinremote.IRRemote.TYPE.AIRCONDITIONER`.
      acRemote = irRemote if isinstance(irRemote, pylookinremote.ACRemote) else None

#### Public Attributes/Methods

`acRemote.operatingModeSet(operatingMode)`
:   Tells the device to switch operating mode to `operatingMode`.  `operatingMode` should be an instance of `pylookinremote.ACRemote.OPERATINGMODE`.

`acRemote.tempSet(temp_C)`
:   Tells the device to target the Celsius temperature `temp_C`.

`acRemote.tempSetF(temp_F)`
:   Tells the device to target the Fahrenheit temperature `temp_F`.

`acRemote.fanSpeedModeSet(fanSpeedMode)`
:   Tells the device to use `fanSpeedMode`.  `fanSpeedMode` should be an instance of `pylookinremote.ACRemote.FANSPEEDMODE`.

`acRemote.swingModeSet(swingMode)`
:   Tells the device to use `swingMode`.  `swingMode` should be an instance of `pylookinremote.ACRemote.SWINGMODE`.

`acRemote.statusGet(refresh=False)`
:   Returns the current status of the device.  Will return the cached state unless `refresh` is `True`.

`acRemote.statusRefresh()`
:   Requests the current status from the device.

`acRemote.statusSet(status)`
:   Modifies the device's status to match `status`.  `status` should be an instance of `pylookinremote.ACRemote.Status`.

### Class `pylookinremote.ACRemote.OPERATINGMODE`

Enum of available air conditioner/heat pump operating modes.

#### Public Attributes/Methods

`pylookinremote.ACRemote.OPERATINGMODE.OFF`
:   Air conditioner is off.

`pylookinremote.ACRemote.OPERATINGMODE.AUTO`
:   Air conditioner is on auto.

`pylookinremote.ACRemote.OPERATINGMODE.COOL`
:   Air conditioner is cooling.

`pylookinremote.ACRemote.OPERATINGMODE.HEAT`
:   Air conditioner is heating.

### Class `pylookinremote.ACRemote.FANSPEEDMODE`

Enum of available air conditioner/heat pump fan speed modes.

#### Public Attributes/Methods

`pylookinremote.ACRemote.FANSPEEDMODE.MINIMUM`
:   Air conditiner fan speed is at minimum speed.

`pylookinremote.ACRemote.FANSPEEDMODE.MEDIUM`
:   Air conditiner fan speed is at a moderate speed.

`pylookinremote.ACRemote.FANSPEEDMODE.MAXIMUM`
:   Air conditiner fan speed is at maximum speed.

`pylookinremote.ACRemote.FANSPEEDMODE.AUTO`
:   Air conditioner fan speed is automatic.

### Class `pylookinremote.ACRemote.SWINGMODE`

Enum of available air conditioner/heat pump diffuser swing modes.

#### Public Attributes/Methods

No modes appear to be working right now (at least for my devices), so all are marked as `UNDEFINED`.

### Class `pylookinremote.ACRemote.Status`

Class representing a status of the air conditioner/heat pump device.

This is typically obtained by:

      acStatus = acRemote.statusGet()

#### Public Attributes/Methods

`acStatus.operatingMode`
:   Instance of `pylookinremote.ACRemote.OPERATINGMODE`.

`acStatus.tempTarget_C`
:   Target temperature in degrees Celsius.

`acStatus.tempTarget_F`
:   Target temperature in degrees Fahrenheit.

`acStatus.fanSpeedMode`
:   Instance of `pylookinremote.ACRemote.FANSPEEDMODE`.

`acStatus.swingMode`
:   Instance of `pylookinremote.ACRemote.SWINGMODE`.

`acStatus = pylookinremote.ACRemote.Status(operatingMode, tempTarget_C, fanSpeedMode, swingMode)`
:   Constructor.

`acStatus = pylookinremote.ACRemote.Status.fromStatusBytes(statusBytes)`
:   Class method.  Creates an instance of this class using the data contained in `statusBytes`.

`acStatus.operatingModeSet(operatingMode)`
:   Sets this object's operating mode to `operatingMode`.

`acStatus.tempTargetSet(tempTarget_C)`
:   Sets this object's target temperature to `tempTarget_C` (Celsius).

`acStatus.tempTargetSet_F(tempTarget_F)`
:   Sets this object's target temperature to `tempTarget_F` (Fahrenheit).

`acStatus.toStatusBytes()`
:   Returns the 16-bit integer with the appropriate status bytes for this object.

`acStatus.fanSpeedModeSet(fanSpeedMode)`
:   Sets this object's fan speed to `fanSpeedMode`.

`acStatus.swingModeSet(swingMode)`
:   Sets this object's swing mode to `swingMode`.

### Class `pylookinremote.IRRemoteFunction`

Class representing a function of an IR Remote.

This is typically obtained by:

      irFunctions = irRemote.functions()
      irFunction = irFunctions['myFunctionName']

#### Public Attributes/Methods

`irFunction.name`
:   `str` name of the function.

`irFunction.functionType`
:   Type of the function as an instance of `pylookinremote.IRRemoteFunction.TYPE`.

`irFunction.irCommands`
:   `tuple` of `pylookinremote.IRRemoteCommand` objects.  `None` indicates the commands are stored on the LOOKin Remote device.

`irFunction = pylookinremote.IRRemoteFunction.fromJSON(jsonData)`
:   Static method.  Creates a new `IRRemoteFunction` object from the given `jsonData`.

`irFunction = pylookinremote.IRRemoteFunction.fromIRSensor(lookinRemote, functionName, functionType=TYPE.SINGLE)`
:   Static method.  Creates/"Learns" a new `IRRemoteFunction` object from IR sequences detected by the given `lookinRemote`'s IR sensor.  This is a function that requires guided user interaction with the LOOKin Remote device.

`irFunction = pylookinremote.IRRemoteFunction(functionName, irRemoteCommands, functionType=TYPE.SINGLE)`
:   Constructor.  `functionName` should be a `str` name for the function.  `irRemoteCommands` should be either an iterable of `IRRemoteCommand` objects or a single `IRRemoteCommand` object.  `functionType` should be a value from `IRRemoteFunction.TYPE`.

`irFunction.toJSON()`
:   Returns this object serialized into a JSON-compatible data structure.

`irFunction.trigger(lookinRemote)`
:   Triggers this function on the given `lookinRemote`.

### Class `pylookinremote.IRRemoteCommand.TYPE`

Enum of possible IR Remote Function types.

#### Public Attributes/Methods

`pylookinremote.IRRemoteFunction.TYPE.SINGLE`
:   `SINGLE` function type.

`pylookinremote.IRRemoteFunction.TYPE.TOGGLE`
:   `TOGGLE` remote type.

### Class `pylookinremote.IRRemoteCommand`

Base class for IR Remote Commands.  This is not useful until it is subclassed.

This is typically obtained by:

      irFunctions = irRemote.functions()
      irFunction = irFunctions['myFunctionName']
      irCommands = irFunction.irCommands
      irCommand = irCommands[0]

...or by direct construction of one of its subclasses:

      irCommandRaw = pylookinremote.IRRemoteCommandRaw('470 -390 470 -390 470 -390 470 -390 470 -390 470 -45000')

#### Public Attributes/Methods

`irCommand.typeName`
:   `str` name of the command type.

`irCommand = pylookinremote.IRRemoteCommand.fromJSON(jsonData)`
:   Static method.  Creates a new `IRRemoteCommand` object--or one of its appropriate subclasses--from the given `jsonData`.

`irCommand = pylookinremote.IRRemoteCommand.fromIRSensorData(jsonSensorData)`
:   Static method.  Creates a new `IRRemoteCommand` object--or one of its appropriate subclasses--from the given `jsonSensorData`.  `jsonSensorData` should be as it was returned by `LOOKinRemote.sensor('IR')`.  Only "raw" commands are currently supported.

`irCommand = pylookinremote.IRRemoteCommand(typeName)`
:   Constructor.  `typeName` should be a `str` name for the command type (e.g. "raw").

`irCommand.toJSON()`
:   Returns a JSON-compatible data structure that represents this object.

`irCommand.trigger(lookinRemote)`
:   Triggers this command on the given `lookinRemote`.

### Class `pylookinremote.IRRemoteCommandUndefined`

Represents an undefined-type remote command.

#### Public Attributes/Methods

`irCommand.data`
:   Python `object` of relevant data.

`irCommand = pylookinremote.IRRemoteCommandUndefined(typeName, data)`
:   Constructor.  `typeName` should be a `str` name for the command type (e.g. "raw"), and `data` can be anything.

`irCommand.toJSON()`
:   Returns a JSON-compatible data structure that represents this object.

`irCommand.trigger(lookinRemote)`
:   Triggers this command on the given `lookinRemote`.

### Class `pylookinremote.IRRemoteCommandRaw`

Represents a raw-type remote command sequence.

#### Public Attributes/Methods

`irCommandRaw = pylookinremote.IRRemoteCommandRaw(sequence, freqCarrier_Hz=38000)`
:   Constructor.  `sequence` should be an IR command sequence either as a `str` or iterable of `int`s.

`irCommandRaw.isSimilar(rhs)`
:   Returns `True` if `rhs` is similar to this object; `False` otherwise.

`len(irCommandRaw)`
:   Returns the length of the stored IR sequence.

`irCommandRaw.toJSON()`
:   Returns a JSON-compatible data structure that represents this object.

`irCommandRaw.toLOOKinRemoteAPIJSON()`
:   Returns a JSON-compatible data structure that represents this object appropriately for the LOOKin Device API.

`irCommandRaw.trigger(lookinRemote)`
:   Triggers this command on the given `lookinRemote`.
