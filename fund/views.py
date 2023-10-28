from django.shortcuts import render, HttpResponse
from .forms import ContributorForm, ContributorCreateForm, ContributionForm
from .models import ContributorInfo, FundsAllocated, ContributionHistory
from django.db.models import Sum
from django.contrib import messages
from django.db.models import F

from django.shortcuts import render, redirect, get_object_or_404
from .models import ContributorInfo



def contributor_list(request):
    contributors = ContributorInfo.objects.all()
    funds = FundsAllocated.objects.all()
    context = {'contributors': contributors, 'funds':funds}
    return render(request, 'contributor_details.html', context)


def make_contribution(request, contributor_id):
    if not request.user.is_superuser:
        return redirect('fund:contributor_list') 
    
    contributor = ContributorInfo.objects.get(id=contributor_id)

    if request.method == 'POST':
        form = ContributorForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            contributor.amount += amount
            contributor.total_contributed_amount += amount
            ContributionHistory.objects.create(contributor=contributor, amount=amount)

            contributor.save()

            funds_allocated = FundsAllocated.objects.first()
            if funds_allocated:
                funds_allocated.accumulated_amount += amount
                funds_allocated.remaining_fund += amount
                funds_allocated.save()
            else:
                FundsAllocated.objects.create(accumulated_amount=amount)

            return redirect('fund:contributor_list')
    else:
        form = ContributorForm()

    context = {'contributor': contributor, 'form': form}
    return render(request, 'make_contribution.html', context)


def create_contributor(request):
    if not request.user.is_superuser:
        return redirect('fund:contributor_list')
    
    if request.method == 'POST':
        form = ContributorCreateForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            amount = form.cleaned_data['amount']

            contributor = ContributorInfo.objects.create(user=user, amount=amount, total_contributed_amount=amount)
            ContributionHistory.objects.create(contributor=contributor, amount=amount)

            funds_allocated = FundsAllocated.objects.first()
            if funds_allocated:
                funds_allocated.accumulated_amount += amount
                funds_allocated.remaining_fund += amount
                funds_allocated.save()
            else:
                FundsAllocated.objects.create(accumulated_amount=amount)

            return redirect('fund:contributor_list')
    else:
        form = ContributorCreateForm()

    context = {'form': form}
    return render(request, 'create_contributor.html', context)


def contribution_history(request, contributor_id):
    contributor = ContributorInfo.objects.get(id=contributor_id)
    history = ContributionHistory.objects.filter(contributor=contributor).order_by('-contribution_date')
    context = {'contributor': contributor, 'history': history}
    return render(request, 'contribution_history.html', context)


def edit_contribution(request, contribution_id):
    
    contribution = get_object_or_404(ContributionHistory, id=contribution_id)

    if request.method == 'POST':
        form = ContributionForm(request.POST, instance=contribution)
        if form.is_valid():
            old_amount = contribution.amount  # Store the old amount
            form.save()

            # Update the main contributor's total
            contributor = contribution.contributor
            contributor.total_contributed_amount = ContributionHistory.objects.filter(contributor=contributor).aggregate(Sum('amount'))['amount__sum']
            contributor.save()

            # Update the accumulated amount in FundsAllocated
            funds_allocated, _ = FundsAllocated.objects.get_or_create(pk=1)
            funds_allocated.accumulated_amount = ContributorInfo.objects.aggregate(Sum('total_contributed_amount'))['total_contributed_amount__sum']
            funds_allocated.remaining_fund = ContributorInfo.objects.aggregate(Sum('total_contributed_amount'))['total_contributed_amount__sum']
            funds_allocated.save()

            return redirect('fund:contributor_list')
    else:
        form = ContributionForm(instance=contribution)

    context = {'form': form, 'contribution': contribution}
    return render(request, 'edit_contribution.html', context)


def contributor_transactions(request):
    transactions = ContributionHistory.objects.all()
    return render(request, 'contributor_transactions.html', {'transactions': transactions})


# def bonus_transactions(request):
#     transactions = BonusTransaction.objects.all()
#     return render(request, 'bonus_transactions.html', {'transactions': transactions})

# def give_bonus(request):
#     if request.method == 'POST':
#         form = GiveBonusesForm(request.POST)
#         if form.is_valid():
#             bonus_amount = form.cleaned_data['bonus_amount']
#             selected_contributors = form.cleaned_data['selected_contributors']

#             if not selected_contributors:
#                 messages.error(request, "Please select at least one contributor.")
#             else:
#                 # Check if all selected contributors have total_contributed_amount >= 0
#                 if all(contributor.total_contributed_amount >= 0 for contributor in selected_contributors):
#                     # Check if bonus amount is valid (greater than 0)
#                     if bonus_amount > 0:
#                         # Calculate the total bonus amount to be given
#                         total_bonus_amount = len(selected_contributors) * bonus_amount

#                         # Check if there are sufficient funds
#                         funds_allocated = FundsAllocated.objects.first()
#                         if funds_allocated and funds_allocated.remaining_fund >= total_bonus_amount:
#                             for contributor in selected_contributors:
#                                 # Check if the bonus amount is not greater than total_contributed_amount
#                                 if contributor.total_contributed_amount >= bonus_amount:
#                                     contributor.total_contributed_amount -= bonus_amount
#                                     contributor.save()
#                                     BonusTransaction.objects.create(contributor=contributor, bonus_amount=bonus_amount)
#                                 else:
#                                     messages.error(request, f"{contributor.user.username}'s total_contributed_amount is less than the bonus amount. Bonus cannot be given to this contributor.")
#                                     return redirect('fund:contributor_list')

#                             # Update the accumulated and remaining funds
#                             funds_allocated.accumulated_amount -= total_bonus_amount
#                             funds_allocated.remaining_fund -= total_bonus_amount
#                             funds_allocated.save()

#                             for contributor in selected_contributors:
#                                 BonusTransaction.objects.create(contributor=contributor, bonus_amount=bonus_amount)
#                             messages.success(request, f"Successfully gave {total_bonus_amount} as bonus to selected contributors.")
#                         else:
#                             messages.error(request, "Insufficient funds. Bonus cannot be given.")
#                     else:
#                         messages.error(request, "Invalid bonus amount. Bonus amount should be greater than 0.")
#                 else:
#                     messages.error(request, "Some selected contributors have total_contributed_amount less than 0. Bonus cannot be given to them.")
            
#             return redirect('fund:contributor_list')
#     else:
#         form = GiveBonusesForm()

#     context = {'form': form}
#     return render(request, 'give_bonus.html', context)



def delete_contributor(request, contributor_id):
    if not request.user.is_superuser:
        return HttpResponse("You are not allowed to delete contributors.")

    contributor = ContributorInfo.objects.get(id=contributor_id)

    if request.method == "POST":
        # Get the contribution amount of the contributor being deleted
        contribution_amount = contributor.total_contributed_amount

        # Delete the contributor
        contributor.delete()

        # Update the accumulated amount in FundsAllocated
        funds_allocated, _ = FundsAllocated.objects.get_or_create(pk=1)
        funds_allocated.accumulated_amount -= contribution_amount
        funds_allocated.remaining_fund -= contribution_amount
        funds_allocated.save()

        messages.success(request, "Contributor deleted successfully.")
        return redirect("fund:contributor_list")

    context = {'obj': contributor.user.username}
    return render(request, "delete.html", context)


def calculate_accumulated_amount():
    contributors = ContributorInfo.objects.all()
    total_amount = sum(contributor.total_contributed_amount for contributor in contributors)
    
    print("Total Amount:", total_amount)  # Print the total amount
    
    funds_allocated = FundsAllocated.objects.first()
    if funds_allocated:
        funds_allocated.accumulated_amount = total_amount
        funds_allocated.remaining_fund = total_amount
        funds_allocated.save()
    else:
        FundsAllocated.objects.create(accumulated_amount=total_amount, remaining_fund=total_amount)



def funds_allocated_view(request):
    funds = FundsAllocated.objects.all()
    return render(request, 'funds_page.html', {'funds': funds})



