#!/usr/bin/env python3

""" read data from GTIL2 Wifi module
    and send it to influxdb server
"""

#
# crontab
#
# */5 * * * * /usr/bin/python3 /home/pi/gtil_influx.py
#

import requests
from requests.auth import HTTPBasicAuth
from influxdb import InfluxDBClient

# GTIL invertor WiFi IP
gtil_ip = '192.168.2.205'

# influx db config
db = InfluxDBClient('192.168.2.4', 8089, use_udp=True, udp_port=8089, database='malina')
measurement = 'gtil2'


def read_gtil_data():
  """ read data from GTIL2 Wifi module """

  gtil_data = dict()

  response = requests.get(
      'http://' + gtil_ip + '/status.html',
      auth=HTTPBasicAuth('admin', 'admin'))
  for line in response.text.splitlines():
    # var webdata_sn = "1905100904";
    if line.startswith('var webdata'):
      key, value = line[12:-1].split("=")
      gtil_data[key.strip()] = value.strip().replace('"', '')

  # print(gtil_data)
  return gtil_data

def send_data_to_influx(gtil_data):
  """ send data to influxdb """
  json_body = {
      "tags": {
          "sn": gtil_data['sn'],
      },
      "points": [{
          "measurement": measurement,
          "fields": {
              "active_power": int(gtil_data['now_p']),
              "today_energy": float(gtil_data['today_e']),
              "total_energy": float(gtil_data['total_e'])
          }
      }]
    }

  db.send_packet(json_body)


def main():
  """Main()"""

  gtil_data = read_gtil_data
  send_data_to_influx(gtil_data)


if __name__ == "__main__":
  main()
