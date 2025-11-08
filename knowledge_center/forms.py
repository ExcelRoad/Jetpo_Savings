from django import forms
from .models import ArticleSubmission, Category, Tag
from ckeditor.widgets import CKEditorWidget


class ArticleSubmissionForm(forms.ModelForm):
    """Form for submitting articles for review"""

    # Override tags to use checkboxes
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='תגיות'
    )

    class Meta:
        model = ArticleSubmission
        fields = [
            'submitter_full_name',
            'expertise_type',
            'agent_diploma_id',
            'advisor_diploma_id',
            'academic_institution',
            'academic_degree',
            'company_name',
            'other_expertise',
            'title',
            'english_title',
            'excerpt',
            'content',
            'category',
            'tags',
        ]
        widgets = {
            'submitter_full_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם מלא',
                'readonly': 'readonly',
            }),
            'expertise_type': forms.Select(attrs={
                'class': 'input',
            }),
            'agent_diploma_id': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'מספר רישיון סוכן',
            }),
            'advisor_diploma_id': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'מספר רישיון יועץ',
            }),
            'academic_institution': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם מוסד אקדמי',
            }),
            'academic_degree': forms.Select(attrs={
                'class': 'input',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'שם החברה',
            }),
            'other_expertise': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'פרט את תחום המומחיות שלך',
            }),
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'כותרת המאמר',
            }),
            'english_title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Article Title (English)',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'תקציר קצר (עד 2 שורות)',
                'maxlength': 300,
            }),
            'category': forms.Select(attrs={
                'class': 'input',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pre-fill user's full name
        if user:
            self.fields['submitter_full_name'].initial = user.get_full_name() or user.email

        # Make expertise-specific fields not required initially
        self.fields['agent_diploma_id'].required = False
        self.fields['advisor_diploma_id'].required = False
        self.fields['academic_institution'].required = False
        self.fields['academic_degree'].required = False
        self.fields['company_name'].required = False
        self.fields['other_expertise'].required = False

    def clean(self):
        cleaned_data = super().clean()
        expertise_type = cleaned_data.get('expertise_type')

        # Validate expertise-specific fields
        if expertise_type == 'AGENT':
            if not cleaned_data.get('agent_diploma_id'):
                self.add_error('agent_diploma_id', 'שדה זה נדרש עבור סוכן פיננסי')

        elif expertise_type == 'ADVISOR':
            if not cleaned_data.get('advisor_diploma_id'):
                self.add_error('advisor_diploma_id', 'שדה זה נדרש עבור יועץ פיננסי')

        elif expertise_type == 'ACADEMIC':
            if not cleaned_data.get('academic_institution'):
                self.add_error('academic_institution', 'שדה זה נדרש עבור אקדמאי')
            if not cleaned_data.get('academic_degree'):
                self.add_error('academic_degree', 'שדה זה נדרש עבור אקדמאי')

        elif expertise_type in ['ANALYST', 'INVESTOR']:
            if not cleaned_data.get('company_name'):
                self.add_error('company_name', 'שדה זה נדרש עבור אנליסט פיננסי / משקיע מנוסה')

        elif expertise_type == 'OTHER':
            if not cleaned_data.get('other_expertise'):
                self.add_error('other_expertise', 'אנא פרט את תחום המומחיות שלך')

        return cleaned_data
