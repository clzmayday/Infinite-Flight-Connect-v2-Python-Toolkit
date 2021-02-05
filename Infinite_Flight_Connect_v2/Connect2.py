from socket import *
import json
import struct
json_file = None
connected = False
BUFFER_SIZE = 1024*100
IF_IP = None
IF_PORT = 10112
IF_ADDR = None
IF_ID = None
FLIGHT_STATUS = {'Aircraft':'', 'Livery':'',}
IF_TCP = None
IF_TYPE = {-1:"-1" , 0:"?", 1:"i", 2:"f", 3:"d", 4:"s", 5:"l"}
IF_COMMAND = {}
TIMEOUT = 5
def get_IF():
    global json_file, IF_ADDR, IF_PORT, IF_IP, IF_ID, FLIGHT_STATUS
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(TIMEOUT)
    s.bind(('', 15000))
    try:
        m = s.recvfrom(BUFFER_SIZE)
    except:
        print("Timeout")
    try:
        json_file = json.loads(m[0])
    except:
        json_file = {}
    if len(json_file) <= 0:
        json_file = None
        IF_ADDR = None
        IF_ID = None
    else:
        IF_IP = json_file["Addresses"][-1]
        IF_ADDR = (IF_IP, IF_PORT)
        IF_ID = m[-1][-1]
        FLIGHT_STATUS["Aircraft"] = json_file["Aircraft"]
        FLIGHT_STATUS["Livery"] = json_file["Livery"]

def pack_data(d, format):
    return struct.pack(format, *d)

def decode_message(data, t):
    if len(data) > 0:
        unpacked = struct.unpack("i i", data[:8])
    else:
        if t == -1:
            return "Command sent"
        else:
            raise ValueError("Unrecognised Data")

    if IF_TYPE[t] == "s":
        return struct.unpack("i i" + str(unpacked[-1]) + IF_TYPE[t], data)[-1].decode("utf-8")
    else:
        return str(struct.unpack("i i" + IF_TYPE[t], data)[-1])


def read_command(data):
    global IF_COMMAND

    for i in data.decode("utf-8").split("\n")[:-1]:
        a = i.split(",")
        index = int(a[0])
        t = int(a[1])
        temp_comm = a[-1].split("/")
        command = []
        for j in range(len(temp_comm)):
            if j == 0:
                command.append(temp_comm[j])
            else:
                try:
                    command[-1] = command[-1] + str(int(temp_comm[j]))
                except:
                    command.append(temp_comm[j])
        command = tuple(command)
        IF_COMMAND[command] = (index, t)



def update():
    global json_file
    if not (json_file and IF_ADDR):
        raise ConnectionError("Cannot find the running Infinite Flight App\nPlease check your device and internet")
    tcp = socket(AF_INET, SOCK_STREAM)
    data = b""
    tcp.connect(IF_ADDR)
    tcp.settimeout(TIMEOUT)
    tcp.sendall(pack_data((-1, False), "i ?"))
    while True:
        try:
            buffer = tcp.recv(BUFFER_SIZE)
        except:
            break
        data += buffer
    tcp.close()
    if len(data) > 0:
        read_command(data[12:])
        return True
    else:
        return False

def TCP_Start():
    global IF_TCP
    IF_TCP = socket(AF_INET, SOCK_STREAM)
    IF_TCP.connect(IF_ADDR)
    IF_TCP.settimeout(TIMEOUT)

def TCP_Shutdown():
    global IF_TCP
    IF_TCP.close()
    IF_TCP = None

def TCP_Communicate(msg1, msg2=None):
    global IF_TCP
    data = b""
    if msg2 == None:
        IF_TCP.sendall(pack_data((msg1, False), "i ?"))
    else:
        IF_TCP.sendall(pack_data((msg1, True, msg2), "i ? i"))
        data = b"setState sent"
    while True:
        try:
            buffer = IF_TCP.recv(BUFFER_SIZE)
        except:
            break
        data += buffer
    return data

def getState(code):
    global IF_COMMAND
    TCP_Start()
    command = IF_COMMAND[code]
    state = TCP_Communicate(int(command[0]))
    TCP_Shutdown()
    return decode_message(state, int(command[-1]))

def setState(code, value):
    global IF_COMMAND
    TCP_Start()
    command = IF_COMMAND[code]
    state = TCP_Communicate(int(command[0]), int(value))
    TCP_Shutdown()
    return state.decode("utf-8")

def runCommand(code):
    global IF_COMMAND
    TCP_Start()
    command = IF_COMMAND[code]
    state = TCP_Communicate(int(command[0]))
    TCP_Shutdown()
    return decode_message(state, int(command[-1]))

def getCommand():
    global IF_COMMAND
    return IF_COMMAND

