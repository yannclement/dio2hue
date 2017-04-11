# dio2hue
Gateway for controlling Hue lamps (http://www2.meethue.com) with DiO Chacon transmitters (HomeEasy 433Mhz home automation, go to https://getdio.com).

This Python program requires a TellStick Duo (http://telldus.se/produkt/tellstick-duo/) to receive commands from the Chacons emitters.

The TellStick listens for every ON / OFF command sent. If an order comes from a known transmitter in the dio_devices_list list, we research the correspondence whith a Hue lamps in correspondences_table variable.

To complete your list of known transmitters, start the program with the parameter "scan" and activate each transmitter to know its parameters and fill in the variable dio_devices_list.

An emitter can therefore control several lamps.

The program then sends the current lighting parameters listed in the variable hue_ambiences_list which are detailed in the variable hue_lights_list.

To change the lighting parameters of each lamp, it is sufficient to send the ON order several times with a DiO emitter, for example whith a remote control.

First of all, you must have identified the program with your Hue Bridge, for this:
- configure your Hue bridge with a static IP (http://notsealed.com/how-to-set-static-philips-hue-bridge-ip-address-fix.html)
- enter in the variable hue_bridge_address the address permitting access to the API of your Hue bridge
- go to http://<your Hue bridge IP>/debug/clip.html
- specify /api in URL and {"devicetype": "dio2hue"} in Message Body
- press the button on the bridge and then press the POST button
- retrieve the identifier in "username" and copy it into the hue_bridge_identification variable

Currently I use this program as is and I have no worries. I left my configuration (2 Hue lamps, Ambience in 1 and Color in 2) to help you locate yourself.

Excuse my English which is not my mother tongue.
