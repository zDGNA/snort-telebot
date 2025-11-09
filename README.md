<h1>🔬 Intrusion Detection System (IDS) Hibrida: Snort & Real-Time Telegram Notifier</h1>

Repositori ini berisi dokumentasi dan script untuk lab uji coba keamanan jaringan yang menerapkan NIDS (Network Intrusion Detection System) Snort di Ubuntu dan sistem notifikasi real-time Telegram Bot. Uji coba dilakukan menggunakan serangan simulasi dari Kali Linux.

<h3>🎯 Tujuan Proyek</h3>

Otomatisasi Deteksi: Mengimplementasikan Snort sebagai layanan systemd untuk memantau lalu lintas jaringan secara non-stop.

Notifikasi Real-time: Mengembangkan script Python untuk memantau log Snort dan mengirim alert kritis ke Telegram Bot, mengatasi keterlambatan respons.

Verifikasi Efektivitas: Menguji sistem IDS terhadap simulasi serangan jaringan umum (DDOS dan Port Scanning).


<h3>⚙️ Topologi Lab Uji Coba</h3>

| Komponen | Peran | Alamat IP / Interface |
| :--- | :--- | :--- |
| **Server IDS** | Ubuntu 20.04/22.04 LTS (Platform Snort) | `192.168.1.66` |
| **Klien Penyerang** | Kali Linux (Menggunakan hping3, nmap) | `192.168.1.50` |
| **Interface yang Dipantau** | Antarmuka Jaringan Utama (Snort) | `enp0s3` |
| **Telegram Bot**	| Sistem Notifikasi Real-time (Outbound)	|`API Telegram (Internet)`|


<h3>🛠️ Langkah-Langkah Instalasi dan Konfigurasi</h3>
1. Instalasi Prasyarat
Instal Snort dan dependensi Python di Ubuntu Server:


```
sudo apt update
sudo apt install snort python3 python3-pip
pip install requests pathlib
```

2. Konfigurasi Layanan Snort
File snort.service (ditempatkan di /etc/systemd/system/):

```
[Unit]
Description=Snort IDS
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/snort -A fast -q -c /etc/snort/snort.conf -i enp0s3
# Ganti 'enp0s3' dengan interface Anda
Restart=always
User=snort
Group=snort
# ... (pengaturan lain)

[Install]
WantedBy=multi-user.target
```
3. Konfigurasi Skrip Telegram (snort2tg.py)


Skrip harus ditempatkan di /usr/local/bin/ (Lihat full code di bawah ini). Pastikan variabel konfigurasi diubah.
```
# CODE: snort2tg.py (Bagian CONFIG)

# GANTI dengan BOT_TOKEN Telegram dan CHAT_ID Anda
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
CHAT_ID   = "YOUR_CHAT_ID_HERE"

# FILTER ALERT YANG DIPEBAIKI (penting untuk mendeteksi SYN Flood)
INTERESTING = re.compile(r"ICMP|SYN|scan|DoS|SNMP|portscan|sweep|POTENTIALLY BAD|BAD TRAFFIC", re.IGNORECASE)
```
4. Konfigurasi Layanan Telegram Notifier
File snort2tg.service (ditempatkan di /etc/systemd/system/):
```
[Unit]
Description=Snort Alert to Telegram Notifier
After=network.target snort.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/snort2tg.py
Restart=always
User=mvdxaa  # Gunakan user yang memiliki izin baca ke log Snort
Group=mvdxaa

[Install]
WantedBy=multi-user.target
```

<h3>🛡️ Aturan (Rule) Snort Kustom</h3>
Rule ini ditambahkan ke /etc/snort/rules/local.rules untuk mendeteksi flood dan aktivitas scan spesifik.

```
# Rule untuk mendeteksi Port Scan yang agresif
alert tcp any any -> $HOME_NET any (msg:"[CUSTOM] Possible Aggressive Port Scan Detected"; flags:S; detection_filter: track by_src, count 15, seconds 60; sid:1000001; rev:1;)

# Rule DDOS / SYN Flood (Akan memicu 'Potentially Bad Traffic')
alert ip any any -> $HOME_NET any (msg:"[CUSTOM] DDOS Traffic Anomaly Detected"; threshold: type both, track by_src, count 20, seconds 5; sid:1000002; rev:1;)
```

<h3>⚔️ Skenario Uji Coba dan Hasil</h3>
1. Uji Coba: SYN Flood Attack (DDOS)
Tujuan: Memverifikasi deteksi threshold Snort dan notifikasi real-time.

Perintah (dari Kali):

```
sudo hping3 -S --flood -p 80 192.168.1.66
```
Hasil:
Snort mencatat: [1:504:7] Notification: Potentially Bad Traffic...
Telegram Bot menerima notifikasi dengan cepat.

2. Uji Coba: Port Scanning
Tujuan: Memverifikasi deteksi rule Port Scan kustom (SID: 1000001).
Perintah (dari Kali):
```
sudo nmap -sS -p 1-1000 192.168.1.66
```
Hasil: Notifikasi [CUSTOM] Possible Aggressive Port Scan Detected masuk ke Telegram.
