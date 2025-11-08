from django import forms
from django.contrib.auth import password_validation
from allauth.account.forms import SignupForm
from .models import User


class CustomSignupForm(SignupForm):
    """
    Custom signup form that adds first_name and last_name fields.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'input'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'input'
        })
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם פרטי'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם משפחה'
            }),
        }
        labels = {
            'first_name': 'שם פרטי',
            'last_name': 'שם משפחה',
            'profile_picture': 'תמונת פרופיל',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make profile_picture optional in the form
        self.fields['profile_picture'].required = False


class EmailUpdateForm(forms.ModelForm):
    """
    Form for updating user email.
    """
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'email@example.com'
            }),
        }
        labels = {
            'email': 'כתובת אימייל',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('כתובת האימייל הזו כבר בשימוש.')
        return email


class PasswordChangeForm(forms.Form):
    """
    Form for changing user password.
    """
    old_password = forms.CharField(
        label='סיסמה נוכחית',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': '••••••••'
        })
    )
    new_password1 = forms.CharField(
        label='סיסמה חדשה',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': '••••••••'
        }),
        help_text=password_validation.password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label='אימות סיסמה חדשה',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': '••••••••'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('הסיסמה הנוכחית שגויה.')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('הסיסמאות אינן תואמות.')
        if password1:
            password_validation.validate_password(password1, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
