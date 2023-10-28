from django import forms
from .models import ContributorInfo, ContributionHistory
from django.contrib.auth.models import User

class ContributionForm(forms.ModelForm):
    class Meta:
        model = ContributionHistory
        fields = ['amount']

class ContributorCreateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class ContributorForm(forms.ModelForm):
    class Meta:
        model = ContributorInfo
        fields = ['amount']
