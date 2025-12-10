import hashlib
import os
import numpy as np
from PIL import Image

def calculate_file_hash(filepath):
    """
    Belirtilen dosyanın binary (ikili) okuma modunda SHA-256 özetini çıkarır.
    Bu, dosyanın diskteki fiziksel 'parmak izidir'.
    """
    sha256 = hashlib.sha256()
    
    # Dosyayı parça parça okuyoruz (Büyük resimlerde RAM şişmesin diye)
    with open(filepath, "rb") as f:
        while True:
            data = f.read(65536) # 64kb bloklar halinde oku
            if not data:
                break
            sha256.update(data)
            
    return sha256.hexdigest()

def simulate_attack(input_path, output_path):
    """
    Resmi açar, 1 pikselini değiştirir ve yeni bir dosya olarak kaydeder.
    """
    try:
        # Resmi aç
        img = Image.open(input_path)
        img = img.convert("RGB") # Renk formatını sabitle
        
        # Matematiksel diziye çevir
        data = np.array(img)
        
        # SALDIRI: (0,0) noktasındaki pikselin Kırmızı tonunu 1 birim değiştir
        # Eğer değer 255 ise 254 yap, değilse 1 artır.
        original_value = data[0, 0, 0]
        new_value = 254 if original_value == 255 else original_value + 1
        data[0, 0, 0] = new_value
        
        # Yeni resmi oluştur ve kaydet
        new_img = Image.fromarray(data)
        new_img.save(output_path)
        
        print(f"\n[Saldırı Bilgisi] (0,0) pikseli değiştirildi.")
        print(f"Eski RGB: {original_value} -> Yeni RGB: {new_value}")
        return True
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return False

def main():
    print("--- TEKNOFEST 2026: Gerçek Resim Bütünlük Testi ---\n")
    
    # Kullanıcıdan dosya adı iste
    image_path = input("Hash'ini almak istediğin resmin adını/yolunu yaz (örn: test.jpg): ").strip()
    
    # Dosya var mı kontrol et
    if not os.path.exists(image_path):
        print("HATA: Dosya bulunamadı! Lütfen ismin doğru olduğundan emin ol.")
        return

    # 1. ADIM: Orijinal Dosyanın Hash'ini Al
    original_hash = calculate_file_hash(image_path)
    print("\n" + "="*60)
    print(f"📂 ORİJİNAL DOSYA: {image_path}")
    print(f"🔑 SHA-256 HASH:  {original_hash}")
    print("="*60)

    # 2. ADIM: Saldırı Simülasyonu
    print("\n... Saldırı simülasyonu başlatılıyor (Piksel Manipülasyonu) ...")
    attacked_filename = "hacked_" + os.path.basename(image_path)
    
    # Orijinal dosyanın bozulmaması için farklı isimle kaydediyoruz
    if filename_split := os.path.splitext(attacked_filename):
         # Çıktıyı her zaman PNG yapalım ki sıkıştırma kaybı olmasın, net piksel değişimi görülsün
         attacked_filename = filename_split[0] + ".png"

    success = simulate_attack(image_path, attacked_filename)

    if success:
        # 3. ADIM: Saldırıya Uğramış Dosyanın Hash'ini Al
        attacked_hash = calculate_file_hash(attacked_filename)
        
        print("\n" + "="*60)
        print(f"⚠️  SALDIRI DOSYASI: {attacked_filename}")
        print(f"🔑 YENİ HASH:       {attacked_hash}")
        print("="*60)
        
        # SONUÇ
        if original_hash != attacked_hash:
            print("\n✅ SİSTEM BAŞARILI: Hash değişti! Manipülasyon tespit edildi.")
            print("   İki resme yan yana bak, farkı gözle göremezsin ama Hash affetmez.")
        else:
            print("\n❌ HATA: Hashler aynı. Bir şeyler ters gitti.")

if __name__ == "__main__":
    main()