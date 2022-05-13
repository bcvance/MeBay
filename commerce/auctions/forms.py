from django import forms
from .models import Bid, Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("name", "desc", "starting_bid", "image", "category")
