FROM alpine:3.11

RUN apk add --no-cache python3 tcpdump

RUN pip3 install -U scapy paho-mqtt

COPY dhcp2mqtt.py .

CMD ["python3", "-u", "dhcp2mqtt.py"]