from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProfileForm(forms.Form):
	FullName = forms.CharField(label='Ad Soyad', max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	Email = forms.EmailField(label='E-posta', required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
	Phone = forms.CharField(label='Telefon', max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5xxxxxxxxx'}))
	Organisation = forms.CharField(label='Kurum/Organizasyon', max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

	def clean_Phone(self):
		phone = self.cleaned_data.get('Phone')
		if phone:
			import re
			if not re.match(r'^5\d{9}$', phone):
				raise forms.ValidationError('Telefon numarası 5xxxxxxxxx formatında olmalıdır.')
		return phone

class PasswordChangeForm(forms.Form):
	old_password = forms.CharField(label='Mevcut Şifre', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	new_password = forms.CharField(label='Yeni Şifre', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	confirm_password = forms.CharField(label='Yeni Şifre (Tekrar)', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

	def clean(self):
		cleaned = super().clean()
		new_password = cleaned.get('new_password')
		confirm_password = cleaned.get('confirm_password')
		if new_password and confirm_password and new_password != confirm_password:
			raise forms.ValidationError('Yeni şifre ile tekrarı eşleşmiyor.')
		return cleaned
