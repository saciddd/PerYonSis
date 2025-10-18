import os
import sys
import django

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PersonelYonSis.settings')
django.setup()

from mercis657.models import SabitMesai

def test_sabit_mesailer():
    print("=== SabitMesai Verilerini Test Etme ===")
    print()
    
    try:
        # Raw SQL ile verileri çek
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai")
            rows = cursor.fetchall()
        
        print(f"Toplam {len(rows)} adet SabitMesai kaydi bulundu.")
        print()
        
        for i, (id, aralik, ara_dinlenme) in enumerate(rows, 1):
            print(f"{i}. Kayit:")
            print(f"   ID: {id}")
            print(f"   Aralik: {aralik}")
            print(f"   Ara Dinlenme (Raw): {ara_dinlenme}")
            
            # ara_dinlenme değerini test et
            try:
                if ara_dinlenme is not None:
                    float(ara_dinlenme)
                    print(f"   OK - ara_dinlenme gecerli: {ara_dinlenme}")
                else:
                    print(f"   INFO - ara_dinlenme null")
            except (ValueError, TypeError) as e:
                print(f"   HATA - ara_dinlenme HATALI: {ara_dinlenme} - Hata: {e}")
            
            print()
            
    except Exception as e:
        print(f"HATA olustu: {e}")

def test_problemli_kayitlar():
    print("=== Problemli Kayitlari Bulma ===")
    print()
    
    problemli_kayitlar = []
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai")
            rows = cursor.fetchall()
        
        for id, aralik, ara_dinlenme in rows:
            try:
                if ara_dinlenme is not None:
                    float(ara_dinlenme)
            except (ValueError, TypeError):
                problemli_kayitlar.append((id, aralik, ara_dinlenme))
    except Exception as e:
        print(f"HATA olustu: {e}")
        return
    
    if problemli_kayitlar:
        print(f"HATA - {len(problemli_kayitlar)} adet problemli kayit bulundu:")
        for id, aralik, ara_dinlenme in problemli_kayitlar:
            print(f"   ID: {id}, Aralik: {aralik}, Ara Dinlenme: {ara_dinlenme}")
    else:
        print("OK - Tum kayitlar gecerli!")

def duzelt_problemli_kayitlar():
    print("=== Problemli Kayitlari Duzeltme ===")
    print()
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Problemli kayıtları bul
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai WHERE ara_dinlenme LIKE '%,%'")
            rows = cursor.fetchall()
        
        if rows:
            print(f"{len(rows)} adet problemli kayit bulundu, duzeltiliyor...")
            
            for id, aralik, ara_dinlenme in rows:
                # Virgülü nokta ile değiştir
                duzeltilmis = ara_dinlenme.replace(',', '.')
                print(f"   ID {id}: '{ara_dinlenme}' -> '{duzeltilmis}'")
                
                # Güncelle
                cursor.execute(
                    "UPDATE mercis657_sabitmesai SET ara_dinlenme = ? WHERE id = ?",
                    (duzeltilmis, str(id))
                )
            
            print("Duzeltme tamamlandi!")
        else:
            print("Problemli kayit bulunamadi.")
            
    except Exception as e:
        print(f"HATA olustu: {e}")

if __name__ == "__main__":
    test_sabit_mesailer()
    print("=" * 50)
    test_problemli_kayitlar()
    print("=" * 50)
    duzelt_problemli_kayitlar()
    print("=" * 50)
    print("Duzeltme sonrasi test:")
    test_sabit_mesailer()