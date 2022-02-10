import os
import sys
import time
from scapy.all import *
import paho.mqtt.client as mqtt

MACS_TO_MONITOR = os.getenv('MACS_TO_MONITOR')
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = os.getenv('MQTT_PORT', 1883)
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', 'network/dhcp')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'dhcp2mqtt')

if MQTT_HOST is None:
    sys.exit("No MQTT_HOST environment variable set")
if MACS_TO_MONITOR is None:
    sys.exit("No MACS_TO_MONITOR environment variable set")

macs = MACS_TO_MONITOR.lower().split(',')
debounce_log = {}

print(f"Monitoring discover packets from: {macs}")

# connect to mqtt and setup last will
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected")
    if rc != 0:
        if rc == 3:
            print ("MQTT Server unavailable")
        elif rc == 4:
            print ("MQTT Bad username or password")
        elif rc == 5:
            print ("MQTT Not authorized")
        else:
            print ("Unable to connect to MQTT: Connection refused. Error code: " + str(rc))
    # publish a message to signal that the service is running
    client.publish(MQTT_TOPIC_PREFIX+'/available', 'online', retain=True)

client = mqtt.Client(client_id=MQTT_CLIENT_ID)
client.on_connect = on_connect
client.will_set(MQTT_TOPIC_PREFIX+'/available', payload='offline', qos=1, retain=True)
if not MQTT_USER is None:
    client.username_pw_set(MQTT_USER, password=MQTT_PASS)
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

def handle_dhcp_packet(packet):
    # just look at discovery packets
    if DHCP in packet and packet[DHCP].options[0][1] in [1,3]:
        # see if the requestor is in the list to monitor
        if packet[Ether].src.lower() in macs:
            if packet[Ether].src not in debounce_log or debounce_log[packet[Ether].src] < time.time() - 2:
                debounce_log[packet[Ether].src] = time.time()
                print(f"DHCP Discovery from {packet[Ether].src}")
                client.publish(f"{MQTT_TOPIC_PREFIX}/{packet[Ether].src}", 'discover', retain=False)

    return

if __name__ == "__main__":
    sniff(filter="udp and (port 67 or 68)", prn=handle_dhcp_packet)
