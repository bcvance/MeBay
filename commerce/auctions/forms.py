from django import forms
from .models import Bid, Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("name", "desc", "starting_bid", "image", "categories")
        widgets = {
            "desc": forms.Textarea(attrs={"cols": 40, "rows": 10})
        }
