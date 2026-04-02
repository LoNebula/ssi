from xdpchandler import *

xdpcHandler = None
orientationResetDone = False
startTime = 0

def initialize():
    """
    Initializes the Movella DOT devices. This function is called once at the start of the pipeline.
    """
    global xdpcHandler, startTime
    xdpcHandler = XdpcHandler()

    if not xdpcHandler.initialize():
        return False

    xdpcHandler.scanForDots()
    if len(xdpcHandler.detectedDots()) == 0:
        print("No Movella DOT device(s) found. Aborting.")
        return False

    xdpcHandler.connectDots()

    if len(xdpcHandler.connectedDots()) == 0:
        print("Could not connect to any Movella DOT device(s). Aborting.")
        return False

    for device in xdpcHandler.connectedDots():
        if device.setOnboardFilterProfile("General"):
            print("Successfully set profile to General")
        else:
            print("Setting filter profile failed!")

        print("Setting quaternion CSV output")
        device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)

        logFileName = "logfile_" + device.bluetoothAddress().replace(':', '-') + ".csv"
        print(f"Enable logging to: {logFileName}")
        if not device.enableLogging(logFileName):
            print(f"Failed to enable logging. Reason: {device.lastResultText()}")

        print("Putting device into measurement mode.")
        if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
            print(f"Could not put device into measurement mode. Reason: {device.lastResultText()}")
            continue

    print("\nMain loop. Ready to receive data.")
    print("-----------------------------------------")
    s = ""
    for device in xdpcHandler.connectedDots():
        s += f"{device.bluetoothAddress():42}"
    print("%s" % s, flush=True)

    startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
    return True

def process(run):
    """
    Processes data from the Movella DOT devices. This function is called repeatedly by the pipeline.
    The 'run' parameter controls whether data is processed.
    """
    global xdpcHandler, orientationResetDone, startTime
    
    if not run:
        return ""

    if xdpcHandler and xdpcHandler.packetsAvailable():
        s = ""
        for device in xdpcHandler.connectedDots():
            packet = xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())
            if packet.containsOrientation():
                euler = packet.orientationEuler()
                s += f"Roll:{euler.x():7.2f}, Pitch:{euler.y():7.2f}, Yaw:{euler.z():7.2f}| "

        # Optional: Reset orientation after a certain time
        if not orientationResetDone and movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime > 5000:
            for device in xdpcHandler.connectedDots():
                print(f"\nResetting heading for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
                if device.resetOrientation(movelladot_pc_sdk.XRM_Heading):
                    print("OK", end="", flush=True)
                else:
                    print(f"NOK: {device.lastResultText()}", end="", flush=True)
            print("\n", end="", flush=True)
            orientationResetDone = True
        
        return s
    
    return ""

def cleanup():
    """
    Cleans up the Movella DOT devices. This function is called when the pipeline stops.
    """
    global xdpcHandler
    if xdpcHandler:
        print("\n-----------------------------------------", end="", flush=True)

        for device in xdpcHandler.connectedDots():
            print(f"\nResetting heading to default for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
            if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
                print("OK", end="", flush=True)
            else:
                print(f"NOK: {device.lastResultText()}", end="", flush=True)
        print("\n", end="", flush=True)

        print("\nStopping measurement...")
        for device in xdpcHandler.connectedDots():
            if not device.stopMeasurement():
                print("Failed to stop measurement.")
            if not device.disableLogging():
                print("Failed to disable logging.")

        xdpcHandler.cleanup()
        xdpcHandler = None
