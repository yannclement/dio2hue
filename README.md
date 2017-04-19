# dio2hue
<h2>Gateway for controlling Hue lamps (http://www2.meethue.com) with DiO Chacon transmitters (HomeEasy 433Mhz home automation, go to https://getdio.com).</h2>

This Python program requires a TellStick Duo (http://telldus.se/produkt/tellstick-duo/) to receive commands from the Chacons emitters.

The TellStick listens for every ON / OFF command sent. If an order comes from a known transmitter in the <code>dio_devices_list</code> list, we research the correspondence with a Hue lamps in <code>correspondences_table</code> variable.

To complete your list of known transmitters, start the program with the parameter "scan":
<code>python dio2hue.py scan</code>

Activate each transmitter to know it's parameters and fill in the variable <code>dio_devices_list</code>.

An emitter can therefore control several lamps.

The program then sends the current lighting parameters listed in the variable <code>hue_ambiences_list</code> which are detailed in the variable <code>hue_lights_list</code>.

To change the lighting parameters of each lamp, it is sufficient to send the ON order several times with a DiO emitter, for example whith a remote control.

First of all, you must have identified the program with your Hue Bridge, for this:
- configure your Hue bridge with a static IP (http://notsealed.com/how-to-set-static-philips-hue-bridge-ip-address-fix.html),
- enter in the variable <code>hue_bridge_address</code> the address permitting access to the API of your Hue bridge,
- go to http://[your Hue bridge IP]/debug/clip.html ,
- specify <code>/api</code> in URL and <code>{"devicetype": "dio2hue"}</code> in Message Body,
- press the button on the bridge and then press the POST button,
- retrieve the identifier in "username" and copy it into the <code>hue_bridge_identification</code> variable.

Currently I use this program as is and I have no worries. I left my configuration (2 Hue lamps, Ambience in 1 and Color in 2) to help you locate yourself.

Excuse my English which is not my mother tongue.
