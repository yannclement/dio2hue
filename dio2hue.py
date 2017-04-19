#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------------
#
#                                 DIO 2 HUE
#
#---------------------------------------------------------------------------------


#---------------------------------------------------------------------------------
# VARIABLES
#---------------------------------------------------------------------------------

# IP of Hue bridge
# you must have configured your Hue bridge with a static IP
hue_bridge_address = "http://192.168.1.15/api/"

# your identification on the Hue bridge
# go to http://<Hue brigge IP>/debug/clip.html
# specify /api in URL and {"devicetype": "dio2hue"} in Message Body
# press the button on the bridge and then press the POST button
# retrieve the identifier in "username" and copy it into the hue_bridge_identification variable
hue_bridge_identification = "abCdleF2ghIjKl3M4Op5rST6UVW7xy8zABcDeFg9"

# list of known DiO transmitters
# to retrieve parameters from a transmitter, use the scan option
# python dio2hue.py scan
dio_devices_list = {
# DIO ID:{ ...parameters... }
"ss1":{ "description":"simple switch", "house":"1234567", "group":"0", "unit":"1" },
"ds0_o":{"description":"door switch when open", "house":"9876543", "group":"0", "unit":"0" },
"ds1_c":{ "description":"door switch when closed", "house":"1234567", "group":"0", "unit":"0" },
"ds1_r":{ "description":"double switch (right)", "house":"1122334", "group":"0", "unit":"1" },
"ds1_l":{ "description":"double switch (left)", "house":"1122334", "group":"0", "unit":"2" },

"1":{ "description":"remote", "house":"9988771", "group":"0", "unit":"1" },
"2":{ "description":"remote", "house":"9988771", "group":"0", "unit":"2" },
"13":{ "description":"remote", "house":"9988771", "group":"0", "unit":"13" },

"g":{ "description":"remote", "house":"9988771", "group":"1", "unit":"1" },
}

# list of Hue lights with several possible parameters (ambiences) for each
hue_lights_list = {
# Hue ID:{ ...parameters... }
"hue_1_cold":{"ct":154 },
"hue_1_middle":{ "ct":327 },
"hue_1_warm":{ "ct":500 },

"hue_2_white":{ "red":255, "green":255, "blue":255, "bri":254 },
"hue_2_yellow":{ "red":255, "green":180, "blue":0, "bri":254 },
"hue_2_orange":{ "red":255, "green":77, "blue":0, "bri":254 },
"hue_2_magenta":{ "red":255, "green":0, "blue":255, "bri":254 },
"hue_2_red":{ "red":255, "green":0, "blue":0, "bri":254 },
}

# list allowing to connect a Hue lamp to several parameters (ambiences)
hue_ambiences_list = {
# hue light:[ Hue ID, Hue ID... ],
"1":["hue_1_middle", "hue_1_warm", "hue_1_cold"],
"2":["hue_2_orange", "hue_2_magenta", "hue_2_red", "hue_2_white", "hue_2_yellow"],
}

# list for connecting a DiO transmitter to a Hue lamp
correspondences_table = {
# DIO ID:[ Hue light, Hue light... ],
"1":["1"],
"ss1":["1"],
"2":["2"],
"g":["1", "2"],

"13":["switch_ambience"]
}


## these variables are not to be modified ##

# flag for only scan DiO devices
scan_only = False

# last Hue light
last_hue_light = next(iter(correspondences_table))

# ambience index
ambience_index = {}
for light in hue_ambiences_list:
  ambience_index[light] = 0


#---------------------------------------------------------------------------------
# FUNCTIONS
#---------------------------------------------------------------------------------

# RGB To XV
def RGBToXY(red, green, blue):
  """Color code conversion from RGB to XY"""

  # check inputs
  if red < 0 or blue < 0 or green < 0:
    return 0, 0

  #check inputs
  if red > 255 or blue > 255 or green > 255:
    return 0, 0

  # convert to value between 0 and 1
  red = red / 255.0
  green = green / 255.0
  blue = blue / 255.0

  # calculate
  X = 0.412453 * red + 0.357580 * green + 0.180423 * blue
  Y = 0.212671 * red + 0.715160 * green + 0.072169 * blue
  Z = 0.019334 * red + 0.119193 * green + 0.950227 * blue
  x = X / (X + Y + Z)
  y = Y / (X + Y + Z)

  return x, y

#---

# MY RAW DEVICE EVENT
def myRawDeviceEvent(data, controllerId, callbackId):
  """Callback when a DiO signal is received"""
  print "- device send informations"

  data = data.split(";")

  received_datas = {}

  if len(data) > 0:
    for item in data:
      if len(item) > 0:
        item = item.split(":")
        if len(item) == 2:
          received_datas[item[0]] = item[1]

  returned_datas = {}

  # check the class information
  if "class" in received_datas:
    if received_datas["class"] != "command":
      print "  - not the good class"
      return
  else:
    print "  - no class information"
    return

  # check the house information
  if "house" in received_datas:
    returned_datas["house"] = received_datas["house"]
  else:
    print "  - no house information"
    return

  # check the group information
  if "group" in received_datas:
    returned_datas["group"] = received_datas["group"]
  else:
    print "  - no group information"
    return

  # check the unit information
  if "unit" in received_datas:
    returned_datas["unit"] = received_datas["unit"]
  else:
    print "  - no unit information"
    return

  # check the method information
  if "method" in received_datas:
    returned_datas["method"] = received_datas["method"]
  else:
    print "  - no method information"
    return

  # if scan only
  if scan_only:
    # display informations and return
    print "  - device informations: house: " + returned_datas["house"] + ", group: " + returned_datas["group"] + ", unit: " + returned_datas["unit"] + ", method: " + returned_datas["method"]
    return

  #print returned_datas

  # now we have house, group, unit and method information
  # try to find a correspondant device in the DIO devices list
  dio_device, method = CheckDIODevice(returned_datas)
  if dio_device is False:
    return

  # now we have a identified DIO device
  # try to find a correpondent list of Hue lights
  lights_list = CheckCorrespondences(dio_device)
  if lights_list is False:
    return

  # check if lights_list is a list
  if isinstance(lights_list, list):
    if len(lights_list) > 0:
      # check if it's a call to the special function who switch ambiences
      if lights_list[0] == "switch_ambience":
        SwitchAmbience(last_hue_light, returned_datas["method"])
        return

  # now we have a list of Hue lights
  # we can send the order method to them
  SendToHues(lights_list, method)
  return

#---

# CHECK DiO DEVICE
def CheckDIODevice(data):
  """Comparison between a received DiO signal and a signal known in the list dio_devices_list"""

  print "- check for known DIO devices..."

  for device in dio_devices_list:
    if dio_devices_list[device].has_key("house"):
      if data["house"] == dio_devices_list[device]["house"]:
        if dio_devices_list[device].has_key("group"):
          if data["group"] == dio_devices_list[device]["group"]:
            if dio_devices_list[device].has_key("unit"):
              if data["unit"] == dio_devices_list[device]["unit"]:
                # device found, we return the ID and the method
                print "  - ID: " + device + " (" + dio_devices_list[device]["description"] + ") is the good device"
                return device, data["method"]

  print "  - no device found"
  return False, False

#---

# CHECK CORRESPONDENCES
def CheckCorrespondences(id):
  """Verification of correspondence between a DiO transmitter and one or more Hue lamps"""
  print "- check for correspondence whith Hue devices..."

  if id is False:
    print "  - no id in input datas"
    return False

  if correspondences_table.has_key(id):
    print "  - correspondence found"
    return correspondences_table[id]
  else:
    print "  - no correspondence found"
    return False

#---

# SEND TO HUE
def SendToHues(lights_list, method):
  """Sending the current light parameter to the Hue lamp"""
  global last_hue_light

  print "- send to Hues devices..."

  # check if we have lights_list and method informations
  if lights_list is False or method is False:
    print "  - no input datas"
    return False

  # check if lights_list is a list
  if not isinstance(lights_list, list):
    print "  - this function need a list in input"
    return False

  # convert method on a on/off flag
  if method == "turnon":
    print "  - turn on action"
    method_flag = True
  elif method == "turnoff":
    print "turn off action"
    method_flag = False
  else:
    print "  - bad method: " + method
    return False

  # for etch lights in input list
  for light in lights_list:
    print "  - processing for light " + light + "..."

    request = {}

    # get the state of the light
    state_of_device = GetDeviceState(light)
    if state_of_device is False:
      print "    - light did not respond"
      return False

    # check the on state of the light
    if state_of_device.has_key("on"):
      # we can add the on/off flag if state is different
      if state_of_device["on"] != method_flag:
        request["on"] = method_flag
      # if state is identical
      else:
        # and user press ON button
        if method_flag:
          print "    - change ambience"
          SwitchAmbience(light, method)
        else:
          print "    - light is already off"
          continue

    else:
      print "    - can't determine if light is on or off"

    # check if we have a list of ambiences for this light
    if hue_ambiences_list.has_key(light):
      # get the light parameters with the ambience index
      ambience = hue_ambiences_list[light][ambience_index[light]]
      # save the last light used
      last_hue_light = light

      # if we have the same key in hue lights list
      if hue_lights_list.has_key(ambience):
        # get the parameters of the light
        hue_device = hue_lights_list[ambience]

        # check for CT parameter
        if "ct" in hue_device:
          print "    - device has CT information"
          ct = hue_device["ct"]

          if ct < 154:
            ct = 154

          if ct > 500:
            ct = 500

          request["ct"] = ct
          SendToDevice(light, request)
          continue

        # check for R. G. B. parameters
        if "red" in hue_device and "green" in hue_device and "blue" in hue_device:
          print "    - device has R. G. B. and BRI informations"

          red = hue_device["red"]
          green = hue_device["green"]
          blue = hue_device["blue"]

          # convert to X, Y color model
          x, y = RGBToXY(red, green, blue)
          request["xy"] = [x, y]

          bri = hue_device["bri"]

          if bri < 0:
            bri = 0

          if bri > 254:
            bri = 254

          request["bri"] = bri
          SendToDevice(light, request)
          continue

        # here, we have not the good parameters
        print "    - no good information"

    else:
      print "    - no ambience found"

  print "- all lights done"

#---

# GET DEVICE STATE
def GetDeviceState(light):
  """Get the state of a Hue lamp"""
  print "    - get light state..."

  try:
    r = requests.get(hue_bridge_address + hue_bridge_identification + "/lights/" + light)

  except requests.exceptions.RequestException as e:
    print "/!\ " + e
    return False

  if r.status_code != 200:
    print "      - request error: " + str(r.status_code)
    return False

  json_content = json.loads(r.content)
  if (json_content) > 0:
    if json_content.has_key("state"):
      state = json_content["state"]
      return state

  print "      - failed"
  return False

#---

# SEND TO DEVICE
def SendToDevice(light, request):
  """Send an order to the Hue lamp"""
  print "      - send order..."

  try:
    r = requests.put(hue_bridge_address + hue_bridge_identification + "/lights/" + light + "/state", json=request)

  except requests.exceptions.RequestException as e:
    print "/!\ " + e
    return False

  if r.status_code != 200:
    print "        - request error: " + str(r.status_code)
    return False

  json_content = json.loads(r.content)
  if isinstance(json_content, list):
    if (json_content) > 0:
      if "success" in json_content[0]:
        print "        - success"
        return True

  print "        - failed"
  return False

#---

# SWITCH AMBIENCE
def SwitchAmbience(light, method):
  """Change the current settings (ambience) of a Hue lamp"""
  print "- switch the ambience"

  if ambience_index.has_key(light):
    # convert method on a on/off flag
    if method == "turnon":
      print "  - increment"
      ambience_index[light] = ambience_index[light] + 1
      if ambience_index[light] > (len(hue_ambiences_list[light]) - 1):
        ambience_index[light] = 0

    elif method == "turnoff":
      print "  - decrement"
      ambience_index[light] = ambience_index[light] - 1
      if ambience_index[light] < 0:
        ambience_index[light] = len(hue_ambiences_list[light]) - 1

    else:
      print "  - bad method: " + method

  print "  - now ambience is " + hue_ambiences_list[light][ambience_index[light]]


#---------------------------------------------------------------------------------
# MODULES
#---------------------------------------------------------------------------------

import sys

try:
  import os
  import json
  import time
  import requests

except ImportError, err:
  error_module = str(err)
  print "/!\ " + error_module
  sys.exit(1)


if os.path.isfile("td.py"):
  import td
else:
  print "/!\ ERROR: this code need td.py to work"
  sys.exit(1)


#---------------------------------------------------------------------------------
# CODE
#---------------------------------------------------------------------------------

print "------------------------------------------------------------"
print "-                        DIO 2 HUE                         -"
print "------------------------------------------------------------"

# get the arguments of the command line
arguments = sys.argv

# check if user want only scan DiO devices
if "scan" in arguments:
  print "- only listen DIO devices"
  scan_only = True

res = td.registerRawDeviceEvent(myRawDeviceEvent)
print "- event handlers registered"
print "- waiting for events..."

try:
  while True:
    time.sleep(0.1)

except KeyboardInterrupt:
  print "/!\ KeyboardInterrupt received, exiting..."
  sys.exit(0)
