from django import forms


class RecipientsTableForm(forms.Form):
    contact_type_choices = (
        ('email', 'email'),
        ('phone', 'phone'),
        ('telegram', 'telegram'),
    )

    table_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'file-input'}))
    contact_type = forms.ChoiceField(choices=contact_type_choices, widget=forms.Select(attrs={'class': 'select'}))

