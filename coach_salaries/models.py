from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from coach.models import Coach
from manager.models import Manager


class CoachContract(models.Model):
    coach = models.OneToOneField('coach.Coach', on_delete=models.PROTECT)
    manager = models.ForeignKey('manager.Manager', on_delete=models.PROTECT)
    price = models.BigIntegerField()
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_(" Description"),
        help_text=_("Detailed description of coach's contarct")
    )
    expiration_date = models.DateField(null=True, blank=True)
    start_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f'{self.coach} - {self.manager}'
    class Meta:
        verbose_name = 'Coach Contract'
        verbose_name_plural = 'Coach Contracts'
        ordering = ['-expiration_date']


class SalaryRecord(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("pending", "Pending"),
    ]

    coach_contract = models.ForeignKey('CoachContract', on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unpaid")
    month = models.DateField()
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_(" Description"),
        help_text=_("Detailed description of coach's salary")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.coach_contract.coach} - {self.month} - {self.status}'


class SalaryPayment(models.Model):
    salary_record = models.OneToOneField(SalaryRecord, on_delete=models.CASCADE)
    paid_at = models.DateTimeField(auto_now_add=True)
    amount = models.BigIntegerField()
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_(" Description"),
        help_text=_("Detailed description of coach's salary payment")
    )

    def __str__(self):
        return f'{self.salary_record} - {self.amount} paid at {self.paid_at}'
