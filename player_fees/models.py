from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from player.models import Player
from team.models import Team

User = get_user_model()

class PlayerInvoice(models.Model):
    """Represents an invoice issued to a player for football school fees."""

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_OVERDUE = "overdue"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_OVERDUE, "Overdue"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    player = models.ForeignKey('player.Player', on_delete=models.CASCADE, related_name='invoices', verbose_name="Player")
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE, related_name='invoices', verbose_name="Team")
    amount = models.BigIntegerField(verbose_name="Total Amount", help_text="Total invoice amount in Toman")
    issued_date = models.DateField(default=timezone.localdate, verbose_name="Issued Date")
    due_date = models.DateField(verbose_name="Due Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="Status")
    description = models.TextField(blank=True, null=True, verbose_name="Description", help_text="Additional notes about the invoice")

    class Meta:
        ordering = ['-issued_date']
        verbose_name = "Player Invoice"
        verbose_name_plural = "Player Invoices"
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['player', 'status']),
            models.Index(fields=['issued_date']),
        ]

    def __str__(self):
        return f"Invoice #{self.pk} - {self.player} - {self.amount:,} Toman"

    def clean(self):
        """Data validation."""
        if self.due_date and self.issued_date and self.due_date < self.issued_date:
            raise ValidationError("Due date cannot be before the issue date.")
        if self.amount is not None and self.amount < 0:
            raise ValidationError("Invoice amount cannot be negative.")

    @property
    def total_paid(self):
        """Total amount paid."""
        return self.payments.aggregate(
            total=models.Sum('amount', default=0)
        )['total'] or 0

    @property
    def outstanding_amount(self):
        """How much is left to be paid."""
        return max(self.amount - self.total_paid, 0)

    def update_status(self):
        """Update invoice status based on payments and due date."""
        if self.total_paid >= self.amount:
            self.status = self.STATUS_PAID
        elif self.due_date and self.due_date < timezone.localdate():
            self.status = self.STATUS_OVERDUE
        else:
            self.status = self.STATUS_PENDING
        self.save(update_fields=['status'])


class PlayerFeePayment(models.Model):
    """Payment"""

    METHOD_CASH = "cash"
    METHOD_ONLINE = "online"
    METHOD_CHOICES = ((METHOD_CASH, "Cash"), (METHOD_ONLINE, "Online"))

    invoice = models.ForeignKey('PlayerInvoice', on_delete=models.CASCADE, related_name="payments", verbose_name="Invoice")
    amount = models.BigIntegerField(verbose_name="Amount")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="Paid At")
    receipt_number = models.CharField(max_length=255, blank=True, verbose_name="Receipt Number")
    note = models.TextField(blank=True, verbose_name="Note")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="Payment Method")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created By")
    date = models.DateField(default=timezone.now, verbose_name="Date")

    class Meta:
        ordering = ("-paid_at",)
        verbose_name = "Fee Payment"
        verbose_name_plural = "Fee Payments"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.invoice:
            self.invoice.update_status()
