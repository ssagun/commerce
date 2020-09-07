from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import User,Bid,Listing,Comment,Watchlist,Closedbid
from .models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime


def index(request):
    items = Listing.objects.all()
    return render(request, "auctions/index.html",{
        "items":items
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
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    items=Listing.objects.raw("SELECT * FROM auctions_listing GROUP BY category")
    return render(request,"auctions/category_page.html",{
        "items": items
    })


def category(request, category):
    items = Listing.objects.filter(category = category)
    return render(request,"auctions/category.html",{
        "items":items,
        "category":category
    })


def create(request):
    if request.method == "POST":
        list = Listing()
        date = datetime.now()
        dt = date.strftime(" %c ")
        list.owner = request.user.username
        list.title = request.POST.get('title')
        list.description = request.POST.get('description')
        list.price = request.POST.get('price')
        list.category = request.POST.get('category')
        if request.POST.get('link'):
            list.link = request.POST.get('link')
        else :
            list.link = "https://pixelz.cc/wp-content/uploads/2018/12/pewdiepie-red-and-black-wavy-background-uhd-4k-wallpaper.jpg"
        list.time = dt
        list.save()
        return redirect('index')
    else:
        return render(request,"auctions/create.html")


def listings(request,id):
    try:
        item = Listing.objects.get(id=id)
        if item.owner == request.user.username :
            owner=True
        else:
            owner=False
    except:
        return redirect('index')
    try:
        comments = Comment.objects.filter(listingid=id)
    except:
        comments = None
    if request.user.username:
        try:
            if Watchlist.objects.get(user=request.user.username, listingid=id):
                watch = True
        except:
            watch = False
    else:
        owner=False
        watch=False
    return render(request,"auctions/listings.html",{
        "i":item,
        "owner":owner,
        "watch":watch,
        "error":request.COOKIES.get('error'),
        "successbid":request.COOKIES.get('successbid'),
        "comments":comments
    })


def removewatchlist(request, listingid):
    w = Watchlist.objects.get(user=request.user.username,listingid=listingid)
    w.delete()
    return redirect('listings',id=listingid)


def addwatchlist(request, listingid):
    w = Watchlist()
    w.user = request.user.username
    w.listingid = listingid
    w.save()
    return redirect('listings',id = listingid)


def bid(request, listingid):
    current_bid = Listing.objects.get(id=listingid)
    current_bid = current_bid.price
    if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            listing_item = Listing.objects.get(id = listingid)
            listing_item.price = user_bid
            listing_item.save()
            try:
                if Bid.objects.filter(id = listingid):
                    ibid = Bid.objects.filter(id=listingid)
                    ibid.delete()
                bidtable = Bid()
                bidtable.user = request.user.username
                bidtable.title = listing_item.title
                bidtable.listingid = listingid
                bidtable.bid = user_bid
                bidtable.save()

            except:
                bidtable = Bid()
                bidtable.user=request.user.username
                bidtable.title = listing_items.title
                bidtable.listingid = listingid
                bidtable.bid = user_bid
                bidtable.save()
            response = redirect('listings',id=listingid)
            response.set_cookie('successbid','bid successful!!!',max_age=3)
            return response
        else :
            response = redirect('listings',id=listingid)
            response.set_cookie('error','Bid should be greater than current price',max_age=3)
            return response
    else:
        return redirect('index')


def comment(request,listingid):
    if request.method == "POST":
        date = datetime.now()
        dt = date.strftime(" %c ")
        c = Comment()
        c.comment = request.POST.get('comment')
        c.user = request.user.username
        c.time = dt
        c.listingid = listingid
        c.save()
        return redirect('listings',id=listingid)
    else :
        return redirect('index')


def watchlist(request, username):
    if request.user.username:
        try:
            w = Watchlist.objects.filter(user = username)
            items = []
            for i in w:
                items.append(Listing.objects.filter(id=i.listingid))
            return render(request,"auctions/watchlist.html",{
                "items":items
            })
        except:
            return render(request,"auctions/watchlist.html",{
                "items":None
            })
    else:
        return redirect('index')


def closebid(request, listingid):
    if request.user.username:
        try:
            item = Listing.objects.get(id = listingid)
        except:
            return redirect('index')
        cb = Closedbid()
        title = item.title
        cb.owner = item.owner
        cb.listingid = listingid
        cb.ctitle = item.title
        cb.cdescription = item.description
        try:
            bid = Bid.objects.get(listingid = listingid, bid = item.price)
            cb.winner = bid.user
            cb.price = bid.bid
            cb.save()
            bid.delete()
        except:
            cb.winner = item.owner
            cb.price = item.price
            cb.save()
        try:
            if Watchlist.objects.filter(listingid = listingid):
                watch = Watchlist.objects.filter(listingid = listingid)
                watch.delete()
            else:
                pass
        except:
            pass
        try:
            comment = Comment.objects.filter(listingid = listingid)
            comment.delete()
        except:
            pass
        try:
            bid = Bid.objects.filter(listingid = listingid)
            bid.delete()
        except:
            pass
        try:
            cblist = Closedbid.objects.get(listingid=listingid)
        except:
            cb.owner = item.owner
            cb.winner = item.owner
            cb.listingid = listingid
            cb.winprice = item.price
            cb.ctitle = item.title
            cb.cdescription = item.description
            cb.save()
            cblist = Closedbid.objects.get(listingid=listingid)
        item.delete()
        return render(request,"auctions/bidend.html",{
            "cb":cblist,
            "title":title
        })

    else:
        return redirect('index')


def win(request):
    if request.user.username:
        items=[]
        try:
            wonitems = Closedbid.objects.filter(winner = request.user.username)
        except:
            wonitems = None
        return render(request,'auctions/win.html',{
            "wonitems":wonitems
        })
    else:
        return redirect('index')
