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
import datetime
import ipaddress
import json
import socket
import sys
import time
import urllib.parse
import urllib.request




class LOOKinRemote:

	def __init__(self, networkAddress):
		"""
		Constructor.  `networkAddress` should be either the IP Address or DNS
		Address for the target device.
		"""
		self._address = networkAddress
		
	# @classmethod
	# def findInNetwork(cls):
		#Can't get this to work at all.  :(
		# #### Looks like "LOOK.in:Discover!" isn't working with the current firmware.  Devices aren't responding even to the Android app.
		# # """
		# # Uses the UDP multicast query to find LOOKinRemote devices on the
		# # network.
		# # """
		# MCAST_GRP = '192.168.1.255'
		# MCAST_PORT = 9760
		# MULTICAST_TTL = 1
		# # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		# # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		# # s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
		# message = b'LOOK.in:Discover!'
		# # multicast_group = ('192.168.1.255', 12345)
		# # # s.sendto(message, ('192.168.1.197', 61201))    # Create the socket
		# # s.sendto(message, multicast_group)import socket
		# # import struct
		# # IS_ALL_GROUPS = False
		# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		# # sock.sendto(message, (MCAST_GRP, MCAST_PORT))
		# # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
		# # if IS_ALL_GROUPS:
			# # on this port, receives ALL multicast groups
		# # sock.bind(('', MCAST_PORT))
		# # else:
			# # on this port, listen ONLY to MCAST_GRP
		# sock.bind(('192.168.1.67', MCAST_PORT + 1))
		# # mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
		# # sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		# print(sock.recv(1))

	def device(self):
		"""
		Returns the "device" information.
		"""
		return json.loads(self._get('device'))

	def deviceSet(
			self,
			name=None,
			timeVal=None,
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
			resp = self._post('device', **kargs)
			timeout = time.time() + 30
			while(time.time() < timeout):
				time.sleep(5)  #The command takes a few seconds to process even when it works well.
				deviceInfo = self.device()
				for (key, valExp) in kargs.items():
					if deviceInfo.get(key) != valExp:
						break
				else:
					return
			print(f'Timed Out Attempt {tryNum + 1} of {retries}...')
		else:
			raise TimeoutError(f'FAILED to set device parameters!')

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
		), timeout=10)
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
		resp = urllib.request.urlopen(url, timeout=30)
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
			timeout=10,
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

	def sensorDump(self, name, period, duration):
		"""
		Polls the `name` sensor for `duration` seconds and `period` seconds
		between calls.
		
		Use `period` of `<=0` seconds to poll as fast as possible.
		"""
		print(f'Running sensor dump for {duration} seconds...')
		timeStop = time.time() + duration
		timeNext = 0
		while time.time() < timeStop:
			if time.time() > timeNext:
				if period > 0:
					timeNext = time.time() + period  #BEFORE calling so duration of call is included.
				try:
					print(self.sensor(name))
				except (ConnectionResetError, socket.timeout):
					print('Connection Reset!')
					if name == 'IR':
						print('NOTE: The device can crash if it receives too much IR data at once.')
			if period > 0:
				time.sleep(max(0, time.time() - timeNext))
		print(f'...Sensor dump finished.')

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
		Alias for `LOOKinRemote.remotes` to match the API call.
		"""
		return self.remotes()

	def remotes(self):
		"""
		Returns the remote's saved IR remotes.
		"""
		rootsData = json.loads(self._get('data'))
		remotes = []
		for rootData in rootsData:
			remotes.append(self._remoteGet(rootData, self.remoteData(rootData["UUID"])))
		return remotes

	def remoteData(self, uuid):
		"""
		Returns the data specific to the remote with the given `uuid`.
		"""
		return json.loads(self._get(f'data/{uuid}'))

	def _remoteGet(self, rootData, remoteData):
		"""
		Returns the appropriate `IRRemote` object for the given data.
		`rootData` is the remote's data from "data/" and `remoteData` is the
		remote's data from "data/<UUID>".
		"""
		typeID = rootData['Type']
		ret = None
		if typeID == 'EF':
			ret = LOOKinRemote.ACRemote(self, rootData, remoteData)
		else:
			ret = LOOKinRemote.IRRemote(self, rootData, remoteData)
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

		def __init__(self, lookinRemote, rootData, remoteData):
			"""
			Constructor initializing the object.  `rootData` is the remote's
			data from "data/" and `remoteData` is the remote's data from
			"data/<UUID>".
			"""
			print(remoteData)
			self._lookinRemote = lookinRemote
			self._rootData = rootData
			self._remoteData = remoteData
			self._uuid = self._rootData['UUID']
			self._name = self._remoteData['Name']
			self._typeID = self._rootData['Type']
			self._typeName = LOOKinRemote.IRRemote.types.get(self._typeID, self._typeID)
			self._updated = datetime.datetime.fromtimestamp(int(self._rootData['Updated']), datetime.timezone.utc)
			self._functions = self._remoteData.get('Functions')

		def __repr__(self):
			return repr((self._rootData, self._remoteData))

		def __str__(self):
			return f'{self._uuid} - {self._typeName} Remote'

	class ACRemote(IRRemote):

		class OPERATINGMODE(Enum):
			OFF = 0x0000
			AUTO = 0x1000
			COOL = 0x2000
			HEAT = 0x3000
			DRY = 0x4000  #Supposed to be "Dry" mode, but doesn't work.
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
				if isinstance(operatingMode, str):
					operatingMode = LOOKinRemote.ACRemote.OPERATINGMODE[operatingMode]
				elif isinstance(operatingMode, int):
					operatingMode = LOOKinRemote.ACRemote.OPERATINGMODE(operatingMode)
				if not isinstance(operatingMode, LOOKinRemote.ACRemote.OPERATINGMODE):
					raise ValueError(f'Unexpected data type for `operatingMode`: {type(operatingMode)}')
				self.operatingMode = operatingMode

			def tempTargetSet(self, tempTarget_C):
				if (31 < tempTarget_C or 16 > tempTarget_C):
					raise ValueError('Only temperatures between 16°C and 31°C are supported.')
				tempTarget_C = min(31, max(16, int(tempTarget_C)))
				self.tempTarget_C = tempTarget_C
				self.tempTarget_F = (tempTarget_C * 9 / 5) + 32

			def tempTargetSet_F(self, tempTarget_F):
				self.tempTargetSet((tempTarget_F - 32) * 5 / 9)

			def toStatusBytes(self):
				"""
				Returns the 16-bit integer with the appropriate status bytes for this object.
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
				if isinstance(fanSpeedMode, str):
					fanSpeedMode = LOOKinRemote.ACRemote.FANSPEEDMODE[fanSpeedMode]
				elif isinstance(fanSpeedMode, int):
					fanSpeedMode = LOOKinRemote.ACRemote.FANSPEEDMODE(fanSpeedMode)
				self.fanSpeedMode = fanSpeedMode
				
			def __str__(self):
				return f'ACStatus({self.operatingMode.name}, {self.tempTarget_C}°C, {self.fanSpeedMode.name}, {self.swingMode.name})'

			def swingModeSet(self, swingMode):
				if isinstance(swingMode, str):
					swingMode = LOOKinRemote.ACRemote.SWINGMODE[swingMode]
				elif isinstance(swingMode, int):
					swingMode = LOOKinRemote.ACRemote.SWINGMODE(swingMode)
				self.swingMode = swingMode

		def __init__(self, *args, **kargs):
			super().__init__(*args, **kargs)
			self._remoteDataSet(self._remoteData)

		def __str__(self):
			return f'{self._uuid} - {self._typeName} Remote: Status={hex(self._status.toStatusBytes())}; LastStatus={hex(self._statusLast.toStatusBytes())}'

		def operatingModeSet(self, operatingMode):
			"""
			Tells the device to use operate in `operatingMode`.
			"""
			self._status.operatingModeSet(operatingMode)
			self.statusSet(self._status)

		def tempSet(self, temp_C):
			"""
			Tells the device to use target the Celsius temperature `temp_C`.
			"""
			self._status.tempTargetSet(temp_C)
			self.statusSet(self._status)

		def tempSetF(self, temp_F):
			"""
			Tells the device to use target the Fahrenheit temperature `temp_F`.
			"""
			return self.tempSet((temp_F - 32) * 5 / 9)

		def fanSpeedModeSet(self, fanSpeedMode):
			"""
			Tells the device to use `fanSpeedMode`.
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
			"""
			self._status.swingModeSet(operatingMode)
			self.statusSet(self._status)

		def statusGet(self, refresh=False):
			"""
			Returns the current status of the device.
			"""
			if refresh:
				self.statusRefresh()
			return self._status

		def statusRefresh(self):
			"""
			Requests the current status from the device.
			"""
			self._remoteDataSet(self._lookinRemote.remoteData(self._uuid))

		def statusSet(self, status):
			"""
			Modifies the device's status to match `status`.
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

if __name__ == '__main__':
	# LOOKinRemote.findInNetwork()  #Can't get this to work right now...
	if len(sys.argv) > 1:
		ipAddr = sys.argv[1]
	else:
		raise ValueError('Please supply an IP/DNS address as the first command line argument e.g. `py pylookinremote2.py 192.168.0.123`.')
	dev = LOOKinRemote(ipAddr);
	print(f'device = {dev.device()}')
	# if 0:
		# print('Testing!')
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
	# dev.sensorDump('IR', 0, 20)
	# print(f'commands = {dev.commands()}')
	# for command in dev.commands():
		# print(f'commandEvents/{command} = {dev.commandEvents(command)}')
	# remotes = dev.remotes()
	# print(f'remotes = {list(str(remote) for remote in remotes)}')
	# for remote in remotes:
		# if isinstance(remote, LOOKinRemote.ACRemote):
			# remote.statusSet(LOOKinRemote.ACRemote.Status('COOL', 23, 'AUTO', 'UNKNOWN00'))
