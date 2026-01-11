from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='TC Kimlik', max_length=100)
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)

class ScheduleForm(forms.Form):
    unit_id = forms.ChoiceField(label='Birim', choices=[], required=True)
    start_date = forms.DateField(label='Başlangıç Tarihi', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Bitiş Tarihi', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, authorized_units=None, **kwargs):
        super().__init__(*args, **kwargs)
        if authorized_units:
            self.fields['unit_id'].choices = [(unit['BirimID'], unit['BirimAdi']) for unit in authorized_units]
