from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Ingrese un correo electrónico válido.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido. Ingrese su nombre.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Requerido. Ingrese su apellido.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso. Por favor, utilice otro.')
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
