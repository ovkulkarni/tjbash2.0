from django import forms
from .models import Announcement, Quote


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.widgets.Textarea(attrs={'class': 'materialize-textarea'})


class QuoteForm(forms.ModelForm):
    tags = forms.CharField(required=False)

    class Meta:
        model = Quote
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(QuoteForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.widgets.Textarea(attrs={'class': 'materialize-textarea'})
