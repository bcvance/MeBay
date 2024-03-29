from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings", views.listings, name="listings"),
    path("delete", views.delete, name="delete"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("watch_add", views.watch_add, name="watch_add"),
    path("watch_del", views.watch_del, name="watch_del"),
    path("categories", views.categories, name="categories"),
    path("comment", views.comment, name="comment"),
    path("close", views.close, name="close"),
    path("category/<int:category_id>", views.category, name="category"),
    path("<int:item_id>", views.listing, name="listing"),
]
