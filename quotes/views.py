from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count


from .models import Announcement, Quote, Tag
from .forms import AnnouncementForm, QuoteForm

import bleach
import json
import re
import requests
from requests_oauthlib import OAuth1


def notify_twitter(status):
    url = 'https://api.twitter.com/1.1/statuses/update.json'

    auth = OAuth1(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_SECRET)

    data = {"status": status}

    req = requests.post(url, data=data, auth=auth)

    return req.text

def post_to_twitter(request, quote):
    url = request.build_absolute_uri(reverse('view_quote', args=[quote.id]))
    content = quote.content
    content = content.replace("<br>", "\n")
    content = re.sub('<[^>]*>', '', content)
    content = content.replace("&nbsp;", " ")
    content_len = 130 - len(url)
    text = "{}{} - {}".format(content[:content_len],"..." if len(content) > content_len else "", url)
    resp = notify_twitter(text)
    respobj = json.loads(resp)

    if respobj and "id" in respobj:
        messages.success(request, "Posted tweet: {}".format(text))
        messages.success(request, "https://twitter.com/tjbash_qdb/status/{}".format(respobj["id"]))
    else:
        messages.error(request, resp)

# Create your views here.


def index_view(request):
    context = {
        "announcements": Announcement.objects.all().order_by('-creation_time')[:5],
        "num_quotes": Quote.objects.filter(approved=True).count(),
        "approval_quotes": Quote.objects.filter(approved=False).count(),
    }
    return render(request, "index.html", context)


def view_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    return render(request, "quotes.html", {"quotes": [quote]})


def view_all_tags(request):
    tags = Tag.objects.annotate(quote_count=Count('quotes')).filter(quote_count__gte=1).filter(quotes__approved=True)
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
                if len(tag_name.lower().strip()) > 0:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower().strip())
                    obj.tags.add(tag)
            messages.success(request, "Quote submitted for approval!")
            return redirect("all_quotes")
        else:
            messages.error(request, "Error adding quote :(")
    else:
        form = QuoteForm()
    tag_list = Tag.objects.filter(quotes__approved=True)
    return render(request, "form.html", {"form": form, "action": reverse("new_quote"), "tags": tag_list})


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
    return render(request, "form.html", {"form": form, "action": reverse("edit_quote", kwargs={"qid": qid})})


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
    return render(request, "form.html", {"form": form, "action": reverse("edit_announcement", kwargs={"aid": aid})})


def upvote_quote(request):
    if request.method == "POST":
        qid = request.POST.get("qid", -1)
        quote = get_object_or_404(Quote, pk=qid)
        if qid in request.session.get("upvoted", []):
            return HttpResponse("already upvoted", content_type="text/plain")
        already_upvoted = request.session.get("upvoted", [])
        already_upvoted.append(qid)
        request.session['upvoted'] = already_upvoted
        quote.votes += 1
        quote.save()
    return redirect("all_quotes")


def downvote_quote(request):
    if request.method == "POST":
        qid = request.POST.get("qid", -1)
        quote = get_object_or_404(Quote, pk=qid)
        if qid in request.session.get("downvoted", []):
            return HttpResponse("already downvoted", content_type="text/plain")
        already_downvoted = request.session.get("downvoted", [])
        already_downvoted.append(qid)
        request.session['downvoted'] = already_downvoted
        quote.votes -= 1
        quote.save()
    return redirect("all_quotes")


@login_required
def approve_quote(request, qid):
    quote = get_object_or_404(Quote, pk=qid)
    quote.approved = True
    quote.save()
    post_to_twitter(request, quote)
    return redirect("unapproved_quotes")


@login_required
def delete_quote(request):
    if request.method == "POST":
        quote = get_object_or_404(Quote, pk=request.POST.get("qid", -1))
        quote.delete()
    return redirect("unapproved_quotes")


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
