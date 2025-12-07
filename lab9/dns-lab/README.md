# DNS Attack Lab

This lab demonstrates various DNS attack techniques including DNS spoofing, cache poisoning, and authority section attacks using Docker containers.

## Lab Architecture

- **attacker** (10.9.0.17) - Attacker machine with Scapy for crafting packets
- **dns-server** (10.9.0.16) - Local DNS server running BIND9
- **user-machine** (10.9.0.18) - User machine that queries DNS

## Quick Start

### 1. Setup

```bash
cd /Users/Apple/Desktop/security_labs/lab9/dns-lab
./setup.sh
```

Or manually:

```bash
docker-compose up -d --build
```

### 2. Verify Setup

```bash
# Test DNS resolution
docker exec user-machine dig www.example.com @10.9.0.16

# Should return: 192.168.0.101
```

📸 **Screenshot Required** - DNS resolution working

---

## Lab Tasks

### Task 1-3: DNS Server Setup (Already Complete)

The Docker setup automatically configures:
- BIND9 DNS server with example.com zone
- Fixed source port (33333) for easier attacks
- Cache dumping enabled

**Verify:**

```bash
# Check DNS server is responding
docker exec user-machine dig www.example.com @10.9.0.16

# Verify zone file is loaded
docker exec dns-server named-checkzone example.com /etc/bind/example.com.db
```

📸 **Screenshot** - `dig` output showing your DNS server responded

---

### Task 4: Modify Host File

Demonstrates that `/etc/hosts` is checked before DNS.

```bash
# Add fake entry
docker exec user-machine bash -c "echo '1.2.3.4 www.bank32.com' >> /etc/hosts"

# Test with ping (uses /etc/hosts)
docker exec user-machine ping -c 2 www.bank32.com

# Compare with dig (bypasses /etc/hosts)
docker exec user-machine dig www.bank32.com
```

**Expected Result:**
- `ping` uses 1.2.3.4 (from /etc/hosts)
- `dig` shows real IP from DNS

📸 **Screenshot** - Show both outputs side-by-side

---

### Task 5: Direct DNS Spoofing to User

Intercept DNS queries from user and send fake responses.

**Terminal 1** - Start attack:
```bash
docker exec -it attacker python3 /attack/task5_spoof_user.py
```

**Terminal 2** - Trigger query:
```bash
docker exec user-machine dig www.example.net
```

**Expected Result:**
- Attacker intercepts query
- User receives fake IP: 10.9.0.17

📸 **Screenshot** - Attack output + dig result showing spoofed IP

---

### Task 6: DNS Cache Poisoning

Poison the DNS server's cache by racing the real DNS response.

**Preparation:**
```bash
# Flush cache first
docker exec dns-server rndc flush
```

**Terminal 1** - Start attack:
```bash
docker exec -it attacker python3 /attack/task6_cache_poison.py
```

**Terminal 2** - Trigger query:
```bash
docker exec user-machine dig www.example.net
```

**Terminal 3** - Verify cache:
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep example.net /var/cache/bind/dump.db
```

**Expected Result:**
- Cache contains poisoned entry
- Subsequent queries return fake IP without asking upstream

📸 **Screenshot** - Cache dump showing poisoned record

---

### Task 7: Authority Section Attack

Inject malicious NS records in the authority section.

```bash
# Flush cache
docker exec dns-server rndc flush
```

**Terminal 1:**
```bash
docker exec -it attacker python3 /attack/task7_authority.py
```

**Terminal 2:**
```bash
docker exec user-machine dig www.example.net
```

**Verify NS record cached:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep -A5 "example.net" /var/cache/bind/dump.db
```

**Expected Result:**
- Cache shows `example.net NS ns.attacker32.com`
- Future queries for `*.example.net` will go to attacker's NS

📸 **Screenshot** - Cache showing malicious NS record

---

### Task 8: Targeting Another Domain (Bailiwick Protection)

Attempt to poison cache for unrelated domains - should **FAIL**.

```bash
docker exec dns-server rndc flush
```

**Terminal 1:**
```bash
docker exec -it attacker python3 /attack/task8_other_domain.py
```

**Terminal 2:**
```bash
docker exec user-machine dig www.example.net
```

**Verify protection worked:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep google.com /var/cache/bind/dump.db
```

**Expected Result:**
- `google.com` should **NOT** appear in cache
- DNS server rejects out-of-bailiwick records

📸 **Screenshot** - Cache showing google.com is NOT present

---

### Task 9: Additional Section Analysis

Test which additional records are accepted.

```bash
docker exec dns-server rndc flush
```

**Terminal 1:**
```bash
docker exec -it attacker python3 /attack/task9_additional.py
```

**Terminal 2:**
```bash
docker exec user-machine dig www.example.net
```

**Analyze results:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server cat /var/cache/bind/dump.db | grep -E "example.net|facebook|attacker"
```

**Expected Result:**
- Related records (`*.example.net`) - **CACHED**
- Unrelated records (`facebook.com`) - **REJECTED**

📸 **Screenshot** - Cache analysis showing which records accepted

---

## Useful Commands

### Container Management
```bash
# Start lab
docker-compose up -d

# Stop lab
docker-compose down

# View logs
docker logs dns-server
docker logs attacker

# Access containers
docker exec -it attacker bash
docker exec -it dns-server bash
docker exec -it user-machine bash
```

### DNS Server Management
```bash
# Flush DNS cache
docker exec dns-server rndc flush

# Dump cache to file
docker exec dns-server rndc dumpdb -cache

# View cache
docker exec dns-server cat /var/cache/bind/dump.db

# Reload configuration
docker exec dns-server rndc reload

# Check BIND status
docker exec dns-server rndc status
```

### Debugging
```bash
# Capture DNS traffic
docker exec attacker tcpdump -i eth0 -n port 53

# Test DNS query
docker exec user-machine dig www.example.com @10.9.0.16

# Check DNS server logs
docker exec dns-server tail -f /var/log/syslog
```

---

## Screenshot Checklist

| Task | Screenshot | Status |
|------|-----------|--------|
| 1-3 | DNS server responding to queries | ⬜ |
| 4 | `/etc/hosts` vs DNS resolution | ⬜ |
| 5 | Direct spoofing attack success | ⬜ |
| 6 | Cache poisoning successful | ⬜ |
| 7 | Malicious NS record in cache | ⬜ |
| 8 | Bailiwick protection working | ⬜ |
| 9 | Additional section filtering | ⬜ |

---

## Troubleshooting

### DNS server not responding
```bash
# Check if BIND is running
docker exec dns-server service bind9 status

# Restart BIND
docker exec dns-server service bind9 restart
```

### Attack scripts not working
```bash
# Check network connectivity
docker exec attacker ping -c 2 10.9.0.16

# Verify Scapy is installed
docker exec attacker python3 -c "from scapy.all import *"
```

### Cache not updating
```bash
# Force flush
docker exec dns-server rndc flush

# Check cache file permissions
docker exec dns-server ls -la /var/cache/bind/
```

---

## Learning Objectives

After completing this lab, you should understand:

1. How DNS resolution works (hosts file → DNS)
2. DNS packet structure (questions, answers, authority, additional)
3. DNS cache poisoning techniques
4. How to craft DNS packets with Scapy
5. DNS security mechanisms (bailiwick checking)
6. Why source port randomization is important
7. The Kaminsky attack concept

---

## Clean Up

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (if any)
docker-compose down -v

# Remove images (optional)
docker rmi dns-lab_attacker dns-lab_dns-server dns-lab_user-machine
```

---

## References

- SEED Labs DNS Attack Lab
- RFC 1035 - Domain Names
- Kaminsky DNS Vulnerability (2008)
- BIND9 Documentation

---

**Good luck with your DNS attack experiments!** 🔐
