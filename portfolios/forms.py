from django import forms
from .models import Portfolio, PortfolioHolding, PeriodicContribution
from funds.models import Fund


class PortfolioForm(forms.ModelForm):
    """
    Form for creating and updating portfolios.
    """
    date_of_birth = forms.DateField(
        label='תאריך לידה',
        input_formats=['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d'],  # Accept dd/mm/yyyy, dd-mm-yyyy, ISO
        widget=forms.TextInput(attrs={
            'class': 'input flatpickr-date',
            'placeholder': 'dd/mm/yyyy',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Portfolio
        fields = ['name', 'owner_name', 'date_of_birth', 'gender', 'description', 'legal_id']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם התיק (יווצר אוטומטית לפי שם הבעלים)',
                'id': 'id_name'
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם מלא של בעל התיק',
                'id': 'id_owner_name'
            }),
            'gender': forms.Select(attrs={
                'class': 'input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'placeholder': 'תיאור התיק, מטרות והאסטרטגיה',
                'rows': 4
            }),
            'legal_id': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'תעודת זהות (נדרש לשיתוף עם סוכנים)',
                'maxlength': '20'
            }),
        }
        labels = {
            'name': 'שם התיק',
            'owner_name': 'שם בעל התיק',
            'gender': 'מגדר',
            'description': 'תיאור',
            'legal_id': 'תעודת זהות',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name field not required - it will be auto-generated
        if not self.instance.pk:  # Only for new portfolios
            self.fields['name'].required = False


class PortfolioHoldingForm(forms.ModelForm):
    """
    Form for adding and updating portfolio holdings.
    """
    fund = forms.ModelChoiceField(
        queryset=Fund.objects.all().order_by('name'),
        label='קרן',
        widget=forms.Select(attrs={
            'class': 'input'
        }),
        empty_label='בחר קרן...'
    )

    purchase_date = forms.DateField(
        label='תאריך רכישה',
        required=False,
        input_formats=['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d'],  # Accept dd/mm/yyyy, dd-mm-yyyy, ISO
        widget=forms.TextInput(attrs={
            'class': 'input flatpickr-date',
            'placeholder': 'dd/mm/yyyy',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = PortfolioHolding
        fields = ['fund', 'amount', 'purchase_date', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'סכום בש״ח',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'input',
                'placeholder': 'הערות (אופציונלי)',
                'rows': 3
            }),
        }
        labels = {
            'fund': 'קרן',
            'amount': 'סכום השקעה (₪)',
            'purchase_date': 'תאריך רכישה',
            'notes': 'הערות',
        }


class PeriodicContributionForm(forms.ModelForm):
    """
    Form for creating and updating periodic contribution plans.
    """
    start_date = forms.DateField(
        label='תאריך התחלה',
        input_formats=['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'input flatpickr-date',
            'placeholder': 'dd/mm/yyyy',
            'autocomplete': 'off'
        })
    )

    end_date = forms.DateField(
        label='תאריך סיום',
        required=False,
        input_formats=['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'input flatpickr-date',
            'placeholder': 'dd/mm/yyyy (אופציונלי)',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = PeriodicContribution
        fields = ['amount', 'interval', 'start_date', 'end_date', 'is_active', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'סכום בש״ח',
                'step': '0.01',
                'min': '0'
            }),
            'interval': forms.Select(attrs={
                'class': 'input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-primary-600 focus:ring-primary-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'input',
                'placeholder': 'הערות (אופציונלי)',
                'rows': 3
            }),
        }
        labels = {
            'amount': 'סכום תרומה תקופתית (₪)',
            'interval': 'תדירות',
            'start_date': 'תאריך התחלה',
            'end_date': 'תאריך סיום',
            'is_active': 'תכנית פעילה',
            'notes': 'הערות',
        }
