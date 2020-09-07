from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category/<str:category>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("create", views.create, name="create"),
    path("listings/<int:id>",views.listings,name="listings"),
    path("removewatchlist/<int:listingid>",views.removewatchlist,name="removewatchlist"),
    path("addwatchlist/<int:listingid>",views.addwatchlist,name="addwatchlist"),
    path("bid/<int:listingid>",views.bid,name="bid"),
    path("comment/<int:listingid>",views.comment,name="comment"),
    path("watchlist/<str:username>",views.watchlist,name="watchlist"),
    path("closebid/<int:listingid>",views.closebid,name="closebid"),
    path("win",views.win,name="win")
]
