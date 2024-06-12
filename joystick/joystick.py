import inputs

pads = inputs.devices.gamepads

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Start...")

    while True:
        events = inputs.get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)