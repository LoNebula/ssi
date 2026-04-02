from xdpchandler import *

def getChannelNames(opts, vars):
    """
    Returns a dictionary of channel names and their descriptions.
    """
    return {'orientation': 'Movella DOT Orientation Data (Roll, Pitch, Yaw)'}

def initChannel(name, channel, types, opts, vars):
    """
    Initializes the properties of a given channel.
    """
    if name == 'orientation':
        channel.dim = 3  # We will output 3 dimensions: Roll, Pitch, Yaw
        channel.type = types.FLOAT
        channel.sr = 60  # Typical sample rate for Movella DOT
    else:
        print(f"Unknown channel name: {name}")

def connect(opts, vars):
    """
    Called once when the pipeline starts. Initializes devices and stores state in the `vars` dictionary.
    """
    print("Connecting to Movella DOT devices...")
    handler = XdpcHandler()

    if not handler.initialize():
        print("Failed to initialize XdpcHandler.")
        handler.cleanup()
        return False

    handler.scanForDots()
    if len(handler.detectedDots()) == 0:
        print("No Movella DOT device(s) found. Aborting.")
        handler.cleanup()
        return False

    handler.connectDots()
    if len(handler.connectedDots()) == 0:
        print("Could not connect to any Movella DOT device(s). Aborting.")
        handler.cleanup()
        return False

    for device in handler.connectedDots():
        if not device.setOnboardFilterProfile("General"):
            print("Setting filter profile failed!")
        if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
            print(f"Could not put device into measurement mode. Reason: {device.lastResultText()}")
            continue
    
    print("Movella DOT connected and in measurement mode.")
    vars['handler'] = handler
    vars['devices'] = handler.connectedDots()
    return True

def read(name, sout, reset, board, opts, vars):
    """
    Called repeatedly by the pipeline to read data blocks.
    """
    handler = vars.get('handler')
    devices = vars.get('devices')
    if not handler or not devices:
        return

    if name == 'orientation':
        # We need to provide sout.num samples. We'll read packets and fill the buffer.
        # For simplicity, we'll use the first connected device.
        device = devices[0]
        
        for i in range(sout.num):
            if handler.packetsAvailable():
                packet = handler.getNextPacket(device.portInfo().bluetoothAddress())
                if packet.containsOrientation():
                    euler = packet.orientationEuler()
                    # Write the 3D sample to the output stream.
                    # We assume sout.set() or equivalent takes a list/tuple for multi-dim data.
                    sout[i] = (euler.x(), euler.y(), euler.z())
                else:
                    # If no orientation data, write a zero vector
                    sout[i] = (0.0, 0.0, 0.0)
            else:
                # If no packets are available, fill with zeros
                sout[i] = (0.0, 0.0, 0.0)

def disconnect(opts, vars):
    """
    Called once when the pipeline stops. Cleans up resources.
    """
    handler = vars.get('handler')
    if handler:
        print("Stopping measurement and disconnecting...")
        for device in handler.connectedDots():
            device.stopMeasurement()
        handler.cleanup()
        print("Disconnected.")
