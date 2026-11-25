from django.contrib import admin
from .models import Book, Member, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "total_copies", "available_copies")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "member_id", "email", "phone", "is_active")
    search_fields = ("full_name", "member_id", "email")
    list_filter = ("is_active",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "member", "issue_date", "due_date", "return_date", "status")
    search_fields = ("book__title", "member__full_name", "member__member_id")
    list_filter = ("status", "issue_date", "due_date")
