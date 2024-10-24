# CryptoMesh Node Network Tool

This Python tool enables a **peer-to-peer (P2P) network** using **Zeroconf service discovery**. Each node in the network can broadcast messages to connected peers, automatically discover new nodes, and maintain active connections with them.

---

## Features

- **Peer-to-peer messaging**: Broadcast messages across nodes in the network.
- **Zeroconf/Bonjour service discovery**: Automatically detect and connect to new nodes.
- **Multi-threaded handling**: Accept multiple peer connections simultaneously.
- **Fault tolerance**: Handles connection failures gracefully.
  
---

## Prerequisites

1. **Python 3.x** installed on your machine.
2. Install the required dependencies:
   ```bash
   pip install zeroconf
