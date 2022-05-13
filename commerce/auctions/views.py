from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import ListingForm
from .models import User, Listing, Bid, Comment, WatchItem
from datetime import date
from .utils import format_price, is_on_watchlist, get_highest_bid
from django.db.models.base import ObjectDoesNotExist

def index(request):
    listings_data = []
    listings_list = list(Listing.objects.all())
    for listing in listings_list:
        bid_string = str(listing.starting_bid)
        price_formatted = format_price(bid_string)
        watchlist = is_on_watchlist(request, listing)
        highest_bid = format_price(get_highest_bid(listing.id))
        listings_data.append({
            "listing": listing,
            "price": price_formatted,
            "watchlist": watchlist,
            "highest_bid": highest_bid
        })
    return render(request, "auctions/index.html", {
        "listings": listings_data
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
        return HttpResponseRedirect(reverse("index"))
    form = ListingForm()
    listings = Listing.objects.all()
    return render(request, "auctions/create.html", context={
        "listings":listings,
        "form": form
    })

def delete(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        Listing.objects.filter(id=listing_id).delete()
        return HttpResponseRedirect(reverse("listings"))

def listing(request, item_id):
    listing = Listing.objects.filter(id=item_id).first()
    bid_string = str(listing.starting_bid)
    price_formatted = format_price(bid_string)
    watchlist = is_on_watchlist(request, listing)
    highest_bid = format_price(get_highest_bid(item_id))
    comments = list(Comment.objects.filter(listing = Listing.objects.get(id = item_id)))
    comments.reverse()
    return render(request, "auctions/listing.html", context={
        "listing": listing,
        "price_formatted": price_formatted,
        "watchlist": watchlist,
        "highest_bid": highest_bid,
        "comments": comments
    })



    

def listings(request):
    user = User.objects.filter(id=request.user.id).first()
    my_listings_list = list(Listing.objects.filter(poster=user))
    return render(request, "auctions/listings.html", context={
        "my_listings_list": my_listings_list
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
    return render(request, "auctions/watchlist.html", context={
        "watch_items_list": zip(watch_items_list, prices_formatted)
    })


