import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import time
from datetime import datetime

# ==========================================
# KONFIGURASI (PALING CEPAT)
# ==========================================
MAX_SIZE_BYTES = 5 * 1024 * 1024 * 1024 # 5 GB
CHUNK_SIZE = 30 * 1024 * 1024 # Baca 30 MB sekaligus (Maksimal I/O)
INTERVAL_UI = 500 # Update tampilan terminal tiap 500 baris

KATEGORI = [
    ("cPanel", [":2082", ":2083", "/cpanel"]),
    ("WHM", [":2086", ":2087", "/whm"]),
    ("Webmail", [":2095", ":2096", "/webmail", "/roundcube"]),
    ("SMTP", [":25", ":465", ":587", "/smtp"]),
    ("Plesk", [":8443", "/plesk"]),
    ("DirectAdmin", [":2222", "/directadmin"]),
    ("Wordpress", ["/wp-login", "/wp-admin", "/xmlrpc"]),
    ("Joomla", ["/administrator", "/joomla"]),
    ("Magento", ["/magento", "/admin"]),
    ("Prestashop", ["/prestashop", "/admin"]),
    ("OpenCart", ["/opencart", "/admin"]),
    ("Nas Synology", [":5000", ":5001", "/synology"]),
    ("Edu Domains", [".edu", ".ac.id"]),
    ("Gov Domains", [".gov", ".go.id"]),
    ("ID Domains", [".id", ".co.id", ".web.id"]),
    ("PayPal", ["paypal"]),
    ("Facebook", ["facebook"]),
    ("UbiSoft", ["ubisoft"]),
    ("Lainnya", [])
]

def open_file_manager(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def get_category(line_lower):
    for nama_kat, keywords in KATEGORI:
        if nama_kat == "Lainnya":
            continue
        for kw in keywords:
            if kw in line_lower:
                return nama_kat
    return "Lainnya"

def get_unique_folder(base_name):
    folder = base_name
    counter = 1
    while os.path.exists(folder):
        folder = f"{base_name}_{counter}"
        counter += 1
    return folder

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # --- TAMPILAN HEADER (CLEAN & ANTI ERROR) ---
    print("==========================================================")
    print("                  GALEN CLOUD CYBER                       ")
    print("==========================================================\n")
    # --------------------------------------------
    
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Pilih File TXT (Maksimal 5 GB)",
        filetypes=[("Text Files", "*.txt")]
    )
    
    if not file_paths:
        sys.exit(0)

    total_size = sum(os.path.getsize(fp) for fp in file_paths)
    if total_size > MAX_SIZE_BYTES:
        messagebox.showerror("Error", "Total ukuran melebihi batas 5 GB.")
        sys.exit(1)

    hari_ini = datetime.now().strftime("%d_%B_%Y")
    base_folder_name = f"hasil_logs_{hari_ini}"
    output_dir = get_unique_folder(base_folder_name)
    os.makedirs(output_dir)
    
    print(f"Folder output dibuat: {output_dir}\n")
    print("Memulai ekstraksi (Mohon tunggu, sedang di top speed)...\n")

    data_ram = {nama_kat: [] for nama_kat, _ in KATEGORI}
    seen_lines = set() 
    
    total_diproses = 0
    total_duplikat = 0
    current_line_counter = 0
    sisa_teks = "" 
    waktu_mulai = time.time()

    for file_path in file_paths:
        nama_file = os.path.basename(file_path)
        current_line_counter = 0
        sisa_teks = ""
        
        if len(nama_file) > 30: 
            nama_file_print = nama_file[:27] + "..."
        else: 
            nama_file_print = nama_file

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                text = sisa_teks + chunk.decode('utf-8', errors='ignore')
                lines = text.splitlines()
                
                if chunk[-1:] != b'\n':
                    sisa_teks = lines.pop()
                else:
                    sisa_teks = ""

                for line in lines:
                    current_line_counter += 1
                    line = line.strip()
                    if not line:
                        continue
                        
                    if not line.startswith("http://") and not line.startswith("https://"):
                        line = "https://" + line
                        
                    if line in seen_lines:
                        total_duplikat += 1
                        continue
                        
                    seen_lines.add(line)
                    kategori = get_category(line.lower())
                    data_ram[kategori].append(line + "\n")
                    total_diproses += 1
                    
                    if len(data_ram[kategori]) >= 100000:
                        out_path = os.path.join(output_dir, f"ULP_{kategori}_@Galen_Cloud_Cyber.txt")
                        with open(out_path, "a", encoding="utf-8") as out_f:
                            out_f.writelines(data_ram[kategori])
                        data_ram[kategori].clear()
                    
                    # --- UPDATE LIVE PROGRESS (CETAK KE BAWAH) ---
                    if current_line_counter % INTERVAL_UI == 0:
                        str_line = f"{current_line_counter:,}".replace(",", ".")
                        # Menggunakan print() biasa agar mencetak ke bawah (enter baru)
                        print(f"prosessing - line - {str_line} - {nama_file_print}")

        if sisa_teks:
            current_line_counter += 1
            if not sisa_teks.startswith("http://") and not sisa_teks.startswith("https://"):
                sisa_teks = "https://" + sisa_teks
            if sisa_teks not in seen_lines:
                seen_lines.add(sisa_teks)
                kat = get_category(sisa_teks.lower())
                data_ram[kat].append(sisa_teks + "\n")

    # Cetak sisa baris terakhir
    str_line = f"{current_line_counter:,}".replace(",", ".")
    print(f"prosessing - line - {str_line} - {nama_file_print}")

    print("\nMenyimpan sisa data ke hardisk...")
    for kat, lines in data_ram.items():
        if lines:
            out_path = os.path.join(output_dir, f"ULP_{kat}_@Galen_Cloud_Cyber.txt")
            with open(out_path, "a", encoding="utf-8") as out_f:
                out_f.writelines(lines)

    waktu_selesai = time.time() - waktu_mulai
    print(f"\n? EKSTRAKSI SELESAI DALAM WAKTU {waktu_selesai:.2f} DETIK!")
    print(f"Total baris valid     : {total_diproses:,}")
    print(f"Total duplikat dibuang: {total_duplikat:,}")
    
    del seen_lines
    del data_ram
    
    time.sleep(1.5)
    open_file_manager(os.path.abspath(output_dir))
    sys.exit(0)

if __name__ == "__main__":
    main()