from django.shortcuts import render, HttpResponse
from .forms import CustomUserCreationForm, TransactionForm, EditTransactionForm, LoanForm, EditLoanForm, ProfileForm, RepaymentForm
from django.db import IntegrityError
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Profile, Loan, Transaction, LoanRepayment, LoanUsertransactions
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from fund.models import FundsAllocated, ContributorInfo
from django.db.models import Sum
# from datetime import date
from datetime import date, timedelta

from django import forms
# from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
from django.utils import timezone
import calendar
import datetime
from django.utils import timezone
from itertools import cycle
from django.http import JsonResponse

# from dateutil.relativedelta import relativedelta

from django.forms import formset_factory


def registerUser(request):

    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                profile = Profile.objects.create(user_id=user)
                login(request, user)
                return redirect('home')
            except IntegrityError:
                messages.error(request,'Username already exists')
        else:
            messages.error(request,'An error occurred during registration')
    return render(request, 'login_register.html', {'form': form})


@login_required
def create_loan(request):
    loan_limit = 10000

    if not request.user.is_superuser:
        messages.error(request, "Only admin users can create loans.")
        return redirect('loans')

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            start_month = form.cleaned_data['start_month']
            if start_month is None:
                start_month = date.today()
            
            existing_loan = Loan.objects.filter(user=selected_user, status__in=['active', 'pending']).first()
        
            contributor_info = ContributorInfo.objects.filter(user=selected_user).first()

            funds_allocated = FundsAllocated.objects.first()

            if not contributor_info:
                messages.error(request, "You must be a contributor to apply for a loan.")
                return redirect('create-loan')
            
            if existing_loan:
                messages.error(request, "You have an active loan. Only one loan at a time is allowed.")
                return redirect('create-loan')

            amount = loan_limit
            if amount > funds_allocated.remaining_fund:
                messages.error(request, "Not Enough Funds!")
                return redirect('create-loan')
            
            interest_rate = 1
            term = 12
            balance = 0
            remaining_balance = amount + Decimal(amount) * Decimal('0.01')
            status = 'active'
            
            loan = Loan.objects.create(user=selected_user, amount=amount, interest_rate=interest_rate, term=term, balance=balance, remaining_balance=remaining_balance, status=status)
            
            repayment_amounts = calculate_repayment_amounts(amount, term)
            create_loan_repayments(loan, repayment_amounts, start_month)

            Transaction.objects.create(loan=loan, transaction_type='debit', transaction_amount=amount, payment_mode='UPI', payment_id='')

            funds_allocated.remaining_fund -= amount
            funds_allocated.save()

            messages.success(request, "Loan created successfully.")
            return redirect('loan_success', pk=loan.pk)
    else:
        form = LoanForm()
    
    context = {
        'form': form
    }
    return render(request, 'create-loan.html', context)


def calculate_repayment_amounts(amount, term):
    repayment_amounts = []
    repayment_amount = (amount + amount * Decimal('0.01')) // term
    remaining_balance = amount + amount * Decimal('0.01')

    for i in range(term - 1):
        rounded_repayment_amount = repayment_amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        repayment_amounts.append(rounded_repayment_amount)
        remaining_balance -= rounded_repayment_amount

    last_repayment_amount = remaining_balance
    repayment_amounts.append(last_repayment_amount)

    return repayment_amounts


def my_view(request):
    today = date.today()
    context = {
        'today': today,
    }
    return render(request, 'my_template.html', context)



def create_loan_repayments(loan, repayment_amounts,start_month):
    start_date = start_month.replace(day=1)  # Use the specified start month

    current_date = increment_month(start_date)  # Move to the next month

    for repayment_amount in repayment_amounts:
        month_name = current_date.strftime("%B")  # Get the month name
        repayment = LoanRepayment.objects.create(
            loan=loan,
            payment_amount=repayment_amount,
            payment_date=current_date,
            month=month_name  # Assign the month name to the 'month' field
        )

        current_date = increment_month(current_date)
                
def increment_month(date):
    year = date.year + (date.month // 12)
    month = (date.month % 12) + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return date.replace(year=year, month=month, day=day)


def loginUser(request):
    page ='login'
    if request.user.is_authenticated:
         return redirect('home')
    if request.method =="POST":
         username = request.POST.get('username').lower()
         password = request.POST.get('password')
         try:
             user = User.objects.get(username=username)         
         except:
             messages.error(request, "User does not exist!")
        
         user = authenticate(request, username=username, password=password)
        
         if user is not None:
             login(request, user)
             return redirect('home')
         else:
             messages.error(request,"Username or Password is incorrect!")
    context = { 'page': page }
    return render(request, "login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('loginpage')

@login_required(login_url="loginpage")
def home(request):
     loans = Loan.objects.all()

    # Calculate total loans given
     funds = FundsAllocated.objects.get()
     accumulated_amount = funds.accumulated_amount
     total_loan_amount = sum(loan.amount for loan in loans)

    # Calculate total interest earned
     total_interest_earned = sum((loan.amount)/100 for loan in loans)
    #  total_interest_earned = accumulated_amount - sum((loan.amount) for loan in loans) + funds.remaining_fund

    # Pass the data to the template

     if request.user.is_superuser:
         loan = Loan.objects.all()[:10]
         transaction = Transaction.objects.all()[:10]
     else:
         loan = Loan.objects.filter(user_id=request.user)[:3]
         transaction = Transaction.objects.filter(loan__user=request.user)[:3]
    
     context = {
         'loan': loan,
         'transaction': transaction,
         'accumulated_amount': accumulated_amount,
         'total_loan_amount': total_loan_amount,
         'total_interest_earned': total_interest_earned,
     }
     return render(request,'home.html', context)
 

@login_required(login_url="loginpage")
def loans(request):
     if request.user.is_superuser:
         loan = Loan.objects.all()
         funds = FundsAllocated.objects.get()
         remaining_amount = funds.remaining_fund
         total_loan_amount = sum(x.remaining_balance for x in loan)
     else:
         loan = Loan.objects.filter(user_id=request.user)
    
     context = {
         'loan': loan,
         'remaining_amount': remaining_amount,
         'total_loan_amount': total_loan_amount,
     }
     return render(request, 'loans.html', context)
 

@login_required(login_url="loginpage")
def loan_details(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    repayments = LoanRepayment.objects.filter(loan=loan)

    # Get a list of paid months
    paid_months = [repayment.month for repayment in repayments if repayment.is_paid]

    context = {
        'loan': loan,
        'repayments': repayments,
        'paid_months': paid_months,
    }
    return render(request, 'loan_details.html', context)



@login_required(login_url="loginpage")
def updateLoan(request,pk):
    loan = get_object_or_404(Loan, pk=pk)
    # transaction = loan.transaction_set.filter(transaction_type = 'repayment')
    loan_transaction = loan.transaction_set.filter(transaction_type="Debit").first()
    repayment_transaction = loan.transaction_set.filter(transaction_type="Repayment").first()

    if loan.status == 'paid':
        disabled = True
    else:
        disabled = False
    
   
    if request.method == 'POST':
        form = EditLoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            if loan.remaining_balance==0:
                loan.status = "paid"
            elif loan.status == "defaulted":
                loan.status = "default"
            else:
                loan.status = "active"
                loan.remaining_balance = loan.amount
                loan.interest_amount = (loan.amount * loan.interest_rate * loan.term)/100
                loan.main_balance = loan.amount  + loan.interest_amount
                loan.remaining_balance = loan.main_balance - loan.balance

            loan.save()

            if loan_transaction:
                loan_transaction.transaction_amount = loan.amount
                loan_transaction.transaction_type = "Debit"
                loan_transaction.save()
            else:
                Transaction.objects.create(loan=loan, transaction_type = "Debit", transaction_amount = loan.amount)
            return redirect("loans")
    else:
        form = EditLoanForm(instance=loan)
        if loan.status == "defaulted":
            form.fields['status'].initial = "default"
    
    context = {'form': form,
               'disabled': disabled,
               'loan': loan}
    return render(request, 'edit-loan.html', context)


@login_required(login_url="loginpage")
def deleteLoan(request,pk):
    loan = Loan.objects.get(pk=pk)
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    if request.method == "POST":
        if loan.balance > 0:
            messages.error(request,"Cannot delete a loan whose 1 or more replayments is there!")
            return redirect("loans")
        else:
            loan_amount = loan.amount

            loan.delete()

            funds_allocated = FundsAllocated.objects.first()  # Assuming there's only one FundsAllocated object
            if funds_allocated:
                funds_allocated.remaining_fund += loan_amount
                funds_allocated.save()

            return redirect("loans")
    return render(request, "delete.html", {'obj':loan})



@login_required(login_url="loginpage")
def transactions(request):
    users = User.objects.all()
    transaction_type_filter = request.GET.get('transaction_type_filter')
    
    transaction_types = ['credit', 'Debit', 'defaulted','repayment']

    
    if request.user.is_superuser:
        transactions = Transaction.objects.all()
        
        user_filter = request.GET.get('user_filter')
        if user_filter:
            transactions = transactions.filter(loan__user__username=user_filter)
    else:
        transactions = Transaction.objects.filter(loan__user_id=request.user)
    
    if transaction_type_filter:
        transactions = transactions.filter(transaction_type=transaction_type_filter)
        
    context = {
        'transactions': transactions,
        'transaction_type_filter': transaction_type_filter,
        'transaction_types': transaction_types,
        'user_filter': user_filter if request.user.is_superuser else None,
        'users': users,
    }
    
    return render(request, 'transactions.html', context)


@login_required(login_url="loginpage")
def createTransaction(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    form = TransactionForm()

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transactions')
    context = {'form': form}
    return render(request, 'create-transaction.html', context)


@login_required(login_url="loginpage")
def updateTransaction(request,pk):
    transaction = Transaction.objects.get(id=pk)
    form = EditTransactionForm(instance=transaction)
    
    
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    
    if request.method == 'POST':
        form = EditTransactionForm(request.POST, instance=transaction)
        
        if form.is_valid():
            form.save()
            return redirect('transactions')
    else:
        loan_user = transaction.loan.user.username
        context = {'form': form,
               'transaction':transaction,
               'loan_user': loan_user
               }
    return render(request, 'edit-transaction.html', context)

@login_required(login_url="loginpage")
def deleteTransaction(request,pk):
    transaction = Transaction.objects.get(id=pk)
    
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    if request.method == "POST":
        transaction.delete()
        return redirect("transactions")
    return render(request, "delete.html", {'obj': transaction})



@login_required(login_url="loginpage")
def profiles(request):
    if request.user.is_superuser:
        profile = Profile.objects.all()
    else:
        profile = Profile.objects.filter(user_id=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request,'profile.html', context)

@login_required(login_url="loginpage")
def admin_profile(request):
    
    profile = Profile.objects.filter(user_id=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request,'admin_profile.html', context)



@login_required(login_url="loginpage")
def createProfile(request):
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    form = ProfileForm()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile')
    context = {'form': form}
    return render(request, 'create_profile.html', context)

@login_required(login_url="loginpage")
def updateProfile(request, pk):
    # profile = request.user.profile
    profile = Profile.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'edit-user.html', context)



@login_required(login_url="loginpage")
def deleteProfile(request, pk):
    profile = Profile.objects.get(profile_id=pk)
    if not request.user.is_superuser:
        return HttpResponse("you are not allowed!")
    if request.method == "POST":
        profile.delete()
        return redirect("profile")
    return render(request, "delete.html", {'obj': profile})



@login_required(login_url="loginpage")
def repay_loan(request, loan_id):
    if not request.user.is_superuser:
        messages.error(request, "Only admin users can repay loans.")
        return redirect('loans')

    loan = get_object_or_404(Loan, id=loan_id)

    if loan.status != 'active':
        messages.error(request, "This loan is not active.")
        return redirect('loans')

    repayments = LoanRepayment.objects.filter(loan=loan, is_paid=False)
    repayment_months = []
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    next_year = current_year + 1
    today = date.today()
    for i in range(1, 13):
        month_number = (current_month + i) % 12
        if month_number == 0:
            month_number = 12
        month_name = calendar.month_name[month_number]
        year = current_year if month_number >= current_month else next_year
        repayment_months.append((month_number, month_name, year))

    if request.method == 'POST':
        selected_repayments = request.POST.getlist('repayments')
        for repayment_id in selected_repayments:
            try:
                repayment = LoanRepayment.objects.get(id=repayment_id)
                # Perform the necessary actions to mark the repayment as paid, update balances, etc.
                repayment.is_paid = True
                repayment.save()

                loan.remaining_balance -= repayment.payment_amount
                loan.balance += repayment.payment_amount
                if loan.remaining_balance == 0:
                    loan.status = 'paid'
                loan.save()
                
                funds_allocated = FundsAllocated.objects.first()  # Assuming there's only one FundsAllocated object
                if funds_allocated:
                    funds_allocated.remaining_fund += repayment.payment_amount
                    funds_allocated.save()

                transaction = Transaction.objects.create(
                    loan=loan,
                    transaction_type='repayment',
                    transaction_amount=repayment.payment_amount,
                    payment_mode='upi',
                    payment_id=''
                )
            except LoanRepayment.DoesNotExist:
                messages.error(request, f"Invalid repayment ID: {repayment_id}")

        messages.success(request, "Loan repayments processed successfully.")
        return redirect('loans')
          # Get the current date


    context = {
        'repayments': repayments,
        'repayment_months': repayment_months,
        'loan': loan,
        'today':today,
    }
    return render(request, 'repay_loan.html', context)



def transaction_filter_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        transaction_type = request.POST.get('transaction_type')
        transactions = Transaction.objects.all()
        if user_id:
            transactions = transactions.filter(loan__user__id=user_id)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        return render(request, 'transaction_filter.html', {'transactions': transactions})
    return render(request, 'transaction_filter.html')


def view_loan_transactions(request, loan_id):
    loan = Loan.objects.get(id=loan_id)
    repayments = loan.repayments.all()
    transactions = []
    for repayment in repayments:
        transactions += list(repayment.transactions.all())
    context = {
        'loan': loan,
        'transactions': transactions,
    }
    return render(request, 'loan_transactions.html', context)


def about(request):
    return render(request,'aboutus.html')


def contact(request):
    return render(request,'contactus.html')


def funds_page(request):
    funds = FundsAllocated.objects.all()
    contributors = ContributorInfo.objects.all()
    # contributor_history = ContributionHistory.objects.all()
    context = {'contributors': contributors, 'funds':funds}
    return render(request, 'funds_page.html', context)

def mark_repayment_paid(request, loan_id, repayment_id):
    # Retrieve the loan object
    loan = get_object_or_404(Loan, id=loan_id)

    # Retrieve the repayment object
    repayment = get_object_or_404(LoanRepayment, id=repayment_id, loan=loan)

    if repayment.is_paid:
        # Repayment is already marked as paid, handle accordingly (e.g., display an error message)
        return render(request, 'repayment_already_paid.html', {'loan': loan, 'repayment': repayment})

    # Update the repayment status to paid
    repayment.is_paid = True
    repayment.save()

    # Update the loan's remaining balance
    payment_amount = repayment.payment_amount
    loan.remaining_balance -= payment_amount
    loan.balance += payment_amount
    loan.save()

    # Create a transaction record
    transaction = Transaction.objects.create(
        loan=loan,
        transaction_type='repayment',
        transaction_amount=payment_amount,
        payment_mode='upi',
        payment_id=''
    )

    # Redirect to the loan details page or any other desired page
    return redirect('transactions')



def loan_success(request,pk):
    error_messages = messages.get_messages(request)
    loan = Loan.objects.get(pk=pk)
    return render(request, "loan_sucess.html", {'obj':loan})

