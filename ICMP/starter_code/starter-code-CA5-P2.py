from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(data):
    # In this function we make the checksum of our packet

    csum = 0
    countTo = (len(data) // 2) * 2
    count = 0

    while (count < countTo):
        thisVal = data[count + 1] * 256 + data[count]

        csum = csum + thisVal
        csum = csum & 0xffffffff

        count = count + 2

    if (countTo < len(data)):
        csum = csum + data[len(data) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)

    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

def build_packet():
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    # Return the current process 
    myID = os.getpid() & 0xFFFF

    # Make a dummy header with a 0 checksum
    myChecksum = 0

    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if (sys.platform == 'darwin'):
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    packet = header + data

    return packet

def get_route(hostname):
    timeLeft = TIMEOUT

    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            # Reset timeleft
            timeLeft = TIMEOUT

            destAddr = gethostbyname(hostname)
            
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))

                t = time.time()
                
                startedSelect = time.time()

                whatReady = select.select([mySocket], [], [], timeLeft)

                howLongInSelect = time.time() - startedSelect

                # Timeout
                if (whatReady[0] == []):
                    print(" * * * Request timed out.")

                    continue
                
                recvPacket, addr = mySocket.recvfrom(1024)

                timeReceived = time.time()

                timeLeft = timeLeft - howLongInSelect
                
                if (timeLeft <= 0):
                    print(" * * * Request timed out.")
                    
            except timeout:
                continue
            
            else:
                # Fetch the icmp type from the IP packet, after IP header which is 20 bytes
                icmpHeader = recvPacket[20 : 28]
                types, code, checksum_val, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

                # Get router name
                try:
                    routerName = gethostbyaddr(addr[0])[0]
                except:
                    routerName = addr[0]
                
                if (types == 11):
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]

                    print(" ttl=%d rtt=%.0f ms IP=%s name=%s" % (ttl, (timeReceived - timeSent) * 1000, addr[0], routerName))
                    
                elif (types == 3):
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]

                    print(" ttl=%d rtt=%.0f ms IP=%s name=%s" % (ttl, (timeReceived - timeSent) * 1000, addr[0], routerName))
                    
                elif (types == 0):
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28 : 28 + bytes])[0]

                    print(" ttl=%d rtt=%.0f ms IP=%s name=%s" % (ttl, (timeReceived - timeSent) * 1000, addr[0], routerName))

                    return
                
                else:
                    print("error")

                break
            
            finally:
                mySocket.close()

# Example run
get_route("google.com")