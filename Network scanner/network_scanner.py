#!/usr/bin/env python3
"""
Network Discovery + Port Scanner
Professional-grade tool for local network scanning
Author: Security Enthusiast
License: Educational Use Only
"""

import socket
import ipaddress
import threading
import subprocess
import sys
import argparse
import json
from datetime import datetime
from queue import Queue
import platform

class ProfessionalNetworkScanner:
    def __init__(self, network_cidr="192.168.1.0/24", ports=None, timeout=0.5, threads=100):
        self.network = network_cidr
        self.ports = ports or [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 5432, 5900, 8080]
        self.timeout = timeout
        self.max_threads = threads
        self.live_hosts = []
        self.open_ports = {}
        self.lock = threading.Lock()
        self.scan_start_time = None
        self.os_type = platform.system().lower()
        
        # Service detection mapping
        self.services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            443: "HTTPS",
            445: "SMB",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Alt"
        }
        
    def get_my_ip(self):
        """Get your local IP address (works cross-platform)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def ping_host(self, ip):
        """Check if host is alive (cross-platform ping)"""
        try:
            if self.os_type == "windows":
                # Windows ping command
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', str(ip)], 
                                      capture_output=True, timeout=2, text=True)
                # Windows returns 0 if host is up
                return str(ip) if result.returncode == 0 else None
            else:
                # Linux/Unix ping command
                result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                      capture_output=True, timeout=2)
                return str(ip) if result.returncode == 0 else None
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def _ping_and_store(self, ip):
        """Thread-safe ping and storage"""
        result = self.ping_host(ip)
        if result:
            with self.lock:
                self.live_hosts.append(result)
                print(f"  ✓ {result} - Host is alive")
    
    def discover_hosts(self):
        """Find all live hosts on network with threading"""
        print(f"\n[*] Discovering live hosts on {self.network}")
        print(f"[*] Your IP: {self.get_my_ip()}")
        print("[*] Scanning all hosts (this may take 30-60 seconds)...\n")
        
        threads = []
        network = ipaddress.IPv4Network(self.network, strict=False)
        
        # Count hosts (excluding network and broadcast)
        total_hosts = sum(1 for _ in network.hosts())
        print(f"[*] Total hosts to check: {total_hosts}")
        
        # Create thread pool for ping sweep
        for ip in network.hosts():
            thread = threading.Thread(target=self._ping_and_store, args=(ip,))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= self.max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for t in threads:
            t.join()
        
        # Sort hosts for consistent output
        self.live_hosts.sort()
    
    def grab_banner(self, ip, port):
        """Attempt to grab service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            
            # Send a generic probe for some services
            probes = {
                80: b"GET / HTTP/1.0\r\n\r\n",
                443: b"HEAD / HTTP/1.0\r\n\r\n",
                22: b"SSH-2.0-ClientTest\r\n",
                21: b"HELP\r\n",
                25: b"EHLO test\r\n"
            }
            
            probe = probes.get(port, b"\r\n")
            sock.send(probe)
            
            # Receive banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            # Clean up banner (first line only usually)
            banner = banner.split('\n')[0][:100]
            return banner if banner else "No banner"
            
        except:
            return "No banner"
    
    def scan_port(self, ip, port):
        """Check if specific port is open and grab banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                # Port is open - grab banner
                banner = self.grab_banner(ip, port)
                service = self.services.get(port, "Unknown")
                
                with self.lock:
                    if ip not in self.open_ports:
                        self.open_ports[ip] = []
                    self.open_ports[ip].append({
                        'port': port,
                        'service': service,
                        'banner': banner
                    })
                    
                    print(f"    [+] {ip}:{port} OPEN - {service}")
                    if banner and banner != "No banner":
                        print(f"        → Banner: {banner[:80]}")
            sock.close()
            
        except:
            pass
    
    def scan_host_ports(self, ip):
        """Scan ports on a specific host with threading"""
        print(f"\n[*] Scanning {ip} for open ports...")
        
        threads = []
        for port in self.ports:
            thread = threading.Thread(target=self.scan_port, args=(ip, port))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for t in threads:
            t.join()
    
    def save_results(self, filename=None):
        """Save scan results to file"""
        if not filename:
            filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results = {
            'scan_time': self.scan_start_time,
            'network': self.network,
            'total_hosts_scanned': sum(1 for _ in ipaddress.IPv4Network(self.network).hosts()),
            'live_hosts': self.live_hosts,
            'open_ports': self.open_ports,
            'summary': {
                'total_live_hosts': len(self.live_hosts),
                'total_open_ports': sum(len(ports) for ports in self.open_ports.values())
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n[✓] Results saved to {filename}")
        except Exception as e:
            print(f"\n[!] Failed to save results: {e}")
    
    def run(self, save_output=False):
        """Execute full network scan"""
        print("="*70)
        print("  PROFESSIONAL NETWORK SCANNER v2.0")
        print("="*70)
        print(f"  Target Network: {self.network}")
        print(f"  Ports to Scan: {len(self.ports)} ports")
        print(f"  Timeout: {self.timeout}s")
        print(f"  Max Threads: {self.max_threads}")
        print("="*70)
        
        self.scan_start_time = datetime.now().isoformat()
        
        # Discover hosts
        self.discover_hosts()
        
        # Scan ports on discovered hosts
        if self.live_hosts:
            print(f"\n[+] Found {len(self.live_hosts)} live host(s)")
            print("-"*70)
            
            for host in self.live_hosts:
                self.scan_host_ports(host)
        else:
            print("\n[!] No live hosts found!")
            print("[*] Suggestions:")
            print("    1. Check your network range (run: ipconfig / ifconfig)")
            print("    2. Try increasing timeout (--timeout 2)")
            print("    3. Disable firewall temporarily for testing")
            return
        
        # Print summary
        self.print_summary()
        
        # Save results if requested
        if save_output:
            self.save_results()
    
    def print_summary(self):
        """Print scan summary"""
        print("\n" + "="*70)
        print("SCAN SUMMARY")
        print("="*70)
        
        if self.open_ports:
            total_ports = sum(len(ports) for ports in self.open_ports.values())
            print(f"\n✓ Found {total_ports} open port(s) across {len(self.open_ports)} host(s)\n")
            
            for ip, ports in self.open_ports.items():
                print(f"📡 {ip}:")
                for p in ports:
                    print(f"   Port {p['port']:5d} - {p['service']:<10} - {p['banner'][:60]}")
                print()
        else:
            print("\n[!] No open ports found on any host")
            print("[*] Possible reasons:")
            print("    - Firewall blocking connections")
            print("    - All hosts are fully protected")
            print("    - Port range doesn't include services these hosts run")
        
        # Calculate scan duration
        if self.scan_start_time:
            start = datetime.fromisoformat(self.scan_start_time)
            duration = datetime.now() - start
            print(f"⏱️  Scan completed in {duration.total_seconds():.2f} seconds")

def main():
    parser = argparse.ArgumentParser(
        description='Professional Network Scanner - Discover hosts and scan ports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan your entire network with default settings
  python network_scanner.py
  
  # Scan specific network with custom ports
  python network_scanner.py -n 192.168.1.0/24 -p 22,80,443,3306
  
  # Fast scan with lower timeout
  python network_scanner.py -t 0.3 -m 200
  
  # Save results to file
  python network_scanner.py -n 10.0.0.0/24 -o
        """
    )
    
    parser.add_argument('-n', '--network', 
                       default=None,
                       help='Network range (e.g., 192.168.1.0/24)')
    
    parser.add_argument('-p', '--ports', 
                       default=None,
                       help='Ports to scan (comma-separated, e.g., 22,80,443)')
    
    parser.add_argument('-t', '--timeout', 
                       type=float, 
                       default=0.5,
                       help='Connection timeout in seconds (default: 0.5)')
    
    parser.add_argument('-m', '--max-threads', 
                       type=int, 
                       default=100,
                       help='Maximum concurrent threads (default: 100)')
    
    parser.add_argument('-o', '--output', 
                       action='store_true',
                       help='Save results to JSON file')
    
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Auto-detect network if not provided
    if not args.network:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            network_parts = local_ip.split('.')
            network = f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}.0/24"
            print(f"[*] Auto-detected network: {network}")
        except:
            network = "192.168.1.0/24"
            print(f"[*] Using default network: {network}")
    else:
        network = args.network
    
    # Parse ports if provided
    ports = None
    if args.ports:
        try:
            ports = [int(p.strip()) for p in args.ports.split(',')]
            print(f"[*] Custom port list: {ports}")
        except:
            print("[!] Invalid port list. Using defaults.")
    
    # Safety warning
    print("\n" + "!"*70)
    print("⚠️  WARNING: Only scan networks you own or have explicit permission to test!")
    print("    Unauthorized scanning may be illegal and unethical.")
    print("!"*70 + "\n")
    
    # Create and run scanner
    scanner = ProfessionalNetworkScanner(
        network_cidr=network,
        ports=ports,
        timeout=args.timeout,
        threads=args.max_threads
    )
    
    try:
        scanner.run(save_output=args.output)
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        if args.output and scanner.live_hosts:
            print("[*] Saving partial results...")
            scanner.save_results()
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
