import socket
import threading
import time
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser, ServiceStateChange
import ipaddress

class CryptoMeshNode:
    def __init__(self, name):
        self.name = name
        self.peers = {}
        self.messages = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 0))  # Bind to any available port
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(5)
        self.zeroconf = Zeroconf()
        self.service_info = None
        self.browser = None

    def start(self):
        print(f"Node {self.name} started on port {self.port}")
        self.register_service()
        threading.Thread(target=self.accept_connections, daemon=True).start()
        self.browser = ServiceBrowser(self.zeroconf, "_cryptomesh._tcp.local.", handlers=[self.on_service_state_change])

    def register_service(self):
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"Registering service with IP: {local_ip}")
        self.service_info = ServiceInfo(
            "_cryptomesh._tcp.local.",
            f"{self.name}._cryptomesh._tcp.local.",
            addresses=[ipaddress.ip_address(local_ip).packed],
            port=self.port,
            properties={'name': self.name}
        )
        self.zeroconf.register_service(self.service_info)
        print(f"Service registered: {self.service_info}")

    def accept_connections(self):
        while True:
            client, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode()
                if message:
                    print(f"\nReceived: {message}")
                    self.messages.append(message)
                    print("Enter message to broadcast (or 'quit' to exit): ", end='', flush=True)
            except:
                break
        client.close()

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        print(f"Service change: {service_type} {name} {state_change}")
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.name != self.service_info.name and info.name not in self.peers:
                try:
                    ip = socket.inet_ntoa(info.addresses[0])
                    print(f"Attempting to connect to {ip}:{info.port}")
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((ip, info.port))
                    self.peers[info.name] = client
                    print(f"\nConnected to peer: {info.name}")
                    print("Enter message to broadcast (or 'quit' to exit): ", end='', flush=True)
                except Exception as e:
                    print(f"\nFailed to connect to peer: {info.name}. Error: {e}")
                    print("Enter message to broadcast (or 'quit' to exit): ", end='', flush=True)

    def broadcast(self, message):
        full_message = f"{self.name}: {message}"
        print(f"\nBroadcasting: {full_message}")
        for peer, client in list(self.peers.items()):
            try:
                client.send(full_message.encode())
            except:
                print(f"\nFailed to send message to peer: {peer}")
                del self.peers[peer]
        print("Enter message to broadcast (or 'quit' to exit): ", end='', flush=True)

    def run(self):
        self.start()
        while True:
            message = input("Enter message to broadcast (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
            self.broadcast(message)

    def cleanup(self):
        self.zeroconf.unregister_service(self.service_info)
        self.zeroconf.close()

if __name__ == "__main__":
    node_name = input("Enter node name: ")
    node = CryptoMeshNode(node_name)
    try:
        node.run()
    finally:
        node.cleanup()
