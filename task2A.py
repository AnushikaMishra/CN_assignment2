import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

SYN = 0x02
FIN = 0x01
ACK = 0x10
RST = 0x04
DEFAULT = 100.0


def analyze_pcap(pcap, output, start=None, end=None):
    print(f"[+] Analyzing: {pcap}")
    cmd = (
        f"tshark -r {pcap} -T fields "
        f"-e frame.time_epoch -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags "
        f"-E header=y -E separator=, -E quote=d -E occurrence=f > details_{pcap.split('.')[0]}.csv"
    )
    print(f"[+] Running: {cmd}")
    os.system(cmd)

    csv_file = f"details_{pcap.split('.')[0]}.csv"
    print(f"[+] Reading: {csv_file}")
    data = pd.read_csv(csv_file)

    data.rename(
        columns={
            "frame.time_epoch": "time",
            "ip.src": "src",
            "ip.dst": "dst",
            "tcp.srcport": "sport",
            "tcp.dstport": "dport",
            "tcp.flags": "flags",
        },
        inplace=True,
    )

    data["time"] = data["time"].astype(float)
    if len(data) > 0:
        start_time = data["time"].min()
        data["relative"] = data["time"] - start_time
    else:
        print("[!] Warning: No packets found.")
        return

    def parse_flags(f):
        try:
            f = str(f).strip()
            if f.startswith("0x") or f.startswith("0X"):
                return int(f, 16)
            return int(f)
        except:
            return 0

    data["flags"] = data["flags"].apply(parse_flags)
    data["conn"] = data.apply(lambda r: (r["src"], r["dst"], r["sport"], r["dport"]), axis=1)
    data.sort_values("time", inplace=True)

    conns = {}
    results = []

    for _, r in data.iterrows():
        c = r["conn"]
        t = r["time"]
        rt = r["relative"]
        f = r["flags"]

        if f & SYN:
            if c not in conns:
                conns[c] = {"start": t, "rel_start": rt, "end": None, "rel_end": None}

        if (f & FIN and f & ACK) or (f & RST):
            if c in conns and conns[c]["end"] is None:
                conns[c]["end"] = t
                conns[c]["rel_end"] = rt

    print(f"[+] Calculating durations for {len(conns)} connections")
    for c, times in conns.items():
        s = times["start"]
        rs = times["rel_start"]
        e = times["end"] if times["end"] is not None else (s + DEFAULT)
        re = times["rel_end"] if times["rel_end"] is not None else (rs + DEFAULT)
        d = e - s
        results.append((s, rs, d))

    res_df = pd.DataFrame(results, columns=["start", "relative", "duration"])
    res_df.to_csv(output, index=False)
    print(f"[+] Results saved to {output}")

    return res_df


def plot_durations(orig_csv, mit_csv, output):
    print(f"[+] Plotting: {orig_csv} and {mit_csv}")

    try:
        df_o = pd.read_csv(orig_csv)
        df_m = pd.read_csv(mit_csv)
    except Exception as e:
        print(f"[!] Error: {e}")
        return

    plt.figure(figsize=(18, 8))

    plt.scatter(df_o["relative"], df_o["duration"], label="Without Mitigation", alpha=0.6, color="red", marker="o")
    plt.scatter(df_m["relative"], df_m["duration"], label="With Mitigation", alpha=0.6, color="green", marker="x")

    plt.axvline(x=20, color="black", linestyle="--", label="Attack Start (20s)")
    plt.axvline(x=120, color="black", linestyle="-.", label="Attack End (120s)")

    plt.xlabel("Connection Start Time (seconds)")
    plt.ylabel("Connection Duration (seconds)")
    plt.title("TCP Connection Durations: With vs. Without SYN Flood Mitigation")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")

    plt.ylim(0, min(plt.ylim()[1], DEFAULT * 1.1))

    plt.text(22, DEFAULT * 0.95, "SYN Flood Attack Period", fontsize=10)

    o_conns = df_o[(df_o["relative"] >= 20) & (df_o["relative"] <= 120)]
    m_conns = df_m[(df_m["relative"] >= 20) & (df_m["relative"] <= 120)]

    stats = (
        f"Statistics during attack:\n"
        f"Without mitigation: {len(o_conns)} connections, "
        f"Avg duration: {o_conns['duration'].mean():.2f}s\n"
        f"With mitigation: {len(m_conns)} connections, "
        f"Avg duration: {m_conns['duration'].mean():.2f}s"
    )

    plt.figtext(0.90, 0.95, stats, fontsize=10, bbox=dict(facecolor="white", alpha=0.8), horizontalalignment='right', verticalalignment='top')

    plt.tight_layout()
    plt.savefig(output, dpi=300)
    print(f"[+] Plot saved to {output}")
    plt.show()


def main():
    os.makedirs("results", exist_ok=True)

    print("=============================================")
    print("TASK 2B: PROCESSING MITIGATED SYN FLOOD DATA")
    print("=============================================")

    orig_pcap = "capture.pcap"
    orig_csv = "results/original.csv"
    mit_pcap = "capture_mitigated.pcap"
    mit_csv = "results/mitigated.csv"

    plot_file = "results/comparison.png"
    plot_durations(orig_csv, mit_csv, plot_file)

    print("\n[+] Analysis complete!")
    print(f"[+] Plot saved to: {plot_file}")
    print("[+] Include this plot in your report.")
    print("[+] Include Wireshark screenshots for Task 2B.")


if __name__ == "__main__":
    main()