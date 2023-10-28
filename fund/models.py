from django.db import models
from django.contrib.auth.models import User


class ContributorInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateField(auto_now=True)
    updated_date = models.DateField(auto_now_add=True)
    last_contributed_date = models.DateField(null=True, blank=True)
    total_contributed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


class ContributionHistory(models.Model):
    contributor = models.ForeignKey(ContributorInfo, on_delete=models.CASCADE)
    contribution_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.contributor.user.username} - {self.contribution_date}"
    


class FundsAllocated(models.Model):
    accumulated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Accumulated Fund: {self.accumulated_amount}"
    
    
    @classmethod
    def add_contribution(cls, amount):
        funds_allocated = cls.objects.first()
        if funds_allocated:
            funds_allocated.accumulated_amount += amount
            funds_allocated.remaining_fund += amount
            funds_allocated.save()

