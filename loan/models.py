from django.db import models
from django.db import models
from django.contrib.auth.models import User
    
class Loan(models.Model):
    
    LOAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('defaulted', 'Defaulted'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2,default=1)
    term = models.IntegerField(default=12)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_loan = models.DateTimeField(auto_now=True)
    updated_loan = models.DateTimeField(auto_now_add=True)
    start_month = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='active')
    
    class Meta:
        ordering = ['-updated_loan','-created_loan']
    
    def __str__(self):
        return f"{self.user}"    
    
class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE,related_name='repayments')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    message = models.CharField(max_length=200, blank=True)
    month = models.CharField(max_length=20, blank=True)
   
class Transaction(models.Model):
        TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
        PAYMENT_MODE_CHOICES = [
        ('UPI', 'UPI'),
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Net Banking', 'Net Banking'),
    ]
        loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
        transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPE_CHOICES)
        transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
        payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES,default="UPI")
        payment_id = models.CharField(max_length=50, default="")
        transaction_time = models.DateTimeField(auto_now=True)

        class Meta:
            ordering = ['-transaction_time']
    
        def __str__(self):
            return f"{self.loan.user}"
        


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    email = models.EmailField(default= "")
    phone = models.CharField(max_length=20)
    dob = models.DateField(default='2000-01-01')
    created = models.DateField(auto_now=True)
    updated = models.DateField(auto_now_add=True)
        
    def __str__(self):
        return f"{self.user_id}"
    

class LoanUsertransactions(models.Model):
    repayment = models.ForeignKey(LoanRepayment, on_delete=models.CASCADE, related_name='transactions')
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_transactions', null=True , blank=True)
    transaction_type = models.CharField(max_length=255)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255)
