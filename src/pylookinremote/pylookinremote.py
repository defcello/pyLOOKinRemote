#! /usr/bin/python3.8

"""
MIT License

Copyright (c) 2021 John Crawford

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from enum import Enum
from itertools import combinations
import datetime
import ipaddress
import json
import pathlib
import random
import socket
import sys
import time
import urllib.parse
import urllib.request




class LOOKinRemote:
	"""
	Use this class to interact with a LOOKin Remote device.  For example:

	@code
		from pylookinremote import LOOKinRemote
		devs = LOOKinRemote.findInNetwork()
		for dev in devs:
			meteoSensorMeas = dev.sensor('Meteo')
			temp_C = meteoSensorMeas['Temperature']
			temp_F = LOOKinRemote.celsius2Fahrenheit(meteoSensorMeas['Temperature'])
			humidityRel = meteoSensorMeas['Humidity']
			print(f'{dev!s} is reporting: {temp_C}°C/{temp_F:0.1f}°F and {humidityRel}%RH')
	@endcode

	This generates the output:

		Starting search for available LOOKinRemote devices...
		...Device Found at 192.168.0.123...
		...Device Found at 192.168.0.234...
		...Search complete!  Found 2 LOOKin Remote devices.
		LOOKinRemote(192.168.0.123) is reporting: 20.7°C/69.3°F and 53.6%RH
		LOOKinRemote(192.168.0.234) is reporting: 21.0°C/69.8°F and 61.3%RH
	"""

	def __init__(self, networkAddress, auxDataFilePath=None):
		"""
		Constructor.  `networkAddress` should be either the IP Address or DNS
		Address for the target device.

		`auxDataFilePath` may be a `str` or `pathlib.Path` object defining a
		local file to save backup/auxiliary information to, particularly
		important since function creation doesn't appear to work on LOOKin
		Remote devices.  Functions will be saved to and loaded from this file to
		augment what is saved on the device.
		"""
		if isinstance(networkAddress, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
			networkAddress = str(networkAddress)
		if auxDataFilePath is not None and not isinstance(auxDataFilePath, pathlib.Path):
			auxDataFilePath = pathlib.Path(auxDataFilePath)
		self._address = networkAddress
		self._auxDataFilePath = auxDataFilePath

	@staticmethod
	def celsius2Fahrenheit(temp_C):
		"""
		Returns `temp_C` in degrees Fahrenheit.
		"""
		return (float(temp_C) * 9. / 5.) + 32

	@staticmethod
	def fahrenheit2Celsius(temp_F):
		"""
		Returns `temp_F` in degrees Celsius.
		"""
		return (float(temp_F) - 32) * 5. / 9.

	@classmethod
	def findInNetwork(cls, timeout_sec=10, auxDataFilePath=None):
		"""
		Searches the network for `timeout_sec` seconds for available LOOKin
		Remote devices and returns a list of `LOOKinRemote` objects.

		`auxDataFilePath` will be passed through to any `LOOKinRemote` objects
		created.
		"""
		try:
			from zeroconf import ServiceBrowser, Zeroconf
		except ImportError:
			print('`findInNetwork` requires the "zeroconf" library (`pip install zeroconf`).')
		class Listener:
			serverAddrs = None
			def __init__(self):
				self.serverAddrs = []
			def add_service(self, zeroconf, type, name):
				info = zeroconf.get_service_info(type, name)
				ipAddr = ipaddress.ip_address(info.addresses[0])
				print(f'...Device Found at {ipAddr!s}...')
				self.serverAddrs.append(ipAddr)
			def remove_service(self, *args, **kargs):
				pass
			def update_service(self, *args, **kargs):
				pass
		zeroconf = Zeroconf()
		listener = Listener()
		print('Starting search for available LOOKinRemote devices...')
		serverBrowser = ServiceBrowser(zeroconf, '_lookin._tcp.local.', listener)
		time.sleep(timeout_sec)
		zeroconf.close()
		print(f'...Search complete!  Found {len(listener.serverAddrs)} LOOKin Remote devices.')
		return [LOOKinRemote(serverAddr, auxDataFilePath) for serverAddr in listener.serverAddrs]

	def api_commands_command_GET(self, command):
		"""
		API call.  Returns the remote's available events for `command`.

		"IR" Command Events
		(Source: https://documenter.getpostman.com/view/11774062/SzzkddLg?version=latest#b583e8ee-912c-46db-b294-18578c4333a5)

		Event name        	Event ID 	Description                                   	Possible operands
		ac                	0xEF     	Send command for the AC unit                  	AC Operand in XXXXMTFS, where XXXX - codeset, M - AC Mode, T - temperature offset over 16 degrees, F - fan mode, S - swing mode
		aiwa              	0x14     	Send aiwa command on 38 kHz                   	Aiwa command
		localremote       	0xFE     	Send command for saved remote                 	Operand with Remote UUID, function and param
		nec1              	0x01     	Send NEC1 command on 38 kHz                   	command
		necx              	0x04     	Send NecX command on 38 kHz                   	command
		panasonic         	0x05     	Send panasonic command on 38 kHz              	command
		prontohex         	0xF0     	Send command in ProntoHEX format              	Command in ProntoHEX
		prontohex-blocked 	?        	?                                             	?
		raw               	0xFF     	Send command in raw timings format            	string in format: "XX;[YY]" where `XX` is Frequency in Hz and `YY` is raw signal timings.
		repeat            	0xED     	Send repeat command for previos sended signal 	no operand
		samsung36         	0x06     	Send Samsung36 command on 38 kHz              	command
		saved             	0xEE     	Send command from device memory               	Storage item ID
		sony              	0x03     	Send Sony command on 38 kHz                   	command
		"""
		return json.loads(self._api_get(f'commands/{urllib.parse.quote(command)}'))

	def api_commands_GET(self):
		"""
		API call.  Returns the remote's available command classes.
		"""
		return json.loads(self._api_get('commands'))

	def api_commands_ir_localremote_GET(self, uuid, functionCode, signalID=0xFF):
		"""
		Triggers a "localremote" command event with `functionCode` and `signalID`.

		`uuid` should be a `str` or 16-bit `int`.
		`functionCode` should be a `str` or 8-bit `int`.
		`signalID` should be a `str` or 8-bit `int`.
		"""
		uuid = hex(0xFFFF & int(signal))[2:].upper()
		functionCode = hex(0xFF & int(functionCode))[2:].upper()
		signalID = hex(0xFF & int(signalID))[2:].upper()
		return json.loads(self._api_get(f'commands/ir/localremote/{uuid}{functionCode}{signalID}'))

	def api_commands_ir_nec1_signal_GET(self, signal):
		"""
		Triggers an "nec1" command event with `signal`.

		`signal` should be a hex string or 32-bit `int`.
		"""
		signal = hex(0xFFFFFFFF & int(signal))[2:].upper()
		return json.loads(self._api_get(f'commands/ir/nec1/{signal}'))

	def api_commands_ir_necx_GET(self, signal):
		"""
		Triggers an "necx" command event with `signal`.

		`signal` should be a hex string or 32-bit `int`.
		"""
		signal = hex(0xFFFFFFFF & int(signal))[2:]
		return json.loads(self._api_get(f'commands/ir/necx/{signal}'))

	def api_commands_ir_prontohex_GET(self, signal):
		"""
		Triggers a "prontohex" command event.

		`signal` should be either a `str` (e.g. `"0000 006C 0022 0002"`) or an
		iterable of 16-bit `int`s (e.g. `[0x0000, 0x006C, 0x0022, 0x0002]`).
		"""
		if not isinstance(signal, str):  #Assume it's an iterable.
			signal = ' '.join(hex(0xFFFF & x)[2:].upper() for x in signal)
		return json.loads(self._api_get(f'commands/ir/prontohex/{urllib.parse.quote(signal)}'))

	def api_commands_ir_raw_GET(self, signal, freqCarrier_Hz=38000):
		"""
		Triggers a "raw" command event.

		`signal` should be either a `str` (e.g.
		`"8000 -4500 9000 -4500 9000 -4500 9000 -4500 9000 -4500 9000 -4500"`)
		or an iterable of `int`s (e.g. `[8000, -4500, 9000, -4500, 9000,
		-4500, 9000, -4500, 9000, -4500, 9000, -4500]`).

		`freqCarrier_Hz` defines the carrier frequency of `signal`.
		"""
		if not isinstance(signal, str):  #Assume it's an iterable.
			signal = ' '.join(str(x) for x in signal)
		return json.loads(self._api_get(f'commands/ir/raw/{freqCarrier_Hz};{urllib.parse.quote(signal)}'))

	def api_commands_ir_saved_GET(self, signalID):
		"""
		Triggers a "saved" command event with `signalID`.

		`signalID` should be a `str` or `int`.
		"""
		signalID = str(int(signalID))
		return json.loads(self._api_get(f'commands/ir/saved/{signalID}'))

	def api_data_DEL(self, *, yesIWantToDoThis=False):
		"""
		Deletes all saved IR remotes from the device.  Make sure you want to
		call this!
		"""
		assert yesIWantToDoThis, f'Keyword argument `yesIWantToDoThis=True` is required to execute this method.'
		return self._api_del(f'data/')

	def api_data_GET(self):
		"""
		Returns the general data for all saved remotes.
		"""
		return json.loads(self._api_get('data'))

	def api_data_POST(self, name, irRemoteType, extra, uuid, updated):
		"""
		Creates a new IR remote definition on the device.

		The purpose of `extra` can vary by remote type.  For `AIRCONDITIONER`
		types, this will indicate the codeset to use.

		If `uuid` is `None`, a random one will be generated for you.
		"""
		return self._api_post(
			'data',
			Type=irRemoteType,
			Updated=updated,
			Name=name,
			UUID=uuid,
			Extra=extra,
		)

	def api_data_uuid_DEL(self, uuid):
		"""
		Deletes the IR remote `uuid` from the device.
		"""
		return self._api_del(f'data/{uuid}')

	def api_data_uuid_function_DEL(self, uuid, functionName):
		"""
		Deletes the function `functionName` from the IR remote `uuid` on the
		device.
		"""
		return self._api_del(f'data/{uuid}/{urllib.parse.quote(functionName)}')

	def api_data_uuid_function_GET(self, uuid, functionName):
		"""
		Returns the data for `functionName` of the IR remote `uuid`.
		"""
		return json.loads(self._api_get(f'data/{uuid}/{urllib.parse.quote(functionName)}'))

	def api_data_uuid_function_POST(self, uuid, functionName, functionType, signals):
		"""
		Creates a new IR remote function definition on the device for remote
		`uuid`.

		`signals` should be an iterable of IR command event definitions like
		those returned by `LOOKinRemote.api_commands_command_GET` and `IRRemoteCommand.toLOOKinRemoteAPIJSON()`.

		For more information, see:  https://www.reddit.com/r/homeautomation/comments/kqaggm/
		"""
		return self._api_post(
			f'data/{uuid}/{urllib.parse.quote(functionName)}',
			type=functionType,
			signals=signals,
		)
		# return self._api_post(
			# f'data/{uuid}',
			# name=functionName,
			# type=functionType,
			# signals=signals,
		# )

	def api_data_uuid_function_PUT(self, uuid, functionName, updated, functionType=None, signals=None):
		"""
		Updates the IR remote function definition `functionName` on the device
		for remote `uuid`.

		`None` values will be excluded from the update.

		`signals` should be an iterable of IR command event definitions like
		those returned by `LOOKinRemote.api_commands_command_GET`.

		For more information, see:  https://www.reddit.com/r/homeautomation/comments/kqaggm/
		"""
		kargs = {'updated': updated}
		if functionType is not None:
			kargs['type'] = functionType
		if signals is not None:
			kargs['signals'] = signals
		return self._api_put(
			f'data/{uuid}/{urllib.parse.quote(functionName)}', **kargs)

	def api_data_uuid_GET(self, uuid):
		"""
		Returns the data specific to the saved IR remote with the given `uuid`.
		"""
		return json.loads(self._api_get(f'data/{uuid}'))

	def api_data_uuid_PUT(self, uuid, updated, name=None, irRemoteType=None, extra=None):
		"""
		Updates the IR remote definition for `uuid` on the device.

		`None` values will be excluded.
		"""
		kargs = {'Updated': updated}
		if name is not None:
			kargs['Name'] = name
		if irRemoteType is not None:
			kargs['Type'] = irRemoteType
		if extra is not None:
			kargs['Extra'] = extra
		return self._api_put(f'data/{uuid}', **kargs)

	def _api_del(self, path):
		"""
		Issues GET request to API with `path`.  `kargs` will be added as parameters.
		"""
		url = urllib.parse.SplitResult(
			'http',
			self._address,
			path,
			'',
			'',
		).geturl()
		resp = urllib.request.urlopen(urllib.request.Request(
			url,
			method='DEL'
		), timeout=10)
		return resp.read()

	def api_device_GET(self):
		"""
		API call.  Returns the "device" information.
		"""
		return json.loads(self._api_get('device'))

	def api_device_POST(
			self,
			name=None,
			timeVal=None,
			timezone=None,
			sensormode=None,
			bluetoothmode=None,
			# firmware=None,  #This should only be modified by official software.
	):
		"""
		API call.  Sets the "device" values.  `None` parameters will be
		excluded.
		"""
		kargs = {}
		if name is not None:
			kargs['Name'] = name
		if timeVal is not None:
			kargs['Time'] = timeVal
		if timezone is not None:
			kargs['Timezone'] = timezone
		if sensormode is not None:
			kargs['SensorMode'] = sensormode
		if bluetoothmode is not None:
			kargs['BluetoothMode'] = bluetoothmode
		# if firmware is not None:  #This should only be modified by official software.
			# kargs['firmware'] = firmware  #This should only be modified by official software.
		retries = 5
		for tryNum in range(retries):
			resp = self._api_post('device', **kargs)
			timeout = time.time() + 30
			while(time.time() < timeout):
				time.sleep(5)  #The command takes a few seconds to process even when it works well.
				deviceInfo = self.api_device_GET()
				for (key, valExp) in kargs.items():
					if deviceInfo.get(key) != valExp:
						break
				else:
					return
			print(f'Timed Out Attempt {tryNum + 1} of {retries}...')
		else:
			raise TimeoutError(f'FAILED to set device parameters!')

	def _api_get(self, path, **kargs):
		"""
		Issues GET request to API with `path`.  `kargs` will be added as
		parameters.
		"""
		url = urllib.parse.SplitResult(
			'http',
			self._address,
			path,
			urllib.parse.urlencode(kargs),
			'',
		).geturl()
		print(f'_get - url={url!r}')
		resp = urllib.request.urlopen(url, timeout=5)
		return resp.read()

	def api_network_connect_GET(self, ssid=None):
		"""
		API call.  Tells the remote to connect to `ssid`, or the strongest
		available WiFi if `ssid` is `None`.
		"""
		kargs = {}
		if (ssid is not None):
			kargs['ssid'] = ssid
		return json.loads(self._api_get('network/connect', **kargs))

	def api_network_GET(self):
		"""
		API call.  Returns the device's network information.
		"""
		return json.loads(self._api_get('network'))

	def api_network_keepwifi_GET(self):
		"""
		API call.  Tells the remote to keep the WiFi connection while
		"sensor mode" is on.
		"""
		return json.loads(self._api_get('network/keepwifi'))

	def api_network_POST(self, ssid, password):
		"""
		API call.  Adds the network `ssid` and `password` to the remote's
		internal list of supported WiFi hotspots.
		"""
		return json.loads(self._api_post('network', WiFiSSID=ssid, WiFiPassword=password))

	def api_network_remotecontrol_GET(self):
		"""
		API call.  Fetches the remote's RemoteControl state.
		"""
		return json.loads(self._api_get('network/remotecontrol'))

	def api_network_remotecontrol_reconnect_GET(self):
		"""
		API call.  Tells the remote to use the "reconnect" RemoteControl state.
		"""
		return json.loads(self._api_get('network/remotecontrol/reconnect'))

	def api_network_remotecontrol_stop_GET(self):
		"""
		API call.  Tells the remote to use the "stop" RemoteControl state.
		"""
		return json.loads(self._api_get('network/remotecontrol/stop'))

	def api_network_savedssid_DEL(self, ssid):
		"""
		API call.  Deletes the network `ssid` from the remote's internal list of
		supported WiFi hotspots.
		"""
		return self._api_del(f'network/savedssid/{urllib.parse.quote(ssid)}')

	def api_network_SavedSSID_GET(self):
		"""
		API call.  Returns the device's internal list of saved networks.

		Use `api_network_POST` and `api_network_savedssid_DEL` to modify this list.
		"""
		return json.loads(self._api_get('network/SavedSSID'))

	def api_network_scannedssidlist_GET(self):
		"""
		API call.  Returns the network SSIDs the device found last time it
		booted up.
		"""
		return json.loads(self._api_get('network/scannedssidlist'))

	def _api_post(self, path, **kargs):
		"""
		Issues POST request to API with `path`.  `kargs` will be transmitted as
		a JSON document.
		"""
		# print(f'POST to {path!r} with parameters {kargs!r}')
		url = urllib.parse.SplitResult(
			'http',
			self._address,
			path,
			'',
			'',
		).geturl()
		resp = urllib.request.urlopen(
			url,
			json.dumps(kargs).encode(),
			timeout=10,
		)
		return resp.read()

	def _api_put(self, path, **kargs):
		"""
		Issues PUT request to API with `path`.  `kargs` will be transmitted as a
		JSON document.
		"""
		url = urllib.parse.SplitResult(
			'http',
			self._address,
			path,
			'',
			'',
		).geturl()
		resp = urllib.request.urlopen(urllib.request.Request(
			url,
			json.dumps(kargs).encode(),
			method='PUT'
		), timeout=10)
		return resp.read()

	def api_sensors_GET(self):
		"""
		API call.  Returns the remote's available sensors.
		"""
		return json.loads(self._api_get('sensors'))

	def api_sensors_sensor_GET(self, name):
		"""
		API call.  Returns the information for sensor named `name` on the remote.
		"""
		return json.loads(self._api_get(f'sensors/{urllib.parse.quote(name)}'))

	def commandEventLocalRemote(self, uuid, functionCode, signalID=0xFF):
		"""
		Triggers a "localremote" command event with `functionCode` and `signalID`.

		`uuid` should be a `str` or 16-bit `int`.
		`functionCode` should be a `str` or 8-bit `int`.
		`signalID` should be a `str` or 8-bit `int`.
		"""
		return self.api_commands_ir_localremote_GET(uuid, functionCode, signalID)

	def commandEventNEC1(self, signal):
		"""
		Triggers an "NEC1" command event with `signal`.

		`signal` should be a hex string or 32-bit `int`.
		"""
		return self.api_commands_ir_nec1_signal_GET(signal)

	def commandEventNECX(self, signal):
		"""
		Triggers an "NECx" command event with `signal`.

		`signal` should be a hex string or 32-bit `int`.
		"""
		return self.api_commands_ir_necx_GET(signal)

	def commandEventProntoHEX(self, signal):
		"""
		Triggers a "ProntoHEX" command event.

		`signal` should be either a `str` (e.g. `"0000 006C 0022 0002"`) or an
		iterable of 16-bit `int`s (e.g. `[0x0000, 0x006C, 0x0022, 0x0002]`).
		"""
		return self.api_commands_ir_prontohex_GET(signal)

	def commandEventRaw(self, signal, freqCarrier_Hz=38000):
		"""
		Triggers a "raw" command event.

		`signal` should be either a `str` (e.g.
		`"8000 -4500 9000 -4500 9000 -4500 9000 -4500 9000 -4500 9000 -4500"`)
		or an iterable of `int`s (e.g. `[8000, -4500, 9000, -4500, 9000,
		-4500, 9000, -4500, 9000, -4500, 9000, -4500]`).

		`freqCarrier_Hz` defines the carrier frequency of `signal`.
		"""
		return self.api_commands_ir_raw_GET(signal, freqCarrier_Hz)

	def commandEvents(self, command):
		"""
		Returns the remote's available events for `command`.

		"IR" Command Events
		(Source: https://documenter.getpostman.com/view/11774062/SzzkddLg?version=latest#b583e8ee-912c-46db-b294-18578c4333a5)

		Event name        	Event ID 	Description                                   	Possible operands
		ac                	0xEF     	Send command for the AC unit                  	AC Operand in XXXXMTFS, where XXXX - codeset, M - AC Mode, T - temperature offset over 16 degrees, F - fan mode, S - swing mode
		aiwa              	0x14     	Send aiwa command on 38 kHz                   	Aiwa command
		localremote       	0xFE     	Send command for saved remote                 	Operand with Remote UUID, function and param
		nec1              	0x01     	Send NEC1 command on 38 kHz                   	command
		necx              	0x04     	Send NecX command on 38 kHz                   	command
		panasonic         	0x05     	Send panasonic command on 38 kHz              	command
		prontohex         	0xF0     	Send command in ProntoHEX format              	Command in ProntoHEX
		prontohex-blocked 	?        	?                                             	?
		raw               	0xFF     	Send command in raw timings format            	string in format: "XX;[YY]" where `XX` is Frequency in Hz and `YY` is raw signal timings.
		repeat            	0xED     	Send repeat command for previos sended signal 	no operand
		samsung36         	0x06     	Send Samsung36 command on 38 kHz              	command
		saved             	0xEE     	Send command from device memory               	Storage item ID
		sony              	0x03     	Send Sony command on 38 kHz                   	command
		"""
		return self.api_commands_command_GET(command)

	def commandEventSaved(self, signalID):
		"""
		Triggers a "saved" command event with `signalID`.

		`signalID` should be a `str` or `int`.
		"""
		return self.api_commands_ir_saved_GET(signalID)

	def commands(self):
		"""
		Returns the remote's available command classes.
		"""
		return self.api_commands_GET()

	def remoteCreate(self, name, irRemoteType, extra='', uuid=None):
		"""
		Creates a new IR remote definition on the device.

		`irRemoteType` should be a value from `IRRemote.TYPE`.

		The purpose of `extra` can vary by remote type.  For `AIRCONDITIONER`
		types, this will indicate the codeset to use.

		If `uuid` is `None`, a random one will be generated for you.
		"""
		if isinstance(irRemoteType, str):
			irRemoteType = IRRemote.TYPE[irRemoteType]
		elif isinstance(irRemoteType, int):
			irRemoteType = IRRemote.TYPE(irRemoteType)
		uuids = []
		for remoteData in self.remotesData():
			uuids.append(remoteData['UUID'])
		if uuid is None:  #Generate one automatically.
			randUUID = lambda: ''.join(random.choices('0123456789ABCDEF', k=4))
			while True:
				uuid = randUUID()
				if uuid in uuids:
					continue
				break
		if uuid in uuids:
			raise ValueError(f'Given IR Remote UUID {uuid!r} already exists on the remote.')
		return self.api_data_POST(
			name,
			hex(irRemoteType.value)[2:].upper(),
			extra,
			uuid,
			str(time.time()),
		)

	def remoteFromUUID(self, uuid):
		"""
		Returns a new `IRRemote` object for the remote matching `uuid`.
		"""
		remotes = self.remotes()
		for remote in remotes:
			if remote.uuid == uuid:
				return remote
		raise ValueError(f'FAILED to find remote matching UUID {uuid!r}.')

	def _remoteGet(self, rootData):
		"""
		Returns the appropriate `IRRemote` object for the given data.
		`rootData` is the remote's data from "data/".
		"""
		typeID = rootData['Type']
		ret = None
		if typeID == 'EF':
			ret = ACRemote(self, rootData["UUID"], rootData)
		else:
			ret = IRRemote(self, rootData["UUID"], rootData)
		return ret

	def remotes(self):
		"""
		Returns the remote's saved IR remotes.
		"""
		remotes = []
		for rootData in self.remotesData():
			remotes.append(self._remoteGet(rootData))
		return remotes

	def remotesData(self):
		"""
		Returns the general data for all saved remotes.
		"""
		return self.api_data_GET()

	def remotesDelete(self, uuids):
		"""
		Deletes the IR remotes `uuids` from the device.

		`uuids` should be an iterable of `str` objects.
		"""
		return [self.remoteDelete(uuid) for uuid in uuids]

	def remotesDeleteAll(self, *, yesIWantToDoThis=False):
		"""
		Deletes all saved IR remotes from the device.  Make sure you want to
		call this!
		"""
		return self.api_data_DEL(yesIWantToDoThis=yesIWantToDoThis)

	def __repr__(self):
		if self._auxDataFilePath is None:
			return f'LOOKinRemote({self._address!r})'
		return f'LOOKinRemote({self._address!r}, {self._auxDataFilePath!r})'

	def sensor(self, name):
		"""
		Returns the remote's sensor information.
		"""
		return self.api_sensors_sensor_GET(name)

	def sensorDump(self, name, period, duration, maxSignals=None):
		"""
		Polls the `name` sensor for `duration` seconds and `period` seconds
		between calls.  Terminates early if `maxSignals` have been received.

		Use `period` of `<=0` seconds to poll as fast as possible.

		Use `maxSignals` of `None` to always run the full `duration`.

		Returns a `list` of data for all the non-empty captures (only "IR"
		sensor supported right now).
		"""
		print(f'Running sensor dump for {duration} seconds...')
		signals = []
		timeStop = time.time() + duration
		timeNext = 0
		while time.time() < timeStop:
			sensorData = None
			if time.time() > timeNext:
				if period > 0:
					timeNext = time.time() + period  #BEFORE calling so duration of call is included.
				try:
					sensorData = self.sensor(name)
				except (ConnectionResetError, socket.timeout, urllib.error.URLError):
					print('Connection Reset!  The device might be restarting due to a crash.')
				if (
						sensorData is not None
						and name == 'IR'
						and sensorData.get('Raw', '') != ''
						and (len(signals) == 0 or signals[-1].get('Updated') != sensorData.get('Updated'))
				):
					signals.append(sensorData)
					print(sensorData)
			if maxSignals is not None and len(signals) >= maxSignals:
				break
			if period > 0:
				time.sleep(max(0, time.time() - timeNext))
		print(f'...Sensor dump finished.  {len(signals)} signals detected.')
		return signals

	def sensorNames(self):
		"""
		Returns the remote's available sensors.
		"""
		return self.api_sensors_GET()

	def __str__(self):
		return self.__repr__()

class IRRemote:

	uuid = None  #`str` UUID of the remote.
	name = None  #`str` name of the remote.
	rType = None  #Value from `IRRemote.TYPE`.
	updated = None  #`datetime.datetime` object.
	functions = None  #`dict` mapping `str` function names to `IRRemoteFunction` objects.

	class TYPE(Enum):
		CUSTOM = 0x00
		TV = 0x01
		MEDIA = 0x02
		LIGHT = 0x03
		HUMIDIFIER_DEHUMIDIFIER = 0x04
		AIRPURIFIER = 0x05
		ROBOVACUUMCLEANER = 0x06
		DATADEVICEFAN = 0x07
		AIRCONDITIONER = 0xEF

	def __init__(self, lookinRemote, uuid, rootData=None, auxDataFilePath=None):
		"""
		Constructor initializing the object.  `lookinRemote` is a `LOOKinRemote`
		object.  `uuid` is the `str` UUID of this remote on `lookinRemote`.

		`rootData` is the remote's data from "data/".  If `None`, this will be
		fetched automatically.

		`auxDataFilePath` may be a `str` or `pathlib.Path` object defining a
		local file to save backup/auxiliary information to, particularly
		important since function creation doesn't appear to work on LOOKin
		Remote devices.  Functions will be saved to and loaded from this file to
		augment what is saved on the device.  If `None`, will try to use the
		file defined in `lookinRemote` or will otherwise not use an aux data
		file.
		"""
		if rootData is None:
			for rootData in lookinRemote.remotesData():
				if rootData["UUID"] == uuid:
					break
			else:
				raise ValueError(
					f'Failed to find remote with UUID {uuid!r} on the device.',
				)
		if auxDataFilePath is None:
			auxDataFilePath = lookinRemote._auxDataFilePath
		if auxDataFilePath is not None and not isinstance(auxDataFilePath, pathlib.Path):
			auxDataFilePath = pathlib.Path(auxDataFilePath)
		self._auxDataFilePath = auxDataFilePath
		self._rootData = rootData
		self._lookinRemote = lookinRemote  #BEFORE `_remoteDataRefresh` call.
		self.functions = {}
		self.uuid = self._rootData['UUID']  #BEFORE `_remoteDataRefresh` call.
		self._remoteDataRefresh()
		self.name = self._remoteData['Name']
		self.rType = IRRemote.TYPE(int(self._rootData['Type'], 16))
		self.updated = datetime.datetime.fromtimestamp(
			int(self._rootData['Updated']),
			datetime.timezone.utc,
		)
		self._functionsRefresh()

	def _auxDataLoad(self):
		"""
		Returns the data from the auxiliary data file.
		"""
		ret = None
		if self._auxDataFilePath is not None and self._auxDataFilePath.exists():
			with self._auxDataFilePath.open('r') as fdRO:
				ret = json.load(fdRO)
		if ret is None:
			ret = {}
		return ret;

	def _auxDataSave(self):
		"""
		Saves data about this object to the auxiliary data file.
		"""
		if self._auxDataFilePath is not None:
			jsonData = None
			if self._auxDataFilePath.exists():
				with self._auxDataFilePath.open('r') as fdRO:
					jsonData = json.load(fdRO)
			if jsonData is None:
				jsonData = {}
			jsonData.setdefault('remotes', {})
			jsonData['remotes'][self.uuid] = self.toJSON()
			with self._auxDataFilePath.open('w') as fdWO:
				json.dump(jsonData, fdWO, sort_keys=True, indent=4)

	def _functionsRefresh(self):
		"""
		Refreshes `self.functions` from `self._remoteData` and
		`self._auxDataFilePath`.
		"""
		self.functions.clear()
		jsonData = self._auxDataLoad()
		jsonDataFunctions = jsonData.get('remotes', {}).get(self.uuid, {}).get('functions', {})
		for (fName, jsonDataFunction) in jsonDataFunctions.items():
			self.functions[fName] = IRRemoteFunction.fromJSON(jsonDataFunction)
		for fName in self._remoteData.get('Functions'):
			apiFunctionData = self._lookinRemote.api_data_uuid_function_GET(self.uuid, fName)
			self.functions[fName] = IRRemoteFunction(fName, None)  #Override anything defined in aux data.

	def _remoteDataRefresh(self):
		"""
		Refreshes `self._remoteData` to match what's on the device.
		"""
		self._remoteData = self._lookinRemote.api_data_uuid_GET(self.uuid)
		self._functionsRefresh()

	def details(self):
		"""
		Returns this remote's details.
		"""
		ret = {
			'UUID': self.uuid
		}
		ret.update(self._remoteData)
		return ret

	def delete(self):
		"""
		Deletes this IR remote from the device.
		"""
		return self._lookinRemote.api_data_uuid_DEL(self.uuid)

	def functionCreate(self, irRemoteFunction):
		"""
		Creates a function on the remote device using the data in
		`irRemoteFunction`.

		`irRemoteFunction` should be a `IRRemoteFunction` object.
		"""
		if self.functionExists(irRemoteFunction.name):
			raise ValueError(f'Given function name {irRemoteFunction.name!r} already exists for remote UUID {self.uuid!r}.')
		try:
			signals = []
			for irRemoteCommand in irRemoteFunction.irCommands:
				if not isinstance(irRemoteCommand, IRRemoteCommand):
					raise ValueError(
						f'`irRemoteCommands` contained an object of unexpected type {type(irRemoteCommand)!r}.'
					)
				signals.append(irRemoteCommand.toLOOKinRemoteAPIJSON())
			ret = self._lookinRemote.api_data_uuid_function_POST(
				self.uuid,
				irRemoteFunction.name,
				irRemoteFunction.functionType.value,
				signals,
			)
		except (ConnectionResetError, socket.timeout, urllib.error.URLError):
			if self._auxDataFilePath is None:
				raise
			else:
				print('Error writing function to device; saving to auxiliary data file...')
				self.functions[irRemoteFunction.name] = irRemoteFunction
				self._auxDataSave()
				print('...Done!')
		self._remoteDataRefresh()
		return ret

	def functionDelete(self, functionName):
		"""
		Deletes the function `functionName` from the device.
		"""
		if not self.functionExists(functionName):
			raise ValueError(f'Given function name {functionName!r} does NOT exist for remote UUID {self.uuid!r}.')
		ret = self._lookinRemote.api_data_uuid_function_DEL(self.uuid, functionName)
		del self.functions[functionName]
		self._auxDataSave()
		self._remoteDataRefresh()
		return ret

	def functionExists(self, functionName):
		"""
		Returns `True` if a function named `functionName` is defined.
		"""
		self._remoteDataRefresh()
		return functionName in self.functions

	def functionTrigger(self, functionName):
		"""
		Triggers the function `functionName`.  The exact behavior depends on the type of function.
		"""
		if not self.functionExists(functionName):
			raise ValueError(f'Given function name {functionName!r} does not exists for remote UUID {self.uuid!r}.')
		self.functions[functionName].trigger(self._lookinRemote)

	def functionUpdate(self, irRemoteFunction, upsert=True):
		"""
		Updates the function definition for `irRemoteFunction`, a
		`pylookinremote.IRRemoteFunction` object.

		If `upsert` is true, will create the function if it doesn't currently
		exist.
		"""
		if not upsert and not self.functionExists(functionName):
			raise ValueError(f'Given function name {functionName!r} does not exists for remote UUID {self.uuid!r}.')
		ret = None
		try:
			signals = []
			for irRemoteCommand in irRemoteFunction.irCommands:
				if not isinstance(irRemoteCommand, IRRemoteCommand):
					raise ValueError(
						f'`irRemoteCommands` contained an object of unexpected type {type(irRemoteCommand)!r}.'
					)
				signals.append(irRemoteCommand.toLOOKinRemoteAPIJSON())
			ret = self._lookinRemote.api_data_uuid_function_PUT(
				self.uuid,
				irRemoteFunction.name,
				irRemoteFunction.functionType.value,
				signals,
				str(time.time())
			)
		except (ConnectionResetError, socket.timeout, urllib.error.URLError):
			print('Error writing function to device; saving to auxiliary data file...')
			self.functions[irRemoteFunction.name] = irRemoteFunction
			self._auxDataSave()
			print('...Done!')
		self._remoteDataRefresh()
		return ret

	def toJSON(self):
		"""
		Returns a JSON-compatible data structure that represents this object.
		"""
		return {
			'name': self.name,
			'uuid': self.uuid,
			'rType': self.rType.name,
			'updated': self.updated.timestamp(),
			'functions': {
				fName: irFunction.toJSON() for (fName, irFunction) in self.functions.items()
			},
		}

	def update(self, name=None, irRemoteType=None, extra=None):
		"""
		Updates the IR remote definition for `uuid` on the device.

		`None` values will be unmodified.
		"""
		if name is None:
			name = self._remoteData.get('Name')
		if irRemoteType is None:
			irRemoteType = self._remoteData.get('Type')
		else:
			if isinstance(irRemoteType, str):
				irRemoteType = IRRemote.TYPE[irRemoteType]
			elif isinstance(irRemoteType, int):
				irRemoteType = IRRemote.TYPE(irRemoteType)
			irRemoteType = hex(irRemoteType.value)[2:].upper()
		if extra is None:
			extra = self._remoteData.get('Extra')
		return self._lookinRemote.api_data_uuid_PUT(
			self.uuid,
			str(time.time()),
			name,
			irRemoteType,
			extra
		)

	def __repr__(self):
		return repr((self._rootData, self._remoteData))

	def __str__(self):
		return f'{self.uuid} - {self.rType.name} Remote'

class ACRemote(IRRemote):

	class OPERATINGMODE(Enum):
		OFF = 0x0000
		AUTO = 0x1000
		COOL = 0x2000
		HEAT = 0x3000
		UNKNOWN04 = 0x4000  #Supposed to be "Dry" mode, but doesn't work.
		UNKNOWN05 = 0x5000
		UNKNOWN06 = 0x6000
		UNKNOWN07 = 0x7000
		UNKNOWN08 = 0x8000
		UNKNOWN09 = 0x9000
		UNKNOWN10 = 0xA000
		UNKNOWN11 = 0xB000
		UNKNOWN12 = 0xC000  #Supposed to be "Vent" mode, but doesn't work.
		UNKNOWN13 = 0xD000
		UNKNOWN14 = 0xE000
		UNKNOWN15 = 0xF000

	class FANSPEEDMODE(Enum):
		UNKNOWN00 = 0x0000
		MINIMUM = 0x0010
		MEDIUM = 0x0020
		MAXIMUM = 0x0030
		UNKNOWN04 = 0x0040
		UNKNOWN05 = 0x0050
		UNKNOWN06 = 0x0060
		UNKNOWN07 = 0x0070
		UNKNOWN08 = 0x0080
		UNKNOWN09 = 0x0090
		AUTO = 0x00A0
		UNKNOWN11 = 0x00B0
		UNKNOWN12 = 0x00C0
		UNKNOWN13 = 0x00D0
		UNKNOWN14 = 0x00E0
		UNKNOWN15 = 0x00F0

	class SWINGMODE(Enum):
		UNKNOWN00 = 0x0000
		UNKNOWN01 = 0x0001
		UNKNOWN02 = 0x0002
		UNKNOWN03 = 0x0003
		UNKNOWN04 = 0x0004
		UNKNOWN05 = 0x0005
		UNKNOWN06 = 0x0006
		UNKNOWN07 = 0x0007
		UNKNOWN08 = 0x0008
		UNKNOWN09 = 0x0009
		UNKNOWN10 = 0x000A
		UNKNOWN11 = 0x000B
		UNKNOWN12 = 0x000C
		UNKNOWN13 = 0x000D
		UNKNOWN14 = 0x000E
		UNKNOWN15 = 0x000F

	class Status:

		operatingMode = None
		tempTarget_C = None
		tempTarget_F = None
		fanSpeedMode = None
		swingMode = None

		def __init__(self, operatingMode, tempTarget_C, fanSpeedMode, swingMode):
			self.operatingModeSet(operatingMode)
			self.tempTargetSet(tempTarget_C)
			self.fanSpeedModeSet(fanSpeedMode)
			self.swingModeSet(swingMode)

		@classmethod
		def fromStatusBytes(cls, statusBytes):
			"""
			Creates an instance of this class using the data contained in
			`statusBytes`.

			`statusBytes` may be `int` or `str`.
			"""
			if isinstance(statusBytes, str):
				statusBytes = int(statusBytes, 16)
			return cls(
				statusBytes & 0xF000,
				((statusBytes & 0x0F00) >> 8) + 16,
				statusBytes & 0x00F0,
				statusBytes & 0x000F,
			)

		def operatingModeSet(self, operatingMode):
			"""
			Sets this object's operating mode to `operatingMode`.
			"""
			if isinstance(operatingMode, str):
				operatingMode = ACRemote.OPERATINGMODE[operatingMode]
			elif isinstance(operatingMode, int):
				operatingMode = ACRemote.OPERATINGMODE(operatingMode)
			if not isinstance(operatingMode, ACRemote.OPERATINGMODE):
				raise ValueError(f'Unexpected data type for `operatingMode`: {type(operatingMode)}')
			self.operatingMode = operatingMode

		def tempTargetSet(self, tempTarget_C):
			"""
			Sets this object's target temperature to `tempTarget_C` (Celsius).
			"""
			if (31 < tempTarget_C or 16 > tempTarget_C):
				raise ValueError('Only temperatures between 16°C and 31°C are supported.')
			tempTarget_C = min(31, max(16, int(tempTarget_C)))
			self.tempTarget_C = tempTarget_C
			self.tempTarget_F = LOOKinRemote.celsius2Fahrenheit(tempTarget_C)

		def tempTargetSet_F(self, tempTarget_F):
			"""
			Sets this object's target temperature to `tempTarget_F` (Fahrenheit).
			"""
			self.tempTargetSet(LOOKinRemote.fahrenheit2Celsius(tempTarget_F))

		def toStatusBytes(self):
			"""
			Returns the 16-bit `int` with the appropriate status bytes for this object.
			"""
			return (
				self.operatingMode.value
				| ((self.tempTarget_C - 16) << 8)
				| self.fanSpeedMode.value
				| self.swingMode.value
			)

		def __eq__(self, rhs):
			if isinstance(rhs, type(self)):
				return (
					rhs.operatingMode is self.operatingMode
					and rhs.tempTarget_C is self.tempTarget_C
					and rhs.fanSpeedMode is self.fanSpeedMode
					and rhs.swingMode is self.swingMode
				)

		def fanSpeedModeSet(self, fanSpeedMode):
			"""
			Sets this object's fan speed to `fanSpeedMode`.
			"""
			if isinstance(fanSpeedMode, str):
				fanSpeedMode = ACRemote.FANSPEEDMODE[fanSpeedMode]
			elif isinstance(fanSpeedMode, int):
				fanSpeedMode = ACRemote.FANSPEEDMODE(fanSpeedMode)
			self.fanSpeedMode = fanSpeedMode

		def __str__(self):
			return f'ACStatus({self.operatingMode.name}, {self.tempTarget_C}°C, {self.fanSpeedMode.name}, {self.swingMode.name})'

		def swingModeSet(self, swingMode):
			"""
			Sets this object's swing mode to `swingMode`.
			"""
			if isinstance(swingMode, str):
				swingMode = ACRemote.SWINGMODE[swingMode]
			elif isinstance(swingMode, int):
				swingMode = ACRemote.SWINGMODE(swingMode)
			self.swingMode = swingMode

	def __init__(self, *args, **kargs):
		super().__init__(*args, **kargs)
		self._remoteDataSet(self._remoteData)

	def __str__(self):
		return f'{self.uuid} - {self.rType.name} Remote: Status={hex(self._status.toStatusBytes()).upper()}; LastStatus={hex(self._statusLast.toStatusBytes()).upper()}'

	def operatingModeSet(self, operatingMode):
		"""
		Tells the device to switch operating mode to `operatingMode`.

		`operatingMode` should be an instance of
		`pylookinremote.ACRemote.OPERATINGMODE`.
		"""
		self._status.operatingModeSet(operatingMode)
		self.statusSet(self._status)

	def tempSet(self, temp_C):
		"""
		Tells the device to target the Celsius temperature `temp_C`.
		"""
		self._status.tempTargetSet(temp_C)
		self.statusSet(self._status)

	def tempSetF(self, temp_F):
		"""
		Tells the device to target the Fahrenheit temperature `temp_F`.
		"""
		return self.tempSet(LOOKinRemote.fahrenheit2Celsius(temp_F))

	def fanSpeedModeSet(self, fanSpeedMode):
		"""
		Tells the device to use `fanSpeedMode`.

		`fanSpeedMode` should be an instance of
		`pylookinremote.ACRemote.FANSPEEDMODE`.
		"""
		self._status.fanSpeedModeSet(operatingMode)
		self.statusSet(self._status)

	def _remoteDataSet(self, remoteData):
		"""
		Updates this object with the data in `remoteData`.
		"""
		self._remoteData = remoteData
		self._extra = self._remoteData.get('Extra')
		if 'Status' in self._remoteData:
			self._status = self.Status.fromStatusBytes(self._remoteData['Status'])
		else:
			self._status = self.Status('OFF', 23, 'AUTO', 'UNKNOWN00')
		if 'LastStatus' in self._remoteData:
			self._statusLast = self.Status.fromStatusBytes(self._remoteData['LastStatus'])
		else:
			self._statusLast = self.Status('OFF', 23, 'AUTO', 'UNKNOWN00')

	def swingModeSet(self, swingMode):
		"""
		Tells the device to use `swingMode`.

		`swingMode` should be an instance of
		`pylookinremote.ACRemote.SWINGMODE`.
		"""
		self._status.swingModeSet(operatingMode)
		self.statusSet(self._status)

	def statusGet(self, refresh=False):
		"""
		Returns the current status of the device.
		"""
		if refresh:
			return self.statusRefresh()
		return self._status

	def statusRefresh(self):
		"""
		Requests the current status from the device.

		Will return the cached state unless `refresh` is `True`.
		"""
		self._remoteDataSet(self._lookinRemote.remoteData(self._uuid))
		return self._status

	def statusSet(self, status):
		"""
		Modifies the device's status to match `status`.

		`status` should be an instance of `pylookinremote.ACRemote.Status`.
		"""
		retries = 5
		for tryNum in range(retries):
			self._lookinRemote._get(f'commands/ir/ac/{self._extra}{status.toStatusBytes():04X}')
			timeout = time.time() + 30
			while(time.time() < timeout):
				time.sleep(5)  #The command takes a few seconds to process even when it works well.
				self.statusRefresh()
				print(self._status)
				if self._status == status:
					return
			print(f'Timed Out Attempt {tryNum + 1} of {retries}...')
		else:
			raise TimeoutError(f'FAILED to set status!')

class IRRemoteFunction:
	"""
	Base class for IR Remote Functions.
	"""

	class TYPE(Enum):
		SINGLE = 'single'
		TOGGLE = 'toggle'

	name = None  #`str` name of the function.
	functionType = None  #Value from `IRRemoteFunction.TYPE`.
	irCommands = None  #`tuple` of `IRRemoteCommand` objects.  `None` indicates the commands are stored on the remote device.

	@staticmethod
	def fromJSON(jsonData):
		"""
		Creates a new `IRRemoteFunction` object from the given `jsonData`.
		"""
		irCommands = tuple(
			IRRemoteCommand.fromJSON(jsonDataCommand) for jsonDataCommand in jsonData.get('irCommands', ())
		)
		return IRRemoteFunction(
			jsonData.get('name'),
			irCommands,
			IRRemoteFunction.TYPE[jsonData.get('type', IRRemoteFunction.TYPE.SINGLE.name)],
		)

	@staticmethod
	def fromIRSensor(lookinRemote, functionName, functionType=TYPE.SINGLE):
		"""
		Creates/"Learns" a new `IRRemoteFunction` object from IR sequences
		detected by the given `lookinRemote`'s IR sensor.
		"""
		if functionType is not IRRemoteFunction.TYPE.SINGLE:
			raise NotImplementedError(f'Functions of type {functionType.name!r} are not yet supported.')
		print(f'Learning new IR remote function {functionName!r}...')
		print('...Please trigger the desired IR remote function repeatedly on the target LOOKin Remote...')
		irSensorData = lookinRemote.sensorDump('IR', 1, 300, 10)
		print('...capture complete!  You can stop triggering the IR remote.')
		irCommands = list(
			(IRRemoteCommand.fromIRSensorData(irSensorDatum) for irSensorDatum in irSensorData)
		)
		irCommandGroups = IRRemoteCommandRaw._groupCommands(irCommands)
		irCommandMostCommon = None
		irCommandGroupMostCommon = None
		for (irCommand, irCommandGroup) in irCommandGroups.items():
			if irCommandMostCommon is None or len(irCommandGroupMostCommon) < len(irCommandGroup):
				irCommandMostCommon = irCommand
				irCommandGroupMostCommon = irCommandGroup
		if irCommandMostCommon is None:
			print('FAILED to find any recurring commands.  Please retry.')
		else:
			print(f'SUCCESS capturing command!  Command selected with {len(irCommandGroupMostCommon)} matches out of {len(irCommands)} total signals detected.')
		return IRRemoteFunction(functionName, irCommandMostCommon, IRRemoteFunction.TYPE.SINGLE)

	def __init__(self, functionName, irRemoteCommands, functionType=TYPE.SINGLE):
		"""
		NOTE: This does not appear to work properly on LOOKin Remote devices.

		Constructor.

		`functionName` should be a `str` name for the function.

		`irRemoteCommands` should be either an iterable of `IRRemoteCommand`
		objects or a single `IRRemoteCommand` object.

		`functionType` should be a value from `IRRemoteFunction.TYPE`.  Types
		are undocumented on the LOOKin API documentation.  Here's what I think I
		know:

		- `???` = "Signal sequence"
		- `'single'` = "Basic button" and requires `irRemoteCommands` of length `1`.
		- `???` = "Power button"
		- `???` = "Cursor pad"
		- `???` = "Digits"
		- `???` = "Up and Down Buttons"
		- `???` = "Modes control"
		- `'toggle'` = "Toggle button" and requires `irRemoteCommands` of length `2`.

		For more information, see:  https://www.reddit.com/r/homeautomation/comments/kqaggm/
		"""
		if isinstance(irRemoteCommands, IRRemoteCommand):
			irRemoteCommands = (irRemoteCommands,)
		if functionType is None:
			raise ValueError('`functionType` may not be `None`.')
		if not isinstance(functionType, IRRemoteFunction.TYPE):
			functionType = IRRemoteFunction.TYPE(functionType)
		irRemoteCommandsLenAct = len(irRemoteCommands)
		if functionType is IRRemoteFunction.TYPE.SINGLE:
			irRemoteCommandsLenExp = 1
		elif functionType is IRRemoteFunction.TYPE.TOGGLE:
			irRemoteCommandsLenExp = 2
		else:
			irRemoteCommandsLenExp = None
		if irRemoteCommandsLenExp is not None and irRemoteCommandsLenAct != irRemoteCommandsLenExp:
			raise ValueError(
				f'Expected {irRemoteCommandsLenExp} `IRRemoteCommand` object(s) for function type {functionType.name!r}; found {irRemoteCommandsLenAct}.'
			)
		self.name = functionName
		self.functionType = functionType;
		self.irCommands = []
		for irRemoteCommand in irRemoteCommands:
			if not isinstance(irRemoteCommand, IRRemoteCommand):
				raise ValueError(
					f'`irRemoteCommands` contained an object of unexpected type {type(irRemoteCommand)!r}.'
				)
			self.irCommands.append(irRemoteCommand)
		self.irCommands = tuple(self.irCommands)  #Make it immutable.

	def toJSON(self):
		"""
		Returns this object serialized into a JSON-compatible data structure.
		"""
		return {
			'name': self.name,
			'type': self.functionType.name,
			'irCommands': None if self.irCommands is None else list(irCommand.toJSON() for irCommand in self.irCommands)
		}

	def trigger(self, lookinRemote):
		"""
		Triggers this function on the given `lookinRemote`.
		"""
		if self.irCommands is None:
			raise NotImplementedError('`LOOKinRemote.commandEventLocalRemote(...)` is not yet supported.')
		elif self.functionType is not IRRemoteFunction.TYPE.SINGLE:
			raise NotImplementedError(f'Functions of type {self.functionType.name!r} are not yet supported.')
		self.irCommands[0].trigger(lookinRemote)

class IRRemoteCommand:
	"""
	Base class for IR Remote Commands.  This is not useful until it is
	subclassed.
	"""

	typeName = None  #`str` name of the command type.

	@staticmethod
	def fromJSON(jsonData):
		"""
		Creates a new `IRRemoteCommand` object--or one of its appropriate
		subclasses--from the given `jsonData`.
		"""
		typeName = next(iter(jsonData.keys()), None)  #Should only be one item in the `dict`.
		if typeName == 'raw':
			ret = IRRemoteCommandRaw(
				jsonData['raw']['Signal'],
				jsonData['raw']['Frequency'],
			)
		# elif typeName == 'ProntoHEX':  #Not yet supported.
			# ret = IRRemoteCommandProntoHEX(
				# jsonData['ProntoHEX']
			# )
		else:
			print('IR Remote Command type {typeName!r} is not supported.')
			ret = IRRemoteCommandUndefined(typeName, jsonData[typeName])
		return ret

	@staticmethod
	def fromIRSensorData(jsonSensorData):
		"""
		Creates a new `IRRemoteCommand` object--or one of its appropriate
		subclasses--from the given `jsonSensorData`.

		`jsonSensorData` should be as it was returned by
		`LOOKinRemote.sensor('IR')`.  Only "raw" commands are currently
		supported.
		"""
		rawSequenceData = jsonSensorData.get('Raw', '')
		if rawSequenceData == '':
			raise ValueError('ERROR Failed to recognize IR sensor data.')
		return IRRemoteCommandRaw(rawSequenceData)

	def __init__(self, typeName):
		"""
		Initializes this object with `typeName`.
		"""
		self.typeName = typeName

	def toJSON(self):
		"""
		Returns a JSON-compatible data structure that represents this object.

		Should be defined by a subclass.
		"""
		raise Exception('This method needs to be overridden by the subclass.')

	def trigger(self, lookinRemote):
		"""
		Triggers this command on the given `lookinRemote`.

		Should be defined by a subclass.
		"""
		raise Exception('This method needs to be overridden by the subclass.')

class IRRemoteCommandUndefined(IRRemoteCommand):
	"""
	Represents undefined remote command sequence types.
	"""

	data = None  #Relevant data.

	def __init__(self, typeName, data):
		"""
		Initializes this object with `typeName` and `data`.

		`data` can be whatever type of object is relevant to the given
		`typeName`.
		"""
		super().__init__(typeName)
		self.data = data

	def toJSON(self):
		"""
		Returns a JSON-compatible data structure that represents this object.
		"""
		return {self.typeName: self.data}

	def trigger(self, lookinRemote):
		"""
		Triggers this command on the given `lookinRemote`.
		"""
		raise Exception('This method is not supported.')

class IRRemoteCommandRaw(IRRemoteCommand):

	def __init__(self, sequence, freqCarrier_Hz=38000):
		"""
		Constructor.

		`sequence` should be an IR command sequence either as a `str` or
		iterable of `int`s.

		`freqCarrier_Hz` should be a positive `int`.
		"""
		super().__init__('raw')
		if isinstance(sequence, str):
			sequence = IRRemoteCommandRaw._parse(sequence)
		self._freqCarrier_Hz = freqCarrier_Hz
		self._hash = hash(sequence)
		self._sequence = sequence

	def __eq__(self, rhs):
		"""
		Returns `True` if `rhs` is equal to this object; `False` otherwise.
		"""
		return (
			type(self) == type(rhs)
			and self._hash == rhs._hash
		)

	def __hash__(self):
		return self._hash

	@staticmethod
	def _compare(lhs, rhs):
		"""
		Compares the 2 IR command sequences.  Returns `True` if it thinks they're a
		match.
		"""
		if isinstance(lhs, str):
			lhs = IRRemoteCommandRaw._parse(lhs)
		if isinstance(rhs, str):
			rhs = IRRemoteCommandRaw._parse(rhs)
		sampleDiffThreshold = 0.10  #10% maximum difference to match.
		samplesNumDiff = abs(len(lhs) - len(rhs))
		samplesNum = max(len(lhs), len(rhs))
		commandDiffThreshold = 0.02  #2% maximum difference to match.
		commandDiffPct = -1
		# print(f'Lengths: ')
		for (idx, (lhsSample, rhsSample)) in enumerate(zip(lhs._sequence, rhs._sequence)):
			pctDiff = abs(abs(lhsSample) - abs(rhsSample)) / (abs(lhsSample) + abs(rhsSample))
			if (pctDiff > sampleDiffThreshold):
				samplesNumDiff += 1
				# print(f'{idx:03d}: {lhsSample:>5d}<=>{rhsSample:>5d}; {pctDiff * 100:>2.0f}%diff')
		# print(f'{samplesNumDiff} samples different; {samplesNum - samplesNumDiff} samples similar')
		commandDiffPct = (samplesNumDiff / samplesNum)
		isMatch = (
			len(lhs) == len(rhs)
			and commandDiffThreshold >= commandDiffPct
		)
		print(f'IR COMMANDS ARE {(1 - commandDiffPct) * 100:.0f}% SIMILAR; LENGTH {len(lhs)}<=>{len(rhs)} IS {"SAME" if len(lhs) == len(rhs) else "DIFFERENT"}; {"MATCH!" if isMatch else "NOT A MATCH"}')
		return commandDiffThreshold >= commandDiffPct

	@staticmethod
	def _groupCommands(irRemoteCommands, minMatches=2):
		"""
		Returns the groups of `IRRemoteCommandRaw` objects that match each other as a
		`dict` mapping a `IRRemoteCommandRaw` object to a `set` of `IRRemoteCommandRaw`
		objects.

		Groups with less than `minMatches` members will be excluded from the output.
		"""
		retCommands = {}  #Maps `IRRemoteCommand` objects to a list of similar `IRRemoteCommand` objects.
		retIDs = {}  #Maps `int` object IDs to a `set` of `int` object IDs.
		for (lhs, rhs) in combinations(irRemoteCommands, 2):
			#Have to use IDs to handle identical IR sequences.
			lhsID = id(lhs)
			rhsID = id(rhs)
			if lhs.isSimilar(rhs):  #Found a match!
				if lhsID in retIDs:
					if rhsID not in retIDs[lhsID]:
						retCommands[lhs].append(rhs)
						retIDs[lhsID].add(rhsID)
				elif rhsID in retIDs:
					if lhsID not in retIDs[rhsID]:
						retCommands[rhs].append(lhs)
						retIDs[rhsID].add(lhsID)
				else:
					matchFound = False
					for key in retCommands.keys():
						if key.isSimilar(lhs) or key.isSimilar(rhs):  #Add to existing group(s).
							matchFound = True
							keyID = id(key)
							if lhsID not in retIDs[keyID]:
								retCommands[key].append(lhs)
								retIDs[keyID].add(lhsID)
							if rhsID not in retIDs[keyID]:
								retCommands[key].append(rhs)
								retIDs[keyID].add(rhsID)
							#Do NOT break; we want to correlate with all similar key signals.
					if not matchFound:  #Create new group.
						retCommands[lhs] = [lhs, rhs]
						retIDs[lhsID] = {lhsID, rhsID}
		toDelete = []
		for (key, values) in retCommands.items():
			if len(values) < minMatches:
				toDelete.append(key)
		for key in toDelete:
			del retCommands[key]
		print(f'Found {len(retCommands)} groups of commands.\n\n\n')
		return retCommands

	@staticmethod
	def _parse(ir_str):
		"""
		Parses the IR command string into a `tuple` of `int`.
		"""
		return tuple(int(x) for x in ir_str.split())

	def isSimilar(self, rhs):
		"""
		Returns `True` if `rhs` is similar to this object; `False` otherwise.
		"""
		if not isinstance(rhs, IRRemoteCommandRaw):
			rhs = IRRemoteCommandRaw(rhs)
		return (self == rhs or IRRemoteCommandRaw._compare(self, rhs))

	def __len__(self):
		"""
		Returns the length of the stored IR sequence.
		"""
		return len(self._sequence)

	def toJSON(self):
		"""
		Returns a JSON-compatible data structure that represents this object.
		"""
		return self.toLOOKinRemoteAPIJSON()

	def toLOOKinRemoteAPIJSON(self):
		"""
		Returns a JSON-compatible data structure that represents this object
		appropriately for the LOOKin Device API.
		"""
		return {
			'raw': {
				'Frequency': str(self._freqCarrier_Hz),
				'Signal': ' '.join(str(sample) for sample in self._sequence),
			},
		}

	def trigger(self, lookinRemote):
		"""
		Triggers this command on the given `lookinRemote`.
		"""
		lookinRemote.commandEventRaw(self._sequence, self._freqCarrier_Hz)

if __name__ == '__main__':
	auxDataFilePath='./auxData.json'
	# dev = LOOKinRemote('192.168.1.123', auxDataFilePath)
	devs = LOOKinRemote.findInNetwork(auxDataFilePath=auxDataFilePath)
	for dev in devs:
		meteoSensorMeas = dev.sensor('Meteo')
		temp_C = meteoSensorMeas['Temperature']
		temp_F = LOOKinRemote.celsius2Fahrenheit(meteoSensorMeas['Temperature'])
		humidityRel = meteoSensorMeas['Humidity']
		print(f'{dev!s} is reporting: {temp_C}°C/{temp_F:0.1f}°F and {humidityRel}%RH')
	dev = LOOKinRemote('192.168.1.197', auxDataFilePath)
	remoteUUID = '4012'  #ID of the IR remote on the LOOKin Remote.
	newIRFunction = IRRemoteFunction.fromIRSensor(dev, 'on_heatmode_75F_auto_fullswing')  #The "Learn IR Command" routine.
	if newIRFunction is not None:  #Capture was successful.
		try:  #The LOOKin Remote can get unstable during captures of long IR sequences, throwing connection errors.
			remote = dev.remoteFromUUID(remoteUUID)
			remote.functionUpdate(newIRFunction)
		except:  #Dump the JSON on error so it can be manually added and all that effort isn't lost.
			print(f'ERROR while saving function:  newIRFunction = {newIRFunction.toJSON()!r}')
