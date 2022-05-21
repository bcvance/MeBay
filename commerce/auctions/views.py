from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import ListingForm
from .models import User, Listing, Bid, Comment, WatchItem, Category
from datetime import date
from .utils import format_price, is_on_watchlist, get_highest_bid, get_num_watch_items
from django.db.models.base import ObjectDoesNotExist
from itertools import zip_longest

def index(request):
    listings_data = []
    listings_list = list(Listing.objects.filter(active = True))
    for listing in listings_list:
        bid_string = str(listing.starting_bid)
        price_formatted = format_price(bid_string)
        watchlist = is_on_watchlist(request, listing)
        highest_bid, highest_bidder = get_highest_bid(listing.id)
        highest_bid = format_price(highest_bid)
        watch_items = get_num_watch_items(request)
        listings_data.append({
            "listing": listing,
            "price": price_formatted,
            "watchlist": watchlist,
            "highest_bid": highest_bid
        })
    return render(request, "auctions/index.html", {
        "listings": listings_data,
        "watch_items": watch_items
    })

def bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        highest_bid = Bid.objects.filter(listing = Listing(id=listing_id)).last()
        this_bid = request.POST["bid_amount"].replace(",", "")
        if highest_bid:
            if float(this_bid) <= highest_bid.amount:
                pass
                # figure out how to throw error message here 
            else:
                new_bid = Bid(amount = float(this_bid), listing = Listing.objects.get(id=listing_id), bidder = User.objects.get(id=request.user.id))
                new_bid.save()
        else:
            if float(this_bid) <= Listing.objects.get(id=listing_id).starting_bid:
                pass
                # figure out how to throw error message here 
            else:
                new_bid = Bid(amount = float(this_bid), listing = Listing.objects.get(id=listing_id), bidder = User.objects.get(id=request.user.id))
                new_bid.save()
    return redirect(request.META['HTTP_REFERER'])

def categories(request):
    categories_list = list(Category.objects.all())
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/categories.html", context={
        "categories_list": categories_list,
        "watch_items": watch_items
    })

def category(request, category_id):
    category = Category.objects.get(id=category_id)
    listings_list = list(Listing.objects.filter(categories = category, active = True))
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/category.html", context={
        "listings_list": listings_list,
        "category": category,
        "watch_items": watch_items
    })

def close(request):
    listing = Listing.objects.get(id=request.POST["listing_id"])
    listing.active = False
    if Bid.objects.filter(listing = listing).exists():
        listing.winner = Bid.objects.filter(listing=listing).last().bidder.id
    listing.save()
    return HttpResponseRedirect(reverse("listings"))

def comment(request):
    if request.method == "POST":
        new_comment = Comment(content = request.POST["comment"], poster = User.objects.get(id=request.user.id), listing = Listing.objects.get(id = request.POST["listing_id"]))
        new_comment.save()
        return redirect(request.META['HTTP_REFERER'])


def create(request):
    if request.method == "POST" and request.FILES["image"]:
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.poster = User.objects.filter(id = request.user.id).first()
            model_instance.save()
            form.save_m2m()
        return HttpResponseRedirect(reverse("index"))
    form = ListingForm()
    listings = Listing.objects.all()
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/create.html", context={
        "listings":listings,
        "form": form,
        "watch_items": watch_items
    })

def delete(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        Listing.objects.get(id=listing_id).delete()
        return HttpResponseRedirect(reverse("listings"))

def listing(request, item_id):
    listing = Listing.objects.filter(id=item_id).first()
    bid_string = str(listing.starting_bid)
    price_formatted = format_price(bid_string)
    watchlist = is_on_watchlist(request, listing)
    highest_bid, highest_bidder = get_highest_bid(item_id)
    highest_bid = format_price(highest_bid)
    comments = list(Comment.objects.filter(listing = Listing.objects.get(id = item_id)))
    comments.reverse()
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/listing.html", context={
        "listing": listing,
        "price_formatted": price_formatted,
        "watchlist": watchlist,
        "highest_bid": highest_bid,
        "highest_bidder": highest_bidder,
        "comments": comments,
        "user_id": request.user.id,
        "watch_items": watch_items
    })


def listings(request):
    user = User.objects.filter(id=request.user.id).first()
    my_listings = Listing.objects.filter(poster=user)
    my_wins = Listing.objects.filter(winner = request.user.id)
    if not my_wins.exists():
        my_wins_list = [-1]
    else:
        my_wins_list = list(my_wins)
    if not my_listings.exists():
        my_listings_list = [-1]
    else:
        my_listings_list = list(my_listings)
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/listings.html", context={
        "my_listings_list": zip_longest(my_listings_list, my_wins_list, fillvalue=None),
        "watch_items": watch_items
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        request.session["username"] = username
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def watch_del(request):
    listing_id = request.POST["listing_id"]
    WatchItem.objects.get(item = Listing.objects.get(id = listing_id), watcher = User.objects.get(id = request.user.id)).delete()
    return HttpResponseRedirect(reverse("watchlist"))

def watch_add(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        try:
            WatchItem.objects.get(watcher = User.objects.filter(id=request.user.id).first(), item = Listing.objects.filter(id=listing_id).first())
        except ObjectDoesNotExist:    
            watch_item = WatchItem(watcher = User.objects.filter(id=request.user.id).first(), item = Listing.objects.filter(id=listing_id).first())
            watch_item.save()
        return HttpResponseRedirect(reverse("watchlist"))

def watchlist(request):
    watch_items_list = list(WatchItem.objects.filter(watcher = User.objects.get(id = request.user.id)))
    prices_formatted = []
    for item in watch_items_list:
        bid_string = str(item.item.starting_bid)
        prices_formatted.append(format_price(bid_string))
    watch_items = get_num_watch_items(request)
    return render(request, "auctions/watchlist.html", context={
        "watch_items_list": zip(watch_items_list, prices_formatted),
        "watch_items": watch_items
    })


