from pyexpat import model
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# from commerce.commerce.settings import MEDIA_URL

image_storage = FileSystemStorage(
    location = u'{0}/my_sell/'.format(settings.MEDIA_ROOT),
    base_url= u'{0}my_sell/'.format(settings.MEDIA_URL),
)

def image_directory_path(instance, filename):
    return u'picture/{0}'.format(filename)


class User(AbstractUser):
    username = models.CharField(max_length=64, unique=True)



class Listing(models.Model):
    list_date = models.DateField(auto_now_add=True)
    top_bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "winning", blank=True, null=True, default="")
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "listings")
    starting_bid = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    name = models.CharField(max_length=64, default="Unnamed Listing")
    desc = models.CharField(max_length=500, blank=True, null=True, default="")
    image = models.ImageField(upload_to=image_directory_path, storage=image_storage, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)


    def __str__(self) -> str:
        return f"\"{self.name}\" posted by {self.poster.username} on {self.list_date}."


class Bid(models.Model):
    bid_date_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return f"Bid of {self.amount} by {self.bidder.username} for \"{self.listing.name}\"."

class Comment(models.Model):
    comment_date_time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=500, default="", blank=True, null=True)
    poster = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return f"Comment by {self.poster.username} on \"{self.listing.name}\"."

class WatchItem(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)



