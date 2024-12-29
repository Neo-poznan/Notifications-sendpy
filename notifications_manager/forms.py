from django import forms


class RecipientsTableForm(forms.Form):
    table_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'file-input'}))

