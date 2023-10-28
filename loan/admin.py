from django.contrib import admin
from .models import Profile, Loan, Transaction, LoanRepayment, LoanUsertransactions
# Register your models here.

admin.site.register(Profile)
admin.site.register(LoanRepayment)
admin.site.register(Loan)
admin.site.register(Transaction)
admin.site.register(LoanUsertransactions)