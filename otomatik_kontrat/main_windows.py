import hashlib
import os
import subprocess
import json
import time

# --- AYARLAR (BURAYI KENDİNE GÖRE DOLDUR) ---
# PowerShell çıktısından kopyaladığın Package ID'yi buraya yapıştır:
PACKAGE_ID = "0xd0c47a02ff0eeac402cfb2c5a1afb971c4ff5e10d3dedeb99b6307e0f167a7fc" 
MODULE_NAME = "storage"
FUNCTION_NAME = "save_hash"
# -------------------------------------------

def calculate_file_hash(filepath):
    """Windows dosya yolunu okur ve SHA-256 hash üretir."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except FileNotFoundError:
        print("Hata: Dosya bulunamadı!")
        return None

def save_to_blockchain(sensor_name, image_hash, description):
    """
    Python içinden Windows terminalini (PowerShell/CMD) tetikleyerek
    Sui Smart Contract'ını çalıştırır.
    """
    print(f"\n[BLOKZİNCİR] İşlem hazırlanıyor... (Hash: {image_hash[:10]}...)")
    
    # Windows için komut listesi
    # Not: Windows'ta 'sui' komutunun PATH'e ekli olması gerekir.
    command = [
        "sui", "client", "call",
        "--package", PACKAGE_ID,
        "--module", MODULE_NAME,
        "--function", FUNCTION_NAME,
        "--args", sensor_name, image_hash, description,
        "--gas-budget", "10000000",
        "--json"  # Çıktıyı JSON formatında al ki işleyebilelim
    ]

    try:
        # subprocess.run Windows'ta komutu çalıştırır
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            output_json = json.loads(result.stdout)
            # Transaction Digest (İşlem Kimliği) alalım
            tx_digest = output_json.get("digest")
            print(f"✅ BAŞARILI! Veri Sui Ağına Kaydedildi.")
            print(f"🔗 İşlem Kimliği (Tx ID): {tx_digest}")
            print(f"🌍 Explorer Linki: https://suiscan.xyz/testnet/tx/{tx_digest}")
            return True
        else:
            print("❌ HATA: Blokzincir işlemi başarısız oldu.")
            print("Hata Detayı:", result.stderr)
            return False

    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return False

def main():
    print("--- TEKNOFEST 2026: Windows AI-Integrity Modülü ---\n")
    
    # Windows'ta dosya yolu örnekleri: C:\Users\Ad\Desktop\resim.jpg
    image_path = input("Resim dosyasının tam yolunu veya adını gir: ").strip().strip('"') 
    # strip('"') Windows'ta "Sağ Tık -> Yol Olarak Kopyala" yapınca gelen tırnakları siler.

    # 1. Hash Hesapla
    file_hash = calculate_file_hash(image_path)
    
    if file_hash:
        print(f"🔑 Hash Hesaplandı: {file_hash}")
        
        # 2. Blokzincire Yaz
        sensor_name = "Kamera-Win-01"
        description = "Guvenlik Taramasi Logu"
        
        save_to_blockchain(sensor_name, file_hash, description)

if __name__ == "__main__":
    main()