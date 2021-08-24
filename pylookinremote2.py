#! /usr/bin/python3.8

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

if __name__ == '__main__':
	print('Testing!')
	dev = LOOKinRemote2(DEVICE_ADDR);
	print(f'device = {dev.device()}')
	nameOrig = dev.device()['Name']
	nameExp = 'TESTING123'
	dev.deviceSet(nameExp)
	if (dev.device()['Name'] != nameExp):
		print('FAILED to set "Name" on device.')
	dev.deviceSet(nameOrig)
	if (dev.device()['Name'] != nameOrig):
		print('FAILED to restore "Name" on device.')
	print(f'sensorNames = {dev.sensorNames()}')
	for sensorName in dev.sensorNames():
		print(f'sensors/{sensorName} = {dev.sensor(sensorName)}')
	print(f'commands = {dev.commands()}')
	for command in dev.commands():
		print(f'commandEvents/{command} = {dev.commandEvents(command)}')
