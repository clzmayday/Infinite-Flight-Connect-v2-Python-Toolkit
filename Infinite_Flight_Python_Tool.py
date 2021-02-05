from Infinite_Flight_Connect_v2 import Connect2
import struct
running = True

connect = Connect2
connect.get_IF()
if not connect.update():
    raise ConnectionError("Cannot get the data from Infinite Flight via TCP")
# Print Aircraft Model and Livery
print(connect.FLIGHT_STATUS)
# Print Command List
for i in connect.IF_COMMAND.keys():
    print(i, connect.IF_COMMAND[i])

# This is the example for Boing 777-300ER for how to use getState, setState and runCommand
print(connect.getState(('simulator', 'time_zone')))
print(connect.setState(('aircraft0', 'systems', 'electrical_switch', 'strobe_lights_switch', 'state'), 1))
print(connect.runCommand(('commands', 'AutoStart')))
