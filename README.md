# DHCP2MQTT

Just a simple script to listen for DHCP multicast discover packets and broadcast over MQTT. Intended to be integrated into HomeAssistant for faster presence detection. Most network detection relies on polling router client lists, and this will fire as soon as your device connects to wifi.

## Running in Docker
Container must be run with host networking in order to receive multicast packets.
```
docker run --rm --net=host -e MQTT_HOST=mqtt.server.com -e MACS_TO_MONITOR=ab:cd:e1:23:45:67,aa:aa:aa:aa:aa:aa blakeblackshear/dhcp2mqtt:latest
```

## Environment Variables
|Name|Required|Default|Description|
|----|--------|-------|-----------|
|MACS_TO_MONITOR|Yes||Comma separated list of mac addresses to watch|
|MQTT_HOST|Yes||Host or IP of MQTT server|
|MQTT_PORT|No|1883|Port of MQTT server|
|MQTT_USER|No||MQTT user if set|
|MQTT_PASS|No||MQTT password if set|
|MQTT_TOPIC_PREFIX|No|network/dhcp|Topic prefix for MQTT messages|
|MQTT_CLIENT_ID|No|dhcp2mqtt|Client id for mqtt connection|

## MQTT Messages
Messages are posted to MQTT when a discover packet is detected:
```
network/dhcp/ab:cd:e1:23:45:67 discover
```