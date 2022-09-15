from django import forms
from .models import Bid, Listing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("name", "desc", "starting_bid", "image", "categories")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder":"Name", "required":True}),
            "desc": forms.Textarea(attrs={"cols": 40, "rows": 10}),
            "starting_bid": forms.NumberInput(attrs={"required":True}),
            "image": forms.FileInput(attrs={"required":True}),
        }

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
