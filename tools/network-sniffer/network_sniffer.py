#!/usr/bin/env python3
"""
Brutal Legend Network Sniffer
A basic LAN traffic sniffer to discover what ports/protocols the game uses.

NOTE: Requires administrator/root privileges to capture raw packets.
On Windows, run as Administrator. On Linux, run with sudo.

Usage:
    sudo python network_sniffer.py
    sudo python network_sniffer.py --port 27015  # Filter by port
    sudo python network_sniffer.py --ports 27015,27016  # Multiple ports

Known Steam ports to monitor:
    - 27015: Steam master server traffic
    - 27016: Steam client
    - 27017: Steam content server
    - 27018-27030: Steam relay servers
    - 27031-27039: Steam dedicated server ports
"""

import socket
import struct
import argparse
import datetime
import sys
from collections import defaultdict

# Common game/multicast ports to monitor
DEFAULT_PORTS = [27015, 27016, 27017, 27018, 27019, 27020,
                 27031, 27032, 27033, 27034, 27035, 27036, 27037, 27038, 27039]

# Well-known ports
WELL_KNOWN_PORTS = {
    27015: "Steam Master Server",
    27016: "Steam Client",
    27017: "Steam Content Server",
    27018: "Steam Relay",
    27019: "Steam Relay",
    27020: "Steam Relay",
}


class PacketCapture:
    """Simple packet sniffer using raw sockets."""

    def __init__(self, ports=None, timeout=0.5):
        self.ports = set(ports) if ports else set()
        self.timeout = timeout
        self.socket = None
        self.running = False
        self.packet_count = 0
        self.traffic_log = defaultdict(list)

    def create_sniffing_socket(self):
        """Create a raw socket for packet capture."""
        try:
            # AF_INET = IPv4, SOCK_RAW = raw packets, IPPROTO_IP = all IP
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            s.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
            s.settimeout(self.timeout)
            return s
        except PermissionError:
            print("ERROR: Raw socket creation failed. Need administrator/root privileges.")
            print("On Windows: Run as Administrator")
            print("On Linux: Run with sudo")
            sys.exit(1)

    def parse_ip_header(self, data):
        """Parse IP header from raw packet data."""
        if len(data) < 20:
            return None

        # IP header structure (little-endian on x86):
        # Version (4 bits) | IHL (4 bits) | TOS (1 byte) | Total Length (2 bytes)
        # Identification (2 bytes) | Flags/Fragment (2 bytes)
        # TTL (1 byte) | Protocol (1 byte) | Header Checksum (2 bytes)
        # Source IP (4 bytes) | Dest IP (4 bytes)

        version_ihl = data[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0x0F

        if version != 4:  # Only IPv4 for now
            return None

        header_len = ihl * 4
        if len(data) < header_len:
            return None

        protocol = data[9]
        src_ip = socket.inet_ntoa(data[12:16])
        dst_ip = socket.inet_ntoa(data[16:20])

        return {
            'version': version,
            'header_len': header_len,
            'protocol': protocol,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'total_len': struct.unpack('!H', data[2:4])[0]
        }

    def parse_tcp_header(self, data, ip_info):
        """Parse TCP header from packet data."""
        if len(data) < 14 + 20:  # Ethernet + IP + TCP minimum
            return None

        tcp_data = data[14 + ip_info['header_len']:]

        if len(tcp_data) < 20:
            return None

        src_port = struct.unpack('!H', tcp_data[0:2])[0]
        dst_port = struct.unpack('!H', tcp_data[2:4])[0]
        seq_num = struct.unpack('!I', tcp_data[4:8])[0]
        ack_num = struct.unpack('!I', tcp_data[8:12])[0]
        flags = tcp_data[13]

        # TCP flags
        flag_strings = []
        if flags & 0x01: flag_strings.append('FIN')
        if flags & 0x02: flag_strings.append('SYN')
        if flags & 0x04: flag_strings.append('RST')
        if flags & 0x08: flag_strings.append('PSH')
        if flags & 0x10: flag_strings.append('ACK')
        if flags & 0x20: flag_strings.append('URG')

        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'seq_num': seq_num,
            'ack_num': ack_num,
            'flags': flags,
            'flag_strings': flag_strings,
            'payload_len': len(tcp_data) - 20  # Subtract TCP header size
        }

    def parse_udp_header(self, data, ip_info):
        """Parse UDP header from packet data."""
        if len(data) < 14 + ip_info['header_len'] + 8:
            return None

        udp_data = data[14 + ip_info['header_len']:]

        src_port = struct.unpack('!H', udp_data[0:2])[0]
        dst_port = struct.unpack('!H', udp_data[2:4])[0]
        length = struct.unpack('!H', udp_data[4:6])[0]

        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'length': length,
            'payload_len': length - 8  # Subtract UDP header size
        }

    def get_protocol_name(self, proto_num):
        """Get protocol name from number."""
        protocols = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
        }
        return protocols.get(proto_num, f'PROTO({proto_num})')

    def format_port(self, port):
        """Format port number with known service name."""
        if port in WELL_KNOWN_PORTS:
            return f"{port} ({WELL_KNOWN_PORTS[port]})"
        return str(port)

    def log_packet(self, ip_info, transport_info, proto_name):
        """Log a captured packet."""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

        if proto_name == 'TCP':
            direction = f"{ip_info['src_ip']}:{transport_info['src_port']} -> {ip_info['dst_ip']}:{transport_info['dst_port']}"
            info = f"flags=[{','.join(transport_info['flag_strings'])}] seq={transport_info['seq_num']} ack={transport_info['ack_num']}"
        else:  # UDP
            direction = f"{ip_info['src_ip']}:{transport_info['src_port']} -> {ip_info['dst_ip']}:{transport_info['dst_port']}"
            info = f"len={transport_info['length']}"

        self.packet_count += 1

        # Log to console
        print(f"[{timestamp}] {proto_name:4} {direction}")
        print(f"         {info}")

        # Store for summary
        key = (ip_info['src_ip'], ip_info['dst_ip'], transport_info['src_port'], transport_info['dst_port'], proto_name)
        self.traffic_log[key].append({
            'timestamp': timestamp,
            'info': info
        })

    def capture_loop(self, duration=None):
        """Main packet capture loop."""
        self.socket = self.create_sniffing_socket()

        # Bind to all interfaces
        try:
            self.socket.bind(('0.0.0.0', 0))
        except Exception as e:
            print(f"Failed to bind socket: {e}")
            sys.exit(1)

        print("=" * 70)
        print("Brutal Legend Network Sniffer")
        print("=" * 70)
        print(f"Monitoring ports: {sorted(self.ports) if self.ports else 'ALL'}")
        print(f"Started at: {datetime.datetime.now()}")
        print("Press Ctrl+C to stop and show summary")
        print("=" * 70)

        self.running = True
        self.packet_count = 0

        try:
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(65535)
                    ip_info = self.parse_ip_header(data)

                    if ip_info is None:
                        continue

                    proto_name = self.get_protocol_name(ip_info['protocol'])

                    if proto_name == 'TCP':
                        transport_info = self.parse_tcp_header(data, ip_info)
                    elif proto_name == 'UDP':
                        transport_info = self.parse_udp_header(data, ip_info)
                    else:
                        continue  # Skip non-TCP/UDP for now

                    if transport_info is None:
                        continue

                    # Filter by port if specified
                    if self.ports:
                        if (transport_info['src_port'] not in self.ports and
                            transport_info['dst_port'] not in self.ports):
                            continue

                    self.log_packet(ip_info, transport_info, proto_name)

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error processing packet: {e}")
                    continue

        except KeyboardInterrupt:
            print("\n" + "=" * 70)
            print("Capture stopped by user")
            self.show_summary()

    def show_summary(self):
        """Show capture summary."""
        print("\n" + "=" * 70)
        print("CAPTURE SUMMARY")
        print("=" * 70)
        print(f"Total packets captured: {self.packet_count}")
        print(f"Unique connections: {len(self.traffic_log)}")

        if self.traffic_log:
            print("\nUnique traffic flows:")
            for (src_ip, dst_ip, src_port, dst_port, proto), packets in sorted(self.traffic_log.items()):
                port_info = f"{self.format_port(src_port)} -> {self.format_port(dst_port)}"
                print(f"  {proto} {src_ip} -> {dst_ip} | {port_info} | {len(packets)} packets")

        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Brutal Legend Network Sniffer - Capture LAN traffic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python network_sniffer.py                    # Capture all traffic
  sudo python network_sniffer.py --port 27015       # Filter by single port
  sudo python network_sniffer.py --ports 27015,27016  # Filter by multiple ports

Note: Requires administrator/root privileges.
        """
    )

    parser.add_argument('--port', type=int, help='Single port to monitor')
    parser.add_argument('--ports', type=str, help='Comma-separated list of ports')
    parser.add_argument('--timeout', type=float, default=0.5, help='Socket timeout (default: 0.5)')

    args = parser.parse_args()

    # Determine ports to monitor
    ports = None
    if args.port:
        ports = {args.port}
    elif args.ports:
        ports = set(int(p.strip()) for p in args.ports.split(','))

    sniffer = PacketCapture(ports=ports, timeout=args.timeout)
    sniffer.capture_loop()


if __name__ == '__main__':
    main()
