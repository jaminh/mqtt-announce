import sys
import argparse
import logging
import string
import re
from time import sleep
import signal
from subprocess import call
import paho.mqtt.client as mqttClient

logger = logging.getLogger(__name__)

class MqttAnnounce:

	ESPEAK_OPTS = "-ven-us"

	def __init__(self, host="127.0.0.1", port=1883, user="mqtt-announce", password=None, ca_cert=None, topic="announce"):
		self.client = mqttClient.Client("MqttAnnounce")
		self.client.username_pw_set(user, password=password)
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect
		self.client.on_message = self.on_message
		self.Connected = False
		self.host = host
		self.port = port
		self.ca_cert = ca_cert
		self.topic = topic 
		self.stop = False
		signal.signal( signal.SIGINT, lambda signal, frame: self.__stop() )

	def mainLoop(self):
		if (self.ca_cert is not None):
			self.client.tls_set(self.ca_cert)
		self.client.connect(self.host, port=self.port)
		self.client.loop_start()
		while (not self.stop and not self.Connected):
			logger.debug("MQTT Connecting")
			sleep(0.1)
		if (self.Connected):
			logger.info("MQTT connected")
			self.client.subscribe(self.topic)
		else:
			logger.warn("Error connecting to MQTT")

		while(not self.stop):
			if (not self.Connected):
				sleep(5)
				if (not self.stop):
					self.client.reconnect()
			sleep(1)
	
	def on_connect(self, client, userdata, flags, rc):
		logger.debug("Attempted to connect to MQTT")
		if rc == 0:
			logger.debug("Connected to broker")
			self.Connected = True                #Signal connection 
		else:
			logger.warn("Connection failed" + mqttClient.connack_string(rc))

	def on_disconnect(self, client, userdata, rc):
		logger.info("MQTT disconnected " + mqttClient.connack_string(rc))
		self.Connected = False                #Signal disconnection 

	def on_message(self, client, userdata, message):
		command = 'espeak '+ self.ESPEAK_OPTS + ' "' + self.clean_message(message) + '" --stdout | aplay 2>/dev/null'
		logger.debug(command)
		call([command], shell=True)

	def clean_message(self, message):
		return re.sub('[\W ]', ' ', str(message.payload.decode('utf-8')))

	def __stop(self):
		logger.debug("Stop requested")
		self.client.disconnect()
		self.client.loop_stop()
		self.stop = True

# #################################################################################
#
#
#
# #################################################################################

parser = argparse.ArgumentParser("MQTT Announcement System");
parser.add_argument("--host", dest="host", default="127.0.0.1", help="Hostname or IP address of the MQTT server, defaults to localhost (127.0.0.1)")
parser.add_argument("--port", dest="port", default=1883, help="Port number used by MQTT, defaults to 1883")
parser.add_argument("--user", dest="user", default="mqtt-announce", help="User to connect to MQTT as, defaults to \"mqtt-announce\"")
parser.add_argument("--password", dest="password", default=None, help="Password used to connect to MQTT if one is required, defaults to None")
parser.add_argument("--ca_cert", dest="ca_cert", default=None, help="CA certificate if connecting with TLS, defaults to None")
parser.add_argument("--topic", dest="topic", default="announce", help="Topic to listen on, defaults to \"announce\"")
parser.add_argument("-v", dest="info", default=False, action="store_true", help="Enable verbose logging")
parser.add_argument("-vv", dest="debug", default=False, action="store_true", help="Enable very verbose logging")

args = parser.parse_args()

if (args.info):
	logging.basicConfig(level=logging.INFO)
if (args.debug):
	logging.basicConfig(level=logging.DEBUG)

app = MqttAnnounce(host=args.host, port=int(args.port), user=args.user, password=args.password, ca_cert=args.ca_cert, topic=args.topic)
app.mainLoop()

logger.info("MQTT Announcement System stopped")
sys.exit(0)
