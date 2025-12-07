# DNS Attack Lab - Quick Start Guide

## Setup (5 minutes)

```bash
cd /Users/Apple/Desktop/security_labs/lab9/dns-lab
docker compose up -d --build
```

Wait ~10 seconds for containers to start.

## Verify Setup

```bash
docker exec user-machine dig www.example.com @10.9.0.16 +short
# Should output: 192.168.0.101
```

---

## Run Attacks

### Task 5: Direct DNS Spoofing

**Terminal 1:**
```bash
docker exec -it attacker python3 /attack/task5_spoof_user.py
```

**Terminal 2:**
```bash
docker exec user-machine dig www.example.net
# Should show spoofed IP: 10.9.0.17
```

---

### Task 6: Cache Poisoning

```bash
# Flush cache first
docker exec dns-server rndc flush
```

**Terminal 1:**
```bash
docker exec -it attacker python3 /attack/task6_cache_poison.py
```

**Terminal 2:**
```bash
docker exec user-machine dig www.example.net
```

**Verify:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep example.net /var/cache/bind/dump.db
```

---

### Task 7: Authority Section Attack

```bash
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

**Check NS record:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep -A3 "example.net" /var/cache/bind/dump.db
```

---

### Task 8: Bailiwick Protection Test

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

**Verify google.com NOT in cache:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep google.com /var/cache/bind/dump.db
# Should return nothing
```

---

### Task 9: Additional Section

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

**Check which records cached:**
```bash
docker exec dns-server rndc dumpdb -cache
docker exec dns-server grep -E "example.net|facebook|attacker" /var/cache/bind/dump.db
```

---

## Useful Commands

```bash
# Access containers
docker exec -it attacker bash
docker exec -it dns-server bash
docker exec -it user-machine bash

# Flush DNS cache
docker exec dns-server rndc flush

# View cache
docker exec dns-server rndc dumpdb -cache
docker exec dns-server cat /var/cache/bind/dump.db

# Stop lab
docker compose down

# Restart lab
docker compose restart
```

---

## Troubleshooting

**DNS not responding:**
```bash
docker logs dns-server
docker exec dns-server rndc status
```

**Network issues:**
```bash
docker exec attacker ping 10.9.0.16
docker exec user-machine ping 10.9.0.16
```

**Rebuild everything:**
```bash
docker compose down
docker compose up -d --build
```

---

See [README.md](README.md) for detailed explanations and learning objectives.
