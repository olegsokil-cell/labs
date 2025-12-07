FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    rsh-redone-client rsh-redone-server openbsd-inetd \
    python3 python3-pip tcpdump net-tools iputils-ping \
    iproute2 vim && rm -rf /var/lib/apt/lists/*
RUN pip3 install scapy
RUN echo "shell stream tcp nowait root /usr/sbin/in.rshd in.rshd" >> /etc/inetd.conf
RUN touch /root/.rhosts && chmod 644 /root/.rhosts
WORKDIR /root
