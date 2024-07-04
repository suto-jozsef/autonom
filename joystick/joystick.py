import inputs
import time

pads = inputs.devices.gamepads
loopcount = 0
loop = True

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Start...")
    start = time.time()

    while loop:
        loopcount += 1
        events = inputs.get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
            
            if event.code == "BTN_SOUTH" and int(event.state) == 1:
                loop = False

print("Elapsed time: {}".format(time.time() - start))
print("Loop count: {}".format(loopcount))
print("Avg loop time: {}".format((time.time() - start) / loopcount))