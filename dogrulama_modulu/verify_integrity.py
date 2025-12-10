import hashlib
import subprocess
import json
import sys

# --- AYARLAR ---
# Buraya Suiscan linkinden bulduğun o yeni OBJECT ID'yi yapıştır:
OBJECT_ID = "0xd2dd0daef960f1fd7d11eebde0f529d38a7fa50ded0435be5c3d3096b59de797" 
# ----------------

def calculate_file_hash(filepath):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                data = f.read(65536)
                if not data: break
                sha256.update(data)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def get_hash_from_blockchain(object_id):
    """
    Sui CLI kullanarak blokzincirdeki veriyi okur.
    """
    print(f"\n🌍 Blokzincire bağlanılıyor... (ID: {object_id})")
    
    command = ["sui", "client", "object", object_id, "--json"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print("❌ HATA: Nesne okunamadı.")
            return None
            
        data = json.loads(result.stdout)
        
        # Sui'nin JSON yapısından bizim veriyi çekiyoruz (fields kısmı)
        # Yapı: content -> fields -> image_hash
        if "content" in data and "fields" in data["content"]:
            fields = data["content"]["fields"]
            return {
                "hash": fields.get("image_hash"),
                "sensor": fields.get("sensor_id"),
                "desc": fields.get("description")
            }
        else:
            print("⚠️ Beklenmeyen veri formatı.")
            print(data) # Debug için
            return None

    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return None

def main():
    print("--- TEKNOFEST 2026: AI Veri Doğrulama Modülü ---\n")
    
    # 1. Kontrol edilecek resmi iste
    image_path = input("Doğrulanacak resmin yolunu gir: ").strip().strip('"')
    
    local_hash = calculate_file_hash(image_path)
    if not local_hash:
        print("Dosya bulunamadı!")
        return


    # 2. Blokzincirden orijinal kaydı çek
    blockchain_record = get_hash_from_blockchain(OBJECT_ID)
    
    if not blockchain_record:
        print("Blokzincir verisi alınamadı. Object ID doğru mu?")
        return

    chain_hash = blockchain_record["hash"]

    # --- DÜZELTME BURADA BAŞLIYOR ---
    # Eğer blokzincirden gelen veri '0x' ile başlıyorsa, ilk 2 karakteri silip temizliyoruz.
    if chain_hash.startswith("0x"):
        chain_hash = chain_hash[2:]
    # --------------------------------

    print("\n" + "="*50)
    print(f"🖼️  YEREL HASH:    {local_hash}")
    print(f"🔗 ZİNCİR HASH:   {chain_hash}  (Format temizlendi)")
    print(f"📝 SENSÖR BİLGİSİ: {blockchain_record['sensor']}")
    print("="*50 + "\n")

  
    # 3. KARŞILAŞTIRMA (BÜYÜK FİNAL)
    if local_hash == chain_hash:
        print("✅ [GÜVENLİ] Veri Bütünlüğü Doğrulandı.")
        print("   Resim orijinaldir, AI modeline gönderilebilir.")
    else:
        print("🚨 [KRİTİK UYARI] SALDIRI TESPİT EDİLDİ!")
        print("   Yerel dosya ile blokzincirdeki kayıt uyuşmuyor.")
        print("   Sistem bu veriyi reddetti.")

if __name__ == "__main__":
    main()