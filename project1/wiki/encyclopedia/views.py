from django.shortcuts import render, redirect
from django.urls import reverse
from markdown2 import markdown
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, entry):
    if not util.get_entry(entry):
        return render(request, "encyclopedia/error.html", {
            "message": f"The requested page: {entry} could not be found.",
            "link": reverse("index")
        })
    entries = util.list_entries()
    for item in entries:
         if entry.lower() == item.lower():
              title = item
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": markdown(util.get_entry(entry))
    })

def search(request):
    query = request.GET.get("q", "")
    if not util.get_entry(query):
        results = []
        entries = util.list_entries()
        for entry in entries:
            if query.lower() in entry.lower():
                results.append(entry)
        return render(request, "encyclopedia/search_results.html", {
            "results": results
        })
    return redirect(wiki, query)

def newpage(request):
    if request.method == "GET":
        return render(request, "encyclopedia/newpage.html")
    if request.method == "POST":
        # first check data in both fields, if missing then show error page
        title = request.POST.get("title")
        entry = request.POST.get("entry")
        if not title or not entry:
            return render(request, "encyclopedia/error.html", {
                "message": "Title and Entry fields must be filled.",
                "link": reverse("newpage")
            })
        
        # if data good then check entry doesn't already exist
        entries = util.list_entries()
        for item in entries:
            if title.lower() == item.lower():
                return render(request, "encyclopedia/error.html", {
                    "message": f"Entry \"{title}\" already exists.",
                    "link": reverse("newpage")
                })

        # if doesn't already exist then save new entry
        util.save_entry(title, entry)
        return redirect(wiki, title)
    
def editpage(request, entry):
    if request.method == "GET":
        # if entry exists already, render page to edit
        entries = util.list_entries()
        for item in entries:
            if entry.lower() == item.lower():
                return render(request, "encyclopedia/editpage.html", {
                    "title": entry,
                    "entry": util.get_entry(entry)
                })
        # if no entry found, error page
        return render(request, "encyclopedia/error.html", {
                    "message": f"The requested page: {entry} could not be found.",
                    "link": reverse("index")
                })                 
    if request.method == "POST":
        new_entry = request.POST.get("entry")
        util.save_entry(entry, new_entry)
        return render(request, "encyclopedia/entry.html", {
            "title": entry,
            "entry": markdown(util.get_entry(entry))
        })
    
def randompage(request):
    entries = util.list_entries()
    choice = random.choice(entries)
    return redirect(wiki, choice)