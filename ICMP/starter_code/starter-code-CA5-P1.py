from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0

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

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while (1):
        startedSelect = time.time()

        whatReady = select.select([mySocket], [], [], timeLeft)

        howLongInSelect = (time.time() - startedSelect)

        # Timeout
        if (whatReady[0] == []):
            return "Request timed out."
        
        timeReceived = time.time()

        recPacket, addr = mySocket.recvfrom(1024)

        # ---------------------------
        # 1) Read IP header
        # ---------------------------

        # TTL is always in 8th byte of IPv4
        ttl = recPacket[8]

        # IHL (Internet Header Length) is in 4 little endian bits in 1st byte of IPv4
        ipHeaderLen = (recPacket[0] & 0x0F) * 4

        # ---------------------------
        # 2) Seperate ICMP header from IP packet
        # ---------------------------

        # ICMP header is 8 byte
        icmpHeader = recPacket[ipHeaderLen : ipHeaderLen + 8]

        # struct: type(1), code(1), checksum(2), id(2), sequence(2)
        icmpType, icmpCode, icmpChecksum, icmpID, icmpSeq = struct.unpack("bbHHh", icmpHeader)

        # ---------------------------
        # 3) Verify ICMP checksum
        # ---------------------------
        
        # Compute and check checksums
        icmpPacket = recPacket[ipHeaderLen : ]

        if (checksum(icmpPacket) != 0):
            timeLeft = timeLeft - howLongInSelect

            if (timeLeft <= 0):
                return "Request timed out."
            
            continue

        # ---------------------------
        # 4) Validate only Echo Reply with our ID from the host
        # ---------------------------

        if (addr[0] == destAddr and icmpType == ICMP_ECHO_REPLY and icmpID == ID and icmpCode == 0):
            # ---------------------------
            # 5) Read 8 bytes data (timestamp)
            # ---------------------------

            # Data starts after ICMP header
            timeSent = struct.unpack("d", recPacket[ipHeaderLen + 8 : ipHeaderLen + 16])[0]

            # Compute RTT
            rtt = timeReceived - timeSent

            # Compute ICMP reply packet's data length (len(total packet) - len(IP header) - len(ICMP header))
            icmpDataLen = len(recPacket) - ipHeaderLen - 8

            # Ping message
            return f"{icmpDataLen} bytes from {addr[0]}: icmp_seq={icmpSeq} ttl={ttl} rtt={rtt*1000:.3f} ms"

        # If the packet was not Echo Reply or with another ID
        timeLeft = timeLeft - howLongInSelect

        if (timeLeft <= 0):
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    # Make a dummy header with a 0 checksum
    myChecksum = 0

    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if (sys.platform == 'darwin'):
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    packet = header + data

    # AF_INET address must be tuple, not str
    mySocket.sendto(packet, (destAddr, 1)) # Both LISTS and TUPLES consist of a number of objects

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details: http://sock-raw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    # Return the current process 
    myID = os.getpid() & 0xFFFF
    
    sendOnePing(mySocket, destAddr, myID)

    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()

    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost

    dest = gethostbyname(host)

    print("Pinging " + dest + " using Python:")
    print("")

    # Send ping requests to a server separated by approximately one second
    while (1):
        delay = doOnePing(dest, timeout)

        print(delay)

        # Wait for one second
        time.sleep(1)

    return delay

# Example run
ping("google.com")