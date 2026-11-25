from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField("ISBN", max_length=20, unique=True)
    category = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=150, blank=True)
    published_year = models.PositiveIntegerField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} — {self.author}"

    @property
    def is_available(self):
        return self.available_copies > 0


class Member(models.Model):
    full_name = models.CharField(max_length=150)
    member_id = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    joined_on = models.DateField(default=timezone.localdate)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.member_id})"

class Loan(models.Model):
    STATUS_CHOICES = [("issued", "Issued"), ("returned", "Returned")]
    FINE_PER_DAY = Decimal("5.00")  # Change this amount to adjust the daily fine.

    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="loans")
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="issued")
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def __str__(self):
        return f"{self.book.title} → {self.member.full_name}"

    @property
    def overdue_days(self):
        """Overdue days as of today, or as of return_date for returned loans."""
        end_date = self.return_date if self.status == "returned" else timezone.localdate()
        if end_date and end_date > self.due_date:
            return (end_date - self.due_date).days
        return 0

    @property
    def fine_amount(self):
        """Calculated fine; returned loans retain the amount based on return_date."""
        return Decimal(self.overdue_days) * self.FINE_PER_DAY

    @property
    def is_overdue(self):
        return self.status == "issued" and self.overdue_days > 0