from .models import WatchItem, Listing, Bid, User
from django.db.models.base import ObjectDoesNotExist

def format_price(bid_string):
    if not bid_string:
        return False
    bid_string = str(bid_string)    
    while(True):
        for i in range(len(bid_string)):
            if bid_string[i] == "," or bid_string[i] == ".":
                if i <= 3:
                    return bid_string
                bid_string = bid_string[0:i-3] + "," + bid_string[i-3:]
                break

def is_on_watchlist(request, listing):
    try: 
        WatchItem.objects.get(watcher = request.user.id, item = Listing.objects.get(id = listing.id))
        return True
    except ObjectDoesNotExist:
        return False

def get_highest_bid(listing_id):
    highest_bid = Bid.objects.filter(listing = Listing.objects.get(id = listing_id)).last()
    if highest_bid:
        return highest_bid.amount, highest_bid.bidder
    return False, False

def get_num_watch_items(request):
    user_id = request.user.id
    num_items = WatchItem.objects.filter(watcher = User.objects.get(id = user_id)).count()
    return num_items
