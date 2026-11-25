from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Book, Member, Loan


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            current = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (current + " form-control").strip()
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)


class BookForm(StyledModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "category", "publisher", "published_year",
                  "total_copies", "available_copies", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class MemberForm(StyledModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "member_id", "email", "phone", "address", "joined_on", "is_active"]
        widgets = {
            "joined_on": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class LoanForm(StyledModelForm):
    class Meta:
        model = Loan
        fields = ["book", "member", "due_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional notes"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["book"].queryset = Book.objects.filter(available_copies__gt=0)
        self.fields["member"].queryset = Member.objects.filter(is_active=True)
        self.fields["due_date"].initial = timezone.localdate() + timedelta(days=14)
