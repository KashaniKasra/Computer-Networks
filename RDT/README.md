# Reliable Data Transfer Simulator (Alternating Bit + Go-Back-N)

A Python implementation of classic **reliable transport protocols** built on top of an unreliable network using the well-known **Kurose & Ross event-driven simulator**.

This repository includes:
- **Stop-and-Wait / Alternating Bit (rdt3.0-style)**
- **Bonus: Go-Back-N (GBN)** with sliding window and buffering

The project demonstrates how reliable data transfer is achieved despite packet loss and corruption.

---

## Background

Real networks are unreliable: packets may be lost, corrupted, or delayed. Reliable transport protocols solve this problem using:
- Sequence numbers
- Acknowledgments (ACKs)
- Timers and retransmissions
- Checksums
- Sliding windows (for higher throughput)

This project simulates these mechanisms in a controlled environment for educational purposes.

---

## Repository Structure

- `rdtsim.py`  
  Implements the simulator and the **Alternating Bit (Stop-and-Wait)** protocol.

- `Bonus-gbn.py`  
  Implements the **Go-Back-N** protocol as a bonus extension.

- `Instruction.pdf`  
  Original assignment description and guidelines.

---

## Packet and Message Format

- **Message (Layer 5 → Layer 4)**  
  Fixed-size payload of 20 bytes.

- **Packet (Layer 4 → Layer 3)**  
  | Field | Description |
  |------|-------------|
  | seqnum | Sequence number |
  | acknum | Acknowledgment number |
  | checksum | Error-detection checksum |
  | payload | 20-byte data payload |

All sequence and acknowledgment numbers are constrained to:
```
0 ≤ value < seqnum_limit
```

---

## Checksum

A simple additive checksum is used:
- Add `seqnum`
- Add `acknum`
- Add ASCII values of payload bytes

A packet is considered corrupted if the computed checksum does not match the stored checksum.

---

## Alternating Bit (Stop-and-Wait)

### Sender (Entity A)
- Uses a 1-bit sequence number (0 or 1)
- Sends one packet at a time
- Waits for a valid ACK before sending the next message
- Retransmits on timeout

### Receiver (Entity B)
- Accepts only the expected sequence number
- Delivers correct packets to layer 5
- Sends duplicate ACKs for corrupted or unexpected packets

This protocol is simple but inefficient under high latency.

---

## Go-Back-N (Bonus)

### Sender
- Maintains a sliding window (max size = 8)
- Buffers packets until acknowledged
- Uses cumulative ACKs
- Retransmits **all unacknowledged packets** on timeout

### Receiver
- Accepts packets in order only
- Discards out-of-order packets
- Sends cumulative ACKs for the last correctly received packet

Go-Back-N improves throughput at the cost of more retransmissions.

---

## Simulator Behavior

- Event-driven simulation
- Packet loss and corruption are probabilistic
- In-order delivery (no reordering)
- One-way data transfer (A → B)

At the end of execution, performance statistics and throughput are printed.

---

## Requirements

- Python 3.x
- No external libraries required

---

## How to Run

### Command-Line Options

- `-n <int>` : Number of messages to send  
- `-d <float>` : Average delay between messages  
- `-z <int>` : Sequence number limit  
- `-l <float>` : Packet loss probability  
- `-c <float>` : Packet corruption probability  
- `-s <int>` : Random seed  
- `-v <int>` : Verbosity level  

---

### Run Alternating Bit

```bash
python3 rdtsim.py -n 20 -d 1000 -l 0.1 -c 0.3 -v 2
```

---

### Run Go-Back-N (Bonus)

```bash
python3 Bonus-gbn.py -n 50 -d 10 -l 0.2 -c 0.2 -v 2
```

---

## Output

The simulator prints:
- Simulation configuration
- Total packets sent
- Packets lost/corrupted
- Messages delivered to layer 5
- Throughput statistics

Increase verbosity (`-v`) for detailed tracing.

---

## Design Assumptions

- No packet reordering
- Simple checksum (educational)
- Only unidirectional data transfer
- Single timer for Go-Back-N sender

---

## Possible Extensions

- Selective Repeat (SR)
- Adaptive timeout (RTT estimation)
- CSV logging for plotting throughput
- Bidirectional data transfer