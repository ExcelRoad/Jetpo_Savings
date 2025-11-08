from django import forms
from .models import Contact, AgentPreOrder, ContactRequest
from portfolios.models import Portfolio


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'message', 'agree_to_notifications']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'שם מלא'}),
            'phone': forms.TextInput(attrs={'class': 'input', 'placeholder': 'טלפון (אופציונלי)'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'אימייל'}),
            'message': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': 'ספר לנו על הצורך שלך...'}),
            'agree_to_notifications': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded', 'checked': True}),
        }
        labels = {
            'name': 'שם מלא',
            'phone': 'טלפון',
            'email': 'אימייל',
            'message': 'הודעה',
            'agree_to_notifications': 'אני מסכים/ה לקבל עדכונים מ-Jetpo',
        }


class AgentPreOrderForm(forms.ModelForm):
    class Meta:
        model = AgentPreOrder
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'שם פרטי'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'שם משפחה'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'input', 'placeholder': '050-1234567'}),
            'company': forms.TextInput(attrs={'class': 'input', 'placeholder': 'שם החברה שלך'}),
            'message': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': 'כמה לקוחות יש לך? מה התחום שלך? כל מידע נוסף...'}),
        }


class ContactRequestPortfolioSelectionForm(forms.Form):
    """
    Step 1: Select portfolios to include in the contact request.
    """
    portfolios = forms.ModelMultipleChoiceField(
        queryset=Portfolio.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-input'}),
        label='בחר תיקים לשיתוף',
        required=True,
        error_messages={
            'required': 'יש לבחור לפחות תיק אחד',
        }
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['portfolios'].queryset = Portfolio.objects.filter(user=user)


class ContactRequestLegalIDForm(forms.Form):
    """
    Step 2: Review and edit legal IDs for selected portfolios.
    Dynamically generates fields based on selected portfolios.
    """
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'input',
            'rows': 4,
            'placeholder': 'הודעה נוספת ליועץ (אופציונלי)'
        }),
        label='הודעה',
        required=False
    )

    def __init__(self, portfolios=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if portfolios:
            for portfolio in portfolios:
                field_name = f'legal_id_{portfolio.id}'
                self.fields[field_name] = forms.CharField(
                    max_length=20,
                    initial=portfolio.legal_id,
                    widget=forms.TextInput(attrs={
                        'class': 'input',
                        'placeholder': 'מספר זהות',
                        'dir': 'ltr'
                    }),
                    label=f'מספר זהות עבור {portfolio.name}',
                    required=True,
                    error_messages={
                        'required': 'יש למלא מספר זהות',
                    }
                )
                # Store portfolio reference for later use
                self.fields[field_name].portfolio = portfolio

    def clean(self):
        cleaned_data = super().clean()
        # Validate that all legal IDs are filled
        for field_name, value in cleaned_data.items():
            if field_name.startswith('legal_id_') and not value:
                raise forms.ValidationError('יש למלא את כל מספרי הזהות')
        return cleaned_data
