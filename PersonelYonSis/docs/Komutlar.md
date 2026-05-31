### Eğer DB'ye manuel data eklenirse, id çakışmasını engellemek ve sekans hesaplatmak için:
python manage.py sync_sequences mercis657

### RFC dosyalarından sonra:
dosyasını oku ve implemente et, konsol komutu çalıştırman gerekirse ilk aşağıdaki komutu çalıştırıp virtual environmenti aktive et:
"..\SqlDjangoVenv\Scripts\activate"

### 4. Güncellenen RFC dosyalarını uygulamak için:
python manage.py makemigrations mercis657
python manage.py migrate

### 5. Sunucuyu çalıştırmak için:
python manage.py runserver