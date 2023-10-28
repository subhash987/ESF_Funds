from django.forms import ModelForm
from .models import Loan, Transaction, Profile, LoanRepayment
from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django.forms.widgets import Select


class CustomUserCreationForm(UserCreationForm): 
    username = forms.CharField( max_length=50)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
 
    class Meta: 
        model = User 
        fields = ['username', 'password1', 'password2']
        
    def create(self, validated_data):
        user = super().save()
        Profile.objects.create(user=user)
        return user
    

class LoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = '__all__'
        exclude = ['balance','remaining_balance']
        
        
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone', 'dob']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = forms.CharField(
            label='Username', 
            disabled=True, 
            initial=self.instance.user_id.username
        )

class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user_id','image']

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

class EditTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ('transaction_amount','payment_mode','payment_id')
        
    # def __init__(self, *args, **kwargs):
    #     super(EditTransactionForm, self).__init__(*args, **kwargs)
    #     self.fields['loan'].widget = Select(choices=[(loan.id, loan.user.username) for loan in self.fields['loan'].queryset])
        
class EditLoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].disabled = True

class LoanRepaymentForm(ModelForm):
    class Meta:
        model = LoanRepayment
        fields = '__all__'


class RepaymentForm(forms.Form):
    selected_month = forms.IntegerField()


class RepaymentForm(forms.Form):
    repayment_month = forms.ChoiceField(label='Repayment Month')
    amount = forms.DecimalField(label='Repayment Amount')
    repayment = forms.ChoiceField(choices=(), widget=forms.Select(attrs={'class': 'form-control'}))
