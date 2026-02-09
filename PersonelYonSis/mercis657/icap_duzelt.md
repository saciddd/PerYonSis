## Open your terminal.
- Activate your virtual environment:
```powershell
..\SqlDjangoVenv\Scripts\activate
```
- Start the Django shell:
```powershell
python manage.py shell
```
- Run the correction script (replace 'YYYY-MM-DD' with your desired start date):
```python
from mercis657.utils import duzelt_icap_kayitlari
duzelt_icap_kayitlari('2026-01-01')
```