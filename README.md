# MQTT Announcement System
This is a project for announcing messages received over MQTT using text to speech.

## Getting Started

### Installing

Running this project requires having the "espeak" package installed.

### Running mqtt-announce

The server subscribes to a specified MQTT topic and speaks the message using espeak. By default will connect to the localhost on the default MQTT port. You can specify a different host and port using the "--host" and "--port" parameters. If your MQTT server requires a username and password that can be specified using the "-username" and "--password" parameter. If your MQTT server is using TLS you can specify the CA certificate using the "--ca_cert" parameter. The server will subscribe to the "announce" topic by default but this can be changed using the "--topic" parameter.

Example:
```
python mqtt-announce.py --host=mqtt.example.com --username=announce --password=changeme --topic=example/announce
```

### Running on a raspberry pi

This was originally developed for use on a raspberry pi with the HifiBerry sound card installed. In order to allow multiple applications to play sound at the same time follow the instructions found here https://support.hifiberry.com/hc/en-us/articles/207397665-Mixing-different-audio-sources.
