import inputs

pads = inputs.devices.gamepads
LOOP = True

if len(pads) == 0:
    raise Exception("Couldn't find any Gamepads!")
else:
    print("Devices:\n {}".format(inputs.devices.gamepads))
    print("Start driving...")

    while LOOP:
        events = inputs.get_gamepad()
        for event in events:
            if event.code == "BTN_SOUTH":
                LOOP = False
            elif event.code == "ABS_HAT0X":
                print(event.state) 
            elif event.code == "ABS_HAT0Y":
                print(event.state) 
            #print(event.code) #, event.state
    
    print("End of driving...")