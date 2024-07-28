#!/usr/bin/python3
# Creator: Thiemo Schuff
# Source: https://github.com/Starwhooper/RPi-deyesun600-to-mqtttls

#######################################################
#
# prepare
#
#######################################################


##### check if all required packages are aviable
import sys
try:
 from urllib.parse import quote
 import json
 import os
 import requests
 import re
 import time
 import random
 import paho.mqtt.client as paho
 from paho import mqtt
 import datetime
except:
 sys.exit("\033[91m {}\033[00m" .format('any needed package is not aviable. Please check README.md to check which components should be installed via pip3".'))

#set const
globals()['scriptroot'] = os.path.dirname(__file__)

###### import config.json
try:
 with open(scriptroot + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + scriptroot + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required '))

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def inverterurl():
 url = 'http://' + cf['inverter']['user'] + ':' + quote(cf['inverter']['pw']) + '@' + cf['inverter']['address'] + '/' + cf['inverter']['site']
 return(url)

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(cf['mqtt']['broker']['user'], cf['mqtt']['broker']['pw'])
client.connect(cf['mqtt']['broker']['url'], cf['mqtt']['broker']['port'])
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish


#client.subscribe("raspberry/#", qos=1)


#######################################################
#
# start
#
#######################################################
 
def main():
 while True:
  try:  
   inverterread = False
   
   try: oldstate
   except: oldstate = ''
   try: oldsensor
   except: oldsensor = ''
   
   for i in range(5):
    try:
     inverter = requests.get(inverterurl(), timeout=2)
     if inverter.status_code == 200: 
      inverterread = True
      break
    except:
     pass
  
 
   if inverterread == False:
    print('publish offline msg')
    client.publish("raspberry-pv/LWT", payload="Offline", qos=cf['mqtt']['qos'])
    client.publish("raspberry-pv/UTC-Time", payload=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S"), qos=cf['mqtt']['qos'])
    print('inverter ' + inverterurl() + ' cloud not read, wait 5 sec')
    time.sleep(cf['inverter']['retry'])
   
   else:
    print('read')
    #var webdata_sn = "2211051851                             ";
    try:
     webdata_sn = str(re.search(r'var\s+webdata_sn\s*=\s*"([^"]+)"', inverter.text).group(1)).strip()
    except:
     webdata_sn = ''
    
 #  webdata_msvn = "                                       ";
    try:
     webdata_msvn = str(re.search(r'var\s+webdata_msvn\s*=\s*"([^"]+)"', inverter.text).group(1)).strip()
    except:
     webdata_msvn = ''
 
 #  webdata_ssvn = "                                       ";    
    try:
     webdata_ssvn = str(re.search(r'var\s+webdata_ssvn\s*=\s*"([^"]+)"', inverter.text).group(1)).strip()
    except:
     webdata_ssvn = ''
 
 #  webdata_pv_type = "";    
    try:
     webdata_pv_type = str(re.search(r'var\s+webdata_pv_type\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_pv_type = ''
     
 #  webdata_rate_p = "";
    try:
     webdata_rate_p = str(re.search(r'var\s+webdata_rate_p\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_rate_p = ''
 
 #  webdata_now_p = "22";
    try:    
     webdata_now_p = int(re.search(r'var\s+webdata_now_p\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_now_p = 0
     
 #  webdata_today_e = "0.0";
    try: 
     webdata_today_e = float(re.search(r'var\s+webdata_today_e\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_today_e = 0.0
 
 #  webdata_total_e = "910.3";    
    try:
     webdata_total_e = float(re.search(r'var\s+webdata_total_e\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_total_e = 0.0
 
 #  webdata_alarm = "";
    try:
     webdata_alarm = str(re.search(r'var\s+webdata_alarm\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_alarm = ''
 
 #  webdata_utime = "0";   
    try:
     webdata_utime = int(re.search(r'var\s+webdata_utime\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     webdata_utime = 0
 
 #  cover_mid = "4164382996";
    try:
     cover_mid = int(re.search(r'var\s+cover_mid\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_mid = 0
     
 #  cover_ver = "MW3_16U_5406_1.62";
    try:
     cover_ver = str(re.search(r'var\s+cover_ver\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_ver = ''
 
 #  cover_wmode = "APSTA";
    try:
     cover_wmode = str(re.search(r'var\s+cover_wmode\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_wmode = ''
 
 #  cover_ap_ssid = "AP_4164382996";
    try:
     cover_ap_ssid = str(re.search(r'var\s+cover_ap_ssid\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_ap_ssid = ''
 
 #  cover_ap_ip = "10.10.100.254";
    try:
     cover_ap_ip = str(re.search(r'var\s+cover_ap_ip\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_ap_ip = ''
     
 #  cover_ap_mac = "EC:FD:F8:76:9A:AA";
    try:
     cover_ap_mac = str(re.search(r'var\s+cover_ap_mac\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_ap_mac = ''
 
 #  cover_sta_ssid = "Schuff";
    try:
     cover_sta_ssid = str(re.search(r'var\s+cover_sta_ssid\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_sta_ssid = ''
 
 #  cover_sta_rssi = "33%";
    try:
     cover_sta_rssi = int(re.search(r'var\s+cover_sta_rssi\s*=\s*"([^"]+)%', inverter.text).group(1))
    except:
     cover_sta_rssi = 0
 
 #  cover_sta_ip = "192.168.179.2";
    try:
     cover_sta_ip = str(re.search(r'var\s+cover_sta_ip\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_sta_ip = ''
 
 #  cover_sta_mac = "E8:FD:F8:76:9A:AA";
    try:
     cover_sta_mac = str(re.search(r'var\s+cover_sta_mac\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     cover_sta_mac = ''
     
 #  status_a = "1";
    try:
     status_a = int(re.search(r'var\s+status_a\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     status_a = 0
 
 #  status_b = "0";
    try:
     status_b = int(re.search(r'var\s+status_b\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     status_b = 0
 
 #  status_c = "0";
    try:
     status_c = int(re.search(r'var\s+status_c\s*=\s*"([^"]+)"', inverter.text).group(1))
    except:
     status_c = 0
 
    state = {
     "webdata":{
      "webdata_sn": webdata_sn,
      "webdata_msvn": webdata_msvn,
      "webdata_ssvn": webdata_ssvn,
      "webdata_pv_type": webdata_pv_type
     },
     "cover":{
      "cover_mid": cover_mid,
      "cover_ver": cover_ver,
      "cover_wmode": cover_wmode
     },
     "Wifi":{
      "AP":{
       "cover_ap_ssid": cover_ap_ssid,
       "cover_ap_ip": cover_ap_ip,
       "cover_ap_mac": cover_ap_mac
      },
      "Status":{
       "cover_sta_ssid": cover_sta_ssid,
       "cover_sta_rssi": cover_sta_rssi,
       "cover_sta_ip": cover_sta_ip,
       "cover_sta_mac": cover_sta_mac
      }
     },
     "Status":{
      "A": status_a,
      "B": status_b,
      "C": status_c
     }
    }
 
    sensor = {
     "webdata_rate_p": webdata_rate_p,
     "webdata_now_p": webdata_now_p,
     "webdata_today_e": webdata_today_e,
     "webdata_total_e": webdata_total_e,
     "webdata_alarm": webdata_alarm,
     "webdata_utime": webdata_utime
    }
    
    if sensor != oldsensor:
     oldsensor = sensor
     dumpsensor = json.dumps(sensor)
     print('sensor publish')
     try: client.publish("raspberry-pv/SENSOR", payload=dumpsensor, qos=cf['mqtt']['qos'])
     except: print('send to broker issue')
    else:
     print('sensor skip')
 
    if state != oldstate:
     oldstate = state
     dumpstate = json.dumps(state)
     print('state publish')
     try: client.publish("raspberry-pv/STATE", payload=dumpstate, qos=cf['mqtt']['qos'])
     except: print('send to broker issue')
    else:
     print('state skip')
    
    try: client.publish("raspberry-pv/LWT", payload="Online", qos=cf['mqtt']['qos'])
    except: print('send to broker issue')
    
    try: client.publish("raspberry-pv/UTC-Time", payload=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S"), qos=cf['mqtt']['qos'])
    except: print('send to broker issue')
    
    time.sleep(cf['calculationrefresh'])

  except: print('unknown issue')
  
if __name__ == '__main__':
 try:
  main()
 except KeyboardInterrupt:
  sys.exit('interrupt via ctrl+c')
 
