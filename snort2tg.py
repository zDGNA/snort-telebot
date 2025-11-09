import time
import re
import requests
from pathlib import Path

BOT_TOKEN = "" #TOKEN BOT HERE
CHAT_ID   = "" #CHAT ID HERE

SNORT_ALERT_FILE = "/var/log/snort/snort.alert.fast"

INTERESTING = re.compile(r"ICMP|SYN|scan|DoS|SNMP|portscan|sweep|POTENTIALLY BAD|BAD TRAFFIC", re.IGNORECASE)

RATE_LIMIT_SECONDS = 1

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=data, timeout=8)
        if not r.ok:
            # Mencetak pesan error API dari Telegram
            print(f"Telegram error {r.status_code}: {r.text}") 
        return r.ok
    except Exception as e:
        # Mencetak error koneksi (jika ada masalah jaringan/DNS)
        print("Telegram send exception:", e) 
        return False


def tail_f(path):
    p = Path(path)
    
    # Loop untuk menunggu file alert Snort dibuat
    while not p.exists():
        print("Menunggu file:", path)
        time.sleep(1)

    with p.open("r", errors="ignore") as f:
        f.seek(0, 2)  # Pindah ke akhir file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.rstrip("\n")

def main():
    print(f"Monitoring: {SNORT_ALERT_FILE}")
    last_sent = 0

    for line in tail_f(SNORT_ALERT_FILE):
        if not line.strip():
            continue

        # Cek apakah alert cocok dengan pola yang kamu mau (Filter INTERESTING)
        if not INTERESTING.search(line):
            continue

        # Simple rate limit global untuk mencegah flood notifikasi
        now = time.time()
        if now - last_sent < RATE_LIMIT_SECONDS:
            continue

        alert_message = f"⚠️ SNORT ALERT ⚠️\n{line}"

        if send_telegram(alert_message):
            print("Sent:", line)
            last_sent = now
        else:
            print("GAGAL KIRIM:", line)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
