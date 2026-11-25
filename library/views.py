from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import BookForm, MemberForm, LoanForm
from .models import Book, Member, Loan

@login_required
def dashboard(request):
    today = timezone.localdate()
    all_loans = Loan.objects.select_related("book", "member")
    total_fines = sum((loan.fine_amount for loan in all_loans), Decimal("0.00"))
    context = {
        "book_count": Book.objects.count(),
        "copy_count": sum(Book.objects.values_list("total_copies", flat=True)),
        "member_count": Member.objects.filter(is_active=True).count(),
        "issued_count": Loan.objects.filter(status="issued").count(),
        "overdue_count": Loan.objects.filter(status="issued", due_date__lt=today).count(),
        "total_fines": total_fines,
        "recent_loans": all_loans[:6],
        "low_stock": Book.objects.filter(available_copies__lte=2).order_by("available_copies")[:5],
    }
    return render(request, "library/dashboard.html", context)


@login_required
def book_list(request):
    q = request.GET.get("q", "").strip()
    books = Book.objects.all()
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q) | Q(category__icontains=q))
    paginator = Paginator(books, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "library/book_list.html", {"books": page_obj, "page_obj": page_obj, "q": q, "result_count": paginator.count})


@login_required
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect("book_list")
    return render(request, "library/form.html", {"form": form, "title": "Add book", "back_url": "book_list"})


@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book details updated.")
        return redirect("book_list")
    return render(request, "library/form.html", {"form": form, "title": "Edit book", "back_url": "book_list"})


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        try:
            book.delete()
            messages.success(request, "Book deleted.")
        except Exception:
            messages.error(request, "This book has loan history and cannot be deleted.")
        return redirect("book_list")
    return render(request, "library/confirm_delete.html", {"object": book, "title": "Delete book", "back_url": "book_list"})


@login_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    members = Member.objects.all()
    if q:
        members = members.filter(Q(full_name__icontains=q) | Q(member_id__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    paginator = Paginator(members, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "library/member_list.html", {"members": page_obj, "page_obj": page_obj, "q": q, "result_count": paginator.count})


@login_required
def member_create(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member registered successfully.")
        return redirect("member_list")
    return render(request, "library/form.html", {"form": form, "title": "Add member", "back_url": "member_list"})


@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = MemberForm(request.POST or None, instance=member)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member details updated.")
        return redirect("member_list")
    return render(request, "library/form.html", {"form": form, "title": "Edit member", "back_url": "member_list"})


@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        try:
            member.delete()
            messages.success(request, "Member deleted.")
        except Exception:
            messages.error(request, "This member has loan history and cannot be deleted.")
        return redirect("member_list")
    return render(request, "library/confirm_delete.html", {"object": member, "title": "Delete member", "back_url": "member_list"})


@login_required
def loan_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    loans = Loan.objects.select_related("book", "member")
    if q:
        loans = loans.filter(Q(book__title__icontains=q) | Q(member__full_name__icontains=q) | Q(member__member_id__icontains=q))
    if status in ("issued", "returned"):
        loans = loans.filter(status=status)
    paginator = Paginator(loans, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "library/loan_list.html", {"loans": page_obj, "page_obj": page_obj, "q": q, "status": status, "result_count": paginator.count})


@login_required
@transaction.atomic
def loan_create(request):
    form = LoanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        book = Book.objects.select_for_update().get(pk=form.cleaned_data["book"].pk)
        if book.available_copies < 1:
            form.add_error("book", "No copies of this book are currently available.")
        else:
            loan = form.save(commit=False)
            loan.book = book
            loan.save()
            book.available_copies -= 1
            book.save(update_fields=["available_copies"])
            messages.success(request, "Book issued successfully.")
            return redirect("loan_list")
    return render(request, "library/form.html", {"form": form, "title": "Issue a book", "back_url": "loan_list"})


@login_required
@transaction.atomic
def loan_return(request, pk):
    loan = get_object_or_404(Loan.objects.select_for_update().select_related("book"), pk=pk)
    if request.method == "POST" and loan.status == "issued":
        loan.status = "returned"
        loan.return_date = timezone.localdate()
        loan.save(update_fields=["status", "return_date"])
        book = Book.objects.select_for_update().get(pk=loan.book_id)
        book.available_copies = min(book.total_copies, book.available_copies + 1)
        book.save(update_fields=["available_copies"])
        messages.success(request, f"Book returned. Calculated fine: ₹{loan.fine_amount:.2f}")
    return redirect("loan_list")