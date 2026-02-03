# ICMP Ping & Traceroute Implementation in Python

This repository contains a complete **Python implementation of ICMP-based Ping and Traceroute utilities** using **raw sockets**.  
The project is part of a Computer Networks coursework and demonstrates low-level interaction with the IP and ICMP protocols, closely mirroring the behavior of standard `ping` and `traceroute` tools.

---

## Project Overview

The project is divided into **two main parts**:

1. **ICMP Ping Client**
2. **ICMP Traceroute (Bonus / Extra Credit)**

Both tools are implemented manually using raw sockets to provide hands-on experience with:
- ICMP packet structure
- Error detection via checksum
- RTT (Round-Trip Time) measurement
- TTL-based path discovery

---

## Repository Structure

- `starter-code-CA5-P1.py`  
  Implementation of **ICMP Ping** client.

- `starter-code-CA5-P2.py`  
  Implementation of **ICMP Traceroute**.

- `Instruction.pdf`  
  Assignment description and protocol details.

- `Report.pdf`  
  Experimental results and analysis.

---

## ICMP Ping

### Description

The Ping program sends **ICMP Echo Request** packets to a target host and listens for **Echo Reply** packets.

For each received reply, the program:
- Verifies packet integrity using checksum
- Extracts TTL from the IP header
- Computes RTT using an embedded timestamp
- Prints formatted output similar to the standard `ping` utility

### Key Features

- Raw socket communication (`SOCK_RAW`)
- Manual ICMP header construction
- Checksum verification
- Timeout handling using `select`
- Accurate RTT calculation

### ICMP Echo Packet Structure

| Field | Description |
|------|-------------|
| Type | 8 (Echo Request) |
| Code | 0 |
| Checksum | Error-detection checksum |
| Identifier | Process ID |
| Sequence Number | Incremental |
| Data | Timestamp |

---

## ICMP Traceroute

### Description

The Traceroute implementation discovers the network path to a destination host by:
- Sending ICMP Echo Requests with increasing TTL values
- Receiving ICMP **Time Exceeded** messages from intermediate routers
- Detecting destination arrival via ICMP Echo Reply

### Key Features

- Incremental TTL probing (1 → MAX_HOPS)
- Detection of intermediate routers
- RTT measurement per hop
- Reverse DNS lookup of router IPs
- Graceful handling of ICMP timeouts

### ICMP Messages Used

| Type | Meaning |
|-----:|--------|
| 8 | Echo Request |
| 11 | Time Exceeded |
| 3 | Destination Unreachable |
| 0 | Echo Reply (destination reached) |

---

## How It Works (High-Level)

1. **Build ICMP packet**
   - Create header with zero checksum
   - Append timestamp
   - Compute checksum
2. **Send packet using raw socket**
3. **Wait for response**
   - Use `select()` for timeout control
4. **Parse received packet**
   - Extract IP header
   - Parse ICMP header
5. **Validate and process**
   - Verify checksum
   - Match identifiers
   - Compute RTT

Traceroute repeats this process while increasing TTL.

---

## Requirements

- Python 3.x
- Administrator / root privileges (required for raw sockets)
- Internet access (some routers may block ICMP)

> ⚠️ Note: Firewalls or antivirus software may block ICMP packets.

---

## How to Run

### ICMP Ping

```bash
sudo python3 starter-code-CA5-P1.py
```

By default, the script pings `google.com`.  
You may change the target host inside the script.

---

### ICMP Traceroute

```bash
sudo python3 starter-code-CA5-P2.py
```

This traces the route to `google.com` using ICMP Echo Requests.

---

## Testing & Experiments

The programs were tested against:
- `127.0.0.1` (localhost)
- Hosts in Asia, Europe, North America, and Oceania
- Public servers and Google infrastructure

Observed behavior:
- RTT increases with geographical distance
- Many routers suppress ICMP Time Exceeded messages
- Final destination replies confirm successful path discovery

Detailed results and screenshots are included in `Report.pdf`.

---

## Design Assumptions

- IPv4 only
- No packet reordering
- Checksum implementation provided
- One probe per TTL per try
- ICMP filtering may affect results

---

## Possible Improvements

- RTT statistics (min / avg / max)
- Packet loss percentage
- Multiple probes per hop
- IPv6 support
- Better CLI argument handling

---

## Educational Value

This project provides practical insight into:
- ICMP internals
- Network diagnostics
- Low-level socket programming
- Real-world Internet behavior and limitations