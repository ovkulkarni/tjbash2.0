from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Announcement, Quote, Tag
from .forms import AnnouncementForm, QuoteForm

import bleach

# Create your views here.

def index_view(request):
    context = {
            "announcements": Announcement.objects.all()[:5],
            "num_quotes": Quote.objects.filter(approved=True).count(),
            "approval_quotes": Quote.objects.filter(approved=False).count(),
            }
    return render(request, "index.html", context)

def view_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    return render(request, "quotes.html", {"quotes":[quote]})

def view_all_tags(request):
    tags = Tag.objects.annotate(quote_count=Count('quotes')).filter(quote_count__gte=1)
    tags_list = [{"text": tag.name, "weight": tag.quotes.count(), "link": "{}?tag={}".format(reverse("quotes_by_tag"), tag.name)} for tag in tags]
    return render(request, "tags.html", {"tags": tags_list})

def view_all_quotes(request):
    quotes_list = Quote.objects.filter(approved=True).order_by('-id')
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    context = {
            "quotes": quotes
            }
    return render(request, "quotes.html", context)

def view_top_quotes(request):
    quotes_list = Quote.objects.filter(approved=True).order_by('-votes')
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    context = {
            "quotes": quotes
            }
    return render(request, "quotes.html", context)

def view_bottom_quotes(request):
    quotes_list = Quote.objects.filter(approved=True).order_by('votes')
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    context = {
            "quotes": quotes
            }
    return render(request, "quotes.html", context)

def view_quotes_by_tag(request):
    quotes_list = Quote.objects.filter(approved=True, tags__name=request.GET.get("tag", "")).order_by('-votes')
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    context = {
            "quotes": quotes
            }
    return render(request, "quotes.html", context)

def create_new_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            tag_names = form.cleaned_data["tags"].split(",")
            obj = form.save(commit=True)
            obj.content = bleach.clean(obj.content.replace("\r\n", "<br>"), tags=[u"br"])
            obj.save()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                obj.tags.add(tag)
            messages.success(request, "Quote submitted for approval!")
            return redirect("all_quotes")
        else:
            messages.error(request, "Error adding quote :(")
    else:
        form = QuoteForm()
    return render(request, "form.html", {"form": form, "action": reverse("new_quote")})

@login_required
def edit_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    if request.method == "POST":
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            tag_names = form.cleaned_data["tags"].split(",")
            obj = form.save()
            obj.content = bleach.clean(obj.content.replace("\r\n", "<br>"), tags=[u"br"])
            obj.save()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                obj.tags.add(tag)
            return redirect("all_quotes")
        else:
            messages.error(request, "Error adding quote :(")
    else:
        form = QuoteForm(instance=quote)
    return render(request, "form.html", {"form": form, "action": reverse("edit_quote", kwargs={"qid":qid})})

@login_required
def add_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.content = bleach.clean(obj.content.replace("\r\n", "<br>"), tags=[u"br"])
            obj.save()
            return redirect("index")
        else:
            messages.error(request, "Error adding announcement :(")
    else:
        form = AnnouncementForm()
    return render(request, "form.html", {"form": form, "action": reverse("new_announcement")})

@login_required
def edit_announcement(request, aid):
    ann = get_object_or_404(Announcement, pk=aid)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            obj = form.save()
            obj.content = bleach.clean(obj.content.replace("\r\n", "<br>"), tags=[u"br"])
            obj.save()
            return redirect("index")
        else:
            messages.error(request, "Error adding announcement :(")
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, "form.html", {"form": form, "action": reverse("edit_announcement", kwargs={"aid":aid})})

def upvote_quote(request):
    if request.method == "POST":
        qid = request.POST.get("qid", -1)
        quote = get_object_or_404(Quote, pk=qid)
        quote.votes += 1
        quote.save()
    return redirect("all_quotes")

def downvote_quote(request):
    if request.method == "POST":
        qid = request.POST.get("qid", -1)
        quote = get_object_or_404(Quote, pk=qid)
        quote.votes -= 1
        quote.save()
    return redirect("all_quotes")

@login_required
def approve_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    quote.approved = True
    quote.save()
    return redirect("all_quotes")

@login_required
def delete_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    quote.delete()
    return redirect("all_quotes")

@login_required
def view_unapproved_quotes(request):
    quotes_list = Quote.objects.filter(approved=False)
    paginator = Paginator(quotes_list, 10)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    context = {
            "quotes": quotes
            }
    return render(request, "quotes.html", context)
