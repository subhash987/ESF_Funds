from django.contrib import admin
from .models import ContributorInfo, FundsAllocated, ContributionHistory

admin.site.register(ContributorInfo)
admin.site.register(FundsAllocated)
admin.site.register(ContributionHistory)