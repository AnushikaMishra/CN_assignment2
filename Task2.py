#!/usr/bin/env python3
import pexpect
import time
import os

def main():
    os.makedirs("results", exist_ok=True)
    
    print("==========================================")
    print("TASK 2B: SYN FLOOD ATTACK WITH MITIGATION")
    print("==========================================")
    
    print("[+] Starting Mininet...")
    cmd = "sudo mn --topo=single,2 --mac --switch=ovsk --controller=default"
    mn = pexpect.spawn(cmd, encoding='utf-8')
    mn.logfile = open('results/mininet_session_mitigated.log', 'w')

    mn.expect("mininet>")

    print("[+] Configuring h2 with SYN flood mitigation settings...")
    mn.sendline("h2 sysctl -w net.ipv4.tcp_max_syn_backlog=1024")
    mn.expect("mininet>")
    
    mn.sendline("h2 sysctl -w net.ipv4.tcp_syncookies=1")
    mn.expect("mininet>")
    print("[+] SYN cookies ENABLED for mitigation")
    
    mn.sendline("h2 sysctl -w net.ipv4.tcp_synack_retries=5")
    mn.expect("mininet>")
    
    mn.sendline("h2 sysctl -w net.ipv4.tcp_fin_timeout=30")
    mn.expect("mininet>")
    
    mn.sendline("h2 sysctl -w net.ipv4.tcp_tw_reuse=1") 
    mn.expect("mininet>")
    
    print("[+] Verifying TCP settings on h2...")
    mn.sendline("h2 sysctl -a | grep tcp_syncookies")
    mn.expect("mininet>")
    mn.sendline("h2 sysctl -a | grep tcp_max_syn_backlog")
    mn.expect("mininet>")
    mn.sendline("h2 sysctl -a | grep tcp_synack_retries")
    mn.expect("mininet>")

    print("[+] Starting iperf3 server on h2...")
    mn.sendline("h2 iperf3 -s -p 5201 &")
    mn.expect("mininet>")

    print("[+] Starting tcpdump on h1...")
    mn.sendline("h1 tcpdump -i h1-eth0 -w capture_mitigated.pcap &")
    mn.expect("mininet>")
    
    print("[+] Waiting 5 seconds for tcpdump to initialize...")
    time.sleep(5)
    
    print("[+] Starting legitimate iperf3 client traffic on h1...")
    mn.sendline("h1 iperf3 -c 10.0.0.2 -p 5201 -t 150 -b 5M &")
    mn.expect("mininet>")

    print("[+] Legitimate traffic running...")
    print("[+] Waiting 20 seconds before starting SYN flood on h1...")
    time.sleep(20)
    
    print("[+] Starting SYN flood attack...")
    mn.sendline("h1 hping3 -S -p 5201 --flood 10.0.0.2 &")
    mn.expect("mininet>")

    print("[+] SYN flood attack running...")
    print("[+] Waiting 100 seconds before stopping the attack...")
    time.sleep(100)
    
    print("[+] Stopping SYN flood attack...")
    mn.sendline("h1 pkill hping3")
    mn.expect("mininet>")

    print("[+] Waiting 20 seconds before stopping legitimate traffic...")
    time.sleep(20)
    
    print("[+] Stopping legitimate traffic...")
    mn.sendline("h1 pkill iperf3")
    mn.expect("mininet>")

    print("[+] Stopping tcpdump on h1...")
    mn.sendline("h1 pkill tcpdump")
    mn.expect("mininet>")
    
    print("[+] Copying pcap file for processing...")
    mn.sendline("h1 cp capture_mitigated.pcap /tmp/")
    mn.expect("mininet>")

    print("[+] Exiting Mininet...")
    mn.sendline("exit")
    mn.close()
    
    print("[+] Experiment completed successfully!")
    print("[+] Packet capture saved to: capture_mitigated.pcap")
    print("[+] To process the results, run: python processing_mitigated.py")

if __name__ == "__main__":
    main()