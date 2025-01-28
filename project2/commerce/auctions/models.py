from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", null=True)
    status = models.CharField(max_length=10, default="open")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_winner", null=True, blank=True)

    def __str__(self):
        return f"{self.title}: Starting Bid €{self.price}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)

    def __str__(self):
        return f"Bid of €{self.amount} for Listing {self.listing_id}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    time = models.DateTimeField(auto_now=False, auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)

    def __str__(self):
        return f"Comment on Listing {self.listing_id}"
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist")
