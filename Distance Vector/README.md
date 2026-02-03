# Distance Vector Routing Protocol Simulation

This repository contains a **C-based simulation of the Distance Vector (DV) routing algorithm**, implemented as part of a Computer Networks coursework.  
The project models how routers exchange distance vectors, update routing tables, and converge to shortest paths in a small network.

---

## Project Overview

The simulation consists of **four network nodes (routers)** that exchange routing information until the network converges.

Each node:
- Maintains a distance table
- Sends updates to its neighbors when changes occur
- Recomputes shortest paths using the Bellman–Ford algorithm

---

## Repository Structure

- `distance_vector.c` – Simulator core and shared logic  
- `node0.c` – Routing logic for Node 0  
- `node1.c` – Routing logic for Node 1  
- `node2.c` – Routing logic for Node 2  
- `node3.c` – Routing logic for Node 3  
- `Instruction.pdf` – Assignment specification  
- `Report.pdf` – Results and convergence analysis  

---

## Distance Vector Algorithm

Each node maintains a distance table:

```
cost[destination][via_neighbor]
```

### Bellman–Ford Update Rule

```
D_x(d) = min_v { c(x, v) + D_v(d) }
```

If a better path is found, the node updates its table and informs its neighbors.

---

## Node Responsibilities

Each node implements:

- `rtinitX()` – Initialize distance table and send initial vectors  
- `rtupdateX()` – Process incoming routing updates  
- `printdtX()` – Display routing table  

---

## How to Compile and Run

```bash
gcc distance_vector.c node0.c node1.c node2.c node3.c -o dv_sim
./dv_sim
```

---

## Output

The simulator prints:
- Initial routing tables
- Routing update exchanges
- Final converged tables

Convergence is reached when no further updates are generated.

---

## Design Assumptions

- Four fixed nodes
- Symmetric link costs
- Reliable message delivery
- Basic Distance Vector (no split horizon or poisoned reverse)

---

## Possible Extensions

- Split Horizon
- Poisoned Reverse
- Dynamic link cost changes
- Count-to-infinity scenarios

---

## Educational Value

This project demonstrates:
- Distributed routing algorithms
- Bellman–Ford in practice
- Routing convergence behavior