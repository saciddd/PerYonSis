import os

# Taranmasını istediğin klasör ve dosyalar (Burayı kendi yapına göre güncelle)
# Sadece iş kurallarının (657 modülünün) olduğu klasörü hedef göstermen yeterli.
TARGET_DIR = "d:/Github/PerYonSis/PersonelYonSis/mercis657" 
OUTPUT_FILE = "ai_ready_codebase.md"
ALLOWED_EXTENSIONS = ['.py'] # İhtiyaca göre .js, .html eklenebilir

def generate_ai_ready_file():
    print("🚀 Kod analiz scripti başlatıldı...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write("# PERSONELYÖNSİS - ÇİZELGE 657 MODÜLÜ KOD YAPISI VE İŞ AKIŞLARI\n")
        outfile.write("Bu döküman, yapay zeka modelinin mevzuat eşleştirmesi yapabilmesi için otomatik üretilmiştir.\n\n")
        
        # 1. Klasör Ağacını Çıkaralım (AI'ın sistemi anlaması için)
        outfile.write("## 1. DOSYA HİYERARŞİSİ\n```text\n")
        for root, dirs, files in os.walk(TARGET_DIR):
            # Git ve cache klasörlerini pas geç
            if any(p in root for p in ['__pycache__', '.git', 'migrations']):
                continue
            level = root.replace(TARGET_DIR, '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    outfile.write(f'{subindent}{f}\n')
        outfile.write("```\n\n---\n\n")
        
        # 2. Dosya İçeriklerini Ekleyelim
        outfile.write("## 2. DOSYA İÇERİKLERİ VE KODLAR\n\n")
        for root, dirs, files in os.walk(TARGET_DIR):
            if any(p in root for p in ['__pycache__', '.git', 'migrations']):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, TARGET_DIR)
                    
                    print(f"Okunuyor: {relative_path}")
                    outfile.write(f"### Dosya: {relative_path}\n")
                    outfile.write(f"Path: `{full_path}`\n\n")
                    outfile.write("```python\n")
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"# Dosya okunurken hata oluştu: {str(e)}")
                        
                    outfile.write("\n```\n\n---\n\n")
                    
    print(f"✅ İşlem tamamlandı! '{OUTPUT_FILE}' dosyası oluşturuldu. Bu dosyayı AI modeline yükleyebilirsin.")

if __name__ == "__main__":
    generate_ai_ready_file()