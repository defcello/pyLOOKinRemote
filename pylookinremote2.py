#! /usr/bin/python3.8

import datetime
import ipaddress
import json
import urllib.parse
import urllib.request




DEVICE_ADDR = '192.168.123.456'

class LOOKinRemote2:

	def __init__(self, networkAddress):
		"""
		Constructor.  `networkAddress` should be either the IP Address or DNS
		Address for the target device.
		"""
		self._address = networkAddress

	def device(self):
		"""
		Returns the "device" information.
		"""
		return json.loads(self._get('device'))

	def deviceSet(
			self,
			name=None,
			time=None,
			timezone=None,
			sensormode=None,
			bluetoothmode=None,
			# firmware=None,  #This should only be modified by official software.
	):
		"""
		Sets the "device" values.  `None` parameters will not be modified.
		"""
		kargs = {}
		if name is not None:
			kargs['name'] = name
		if time is not None:
			kargs['time'] = time
		if timezone is not None:
			kargs['timezone'] = timezone
		if sensormode is not None:
			kargs['sensormode'] = sensormode
		if bluetoothmode is not None:
			kargs['bluetoothmode'] = bluetoothmode
		# if firmware is not None:
			# kargs['firmware'] = firmware
		return self._post('device', **kargs)

	def _del(self, path):
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
		))
		return resp.read()

	def _get(self, path, **kargs):
		"""
		Issues GET request to API with `path`.  `kargs` will be added as parameters.
		"""
		url = urllib.parse.SplitResult(
			'http',
			self._address,
			path,
			urllib.parse.urlencode(kargs),
			'',
		).geturl()
		print(f'_get - url={url!r}')
		resp = urllib.request.urlopen(url)
		return resp.read()

	def _post(self, path, **kargs):
		"""
		Issues POST request to API with `path`.  `kargs` will be transmitted as a JSON document.
		"""
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
		)
		return resp.read()

	def network(self):
		return json.loads(self._get('network'))

	def networkScannedSSIDList(self):
		return json.loads(self._get('network/scannedssidlist'))

	def networkSavedSSID(self):
		return json.loads(self._get('network/SavedSSID'))

	def networkAdd(self, ssid, password):
		"""
		Adds the network `ssid` and `password` to the remote's internal list of
		supported WiFi hotspots.
		"""
		return json.loads(self._post('network', WiFiSSID=ssid, WiFiPassword=password))

	def networkDel(self, ssid):
		"""
		Deletes the network `ssid` from the remote's internal list of supported
		WiFi hotspots.
		"""
		return json.loads(self._del(f'network/savedssid/{urllib.parse.quote_plus(ssid)}'))

	def networkConnect(self, ssid=None):
		"""
		Tells the remote to connect to `ssid`, or the strongest available WiFi
		if `ssid` is `None`.
		"""
		kargs = {}
		if (ssid is not None):
			kargs['ssid'] = ssid
		return json.loads(self._get('network/connect', **kargs))

	def networkKeepWifi(self):
		"""
		Tells the remote to keep the WiFi connection while "sensor mode" is on.
		"""
		return json.loads(self._get('network/keepwifi'))

	def networkRemoteControlStop(self):
		"""
		Tells the remote to use the "stop" RemoteControl state.
		"""
		return json.loads(self._get('network/remotecontrol/stop'))

	def networkRemoteControlReconnect(self):
		"""
		Tells the remote to use the "reconnect" RemoteControl state.
		"""
		return json.loads(self._get('network/remotecontrol/reconnect'))

	def sensorNames(self):
		"""
		Returns the remote's available sensors.
		"""
		return json.loads(self._get('sensors'))

	def sensor(self, name):
		"""
		Returns the remote's sensor information.
		"""
		return json.loads(self._get(f'sensors/{urllib.parse.quote_plus(name)}'))

	def commands(self):
		"""
		Returns the remote's available command classes.
		"""
		return json.loads(self._get('commands'))

	def commandEvents(self, command):
		"""
		Returns the remote's available events for `command`.
		"""
		return json.loads(self._get(f'commands/{urllib.parse.quote_plus(command)}'))

	"""
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

	def data(self):
		"""
		Alias for `LOOKinRemote2.remotes` to match the API call.
		"""
		return self.remotes()

	def remotes(self):
		"""
		Returns the remote's saved IR remotes.
		"""
		rootsData = json.loads(self._get('data'))
		remotes = []
		for rootData in rootsData:
			remotes.append(self._remoteGet(rootData, json.loads(self._get(f'data/{rootData["UUID"]}'))))
		return remotes

	def _remoteGet(self, rootData, remoteData):
		"""
		Returns the appropriate `IRRemote` object for the given data.
		`rootData` is the remote's data from "data/" and `remoteData` is the
		remote's data from "data/<UUID>".
		"""
		typeID = rootData['Type']
		ret = None
		if typeID == 'EF':
			ret = LOOKinRemote2.ACRemote(rootData, remoteData)
		else:
			ret = LOOKinRemote2.IRRemote(rootData, remoteData)
		return ret

	class IRRemote:

		types = {
			'00': 'Custom',
			'01': 'TV',
			'02': 'Media',
			'03': 'Light',
			'04': 'Humidifier/Dehumidifier',
			'05': 'Air Purifier',
			'06': 'Robo Vacuum Cleaner',
			'07': 'Data Device Fan',
			'EF': 'Air Conditioner',
		}

		def __init__(self, rootData, remoteData):
			"""
			Constructor initializing the object.  `rootData` is the remote's
			data from "data/" and `remoteData` is the remote's data from
			"data/<UUID>".
			"""
			self._rootData = rootData
			self._remoteData = remoteData
			self._uuid = self._rootData['UUID']
			self._name = self._remoteData['Name']
			self._typeID = self._rootData['Type']
			self._typeName = LOOKinRemote2.IRRemote.types.get(self._typeID, self._typeID)
			self._updated = datetime.datetime.fromtimestamp(int(self._rootData['Updated']), datetime.timezone.utc)
			self._functions = self._remoteData.get('Functions')

		def __repr__(self):
			return repr((self._rootData, self._remoteData))

		def __str__(self):
			return f'{self._uuid} - {self._typeName} Remote'

	class ACRemote(IRRemote):

		operatingModes = {
			'OFF': 0x0000,
			'AUTO': 0x1000,
			'COOL': 0x2000,
			'HEAT': 0x3000,
		}

		fanModes = {
			'AUTO': 0x00A0,
		}

		swingModes = {
			'HORIZONTAL': 0x000C,
			'VERTICAL': 0x000D,
		}

		def __init__(self, rootData, remoteData):
			super().__init__(rootData, remoteData)
			print(remoteData)
			self._extra = self._remoteData.get('Extra')
			if 'Status' in self._remoteData:
				self._status = int(self._remoteData['Status'], 16)
			else:
				self._status = 0x0A8C
			if 'LastStatus' in self._remoteData:
				self._statusLast = int(self._remoteData['LastStatus'], 16)
			else:
				self._statusLast = 0x0A8D

		def __str__(self):
			return f'{self._uuid} - {self._typeName} Remote: Status={hex(self._status)}; LastStatus={hex(self._statusLast)}'

		def operatingModeSet(self, lookinRemote2, operatingMode):
			operatingModeBits = LOOKinRemote2.ACRemote.operatingModes[operatingMode]
			newStatus = (self._status & ~0xF000) | operatingModeBits
			lookinRemote2._get(f'commands/ir/ac/{self._extra}{newStatus:04X}')

		def tempSet(self, lookinRemote2, temp_C):
			temp_C = min(31, max(16, int(temp_C)))
			newStatus = (self._status & ~0x0F00) | ((temp_C - 16) << 8)
			lookinRemote2._get(f'commands/ir/ac/{self._extra}{newStatus:04X}')

		def tempSetF(self, lookinRemote2, temp_F):
			return self.tempSet(lookinRemote2, (temp_F - 32) * 5 / 9)

		def fanModeSet(self, lookinRemote2, fanMode):
			fanModeBits = LOOKinRemote2.ACRemote.fanModes[fanMode]
			newStatus = (self._status & ~0x00F0) | fanModeBits
			lookinRemote2._get(f'commands/ir/ac/{self._extra}{newStatus:04X}')

		def swingModeToggle(self, lookinRemote2, swingMode):
			swingModeBits = LOOKinRemote2.ACRemote.swingModes[swingMode]
			newStatus = (self._status & ~0xF) | swingModeBits
			lookinRemote2._get(f'commands/ir/ac/{self._extra}{newStatus:04X}')

		def statusSet(self, lookinRemote2, operatingMode, temp_C, fanMode, swingMode):
			operatingModeBits = LOOKinRemote2.ACRemote.operatingModes[operatingMode]
			temp_C = min(31, max(16, int(temp_C)))
			fanModeBits = LOOKinRemote2.ACRemote.fanModes[fanMode]
			swingModeBits = LOOKinRemote2.ACRemote.swingModes[swingMode]
			newStatus = operatingModeBits | ((temp_C - 16) << 8) | fanModeBits | swingModeBits
			# import pdb; pdb.set_trace()
			lookinRemote2._get(f'commands/ir/ac/{self._extra}{newStatus:04X}')

if __name__ == '__main__':
	print('Testing!')
	dev = LOOKinRemote2(DEVICE_ADDR);
	# print(f'device = {dev.device()}')
	# nameOrig = dev.device()['Name']
	# nameExp = 'TESTING123'
	# dev.deviceSet(nameExp)
	# if (dev.device()['Name'] != nameExp):
		# print('FAILED to set "Name" on device.')
	# dev.deviceSet(nameOrig)
	# if (dev.device()['Name'] != nameOrig):
		# print('FAILED to restore "Name" on device.')
	# print(f'sensorNames = {dev.sensorNames()}')
	# for sensorName in dev.sensorNames():
		# print(f'sensors/{sensorName} = {dev.sensor(sensorName)}')
	# print(f'commands = {dev.commands()}')
	# for command in dev.commands():
		# print(f'commandEvents/{command} = {dev.commandEvents(command)}')
	remotes = dev.remotes()
	print(f'remotes = {list(str(remote) for remote in remotes)}')
	for remote in remotes:
		if isinstance(remote, LOOKinRemote2.ACRemote):
			remote.statusSet(dev, 'COOL', 23, 'AUTO', 'HORIZONTAL')
			# remote.operatingModeSet(dev, 'COOL')
			# remote.tempSet(dev, 23)
			# remote.swingModeToggle(dev)
