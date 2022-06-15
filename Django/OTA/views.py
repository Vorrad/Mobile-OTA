from django.shortcuts import render, HttpResponse, redirect
from datetime import datetime
from OTA import models

# Create your views here.
from OTA.models import UserInfo


def image(request):
    datalist = UserInfo.objects.all()
    print(datalist)
    return render(request, "image.html", {"datalist": datalist})


def director(request):
    return render(request, "director.html")


def api(request):
    return render(request, "api.html")


def about(request):
    return render(request, "about.html")


def login(request):
    return render(request, "login.html")


def upload(request):
    if request.method == "GET":
        return render(request, "upload.html")
    if request.method == "POST":
        u = request.POST.get("name", None)
        d = request.POST.get("device", None)
        v = request.POST.get("version", None)
        r = request.POST.get("reporter", None)
        models.UserInfo.objects.create(
            name=u,
            device=d,
            version=v,
            reporter=r,
        )

        return redirect("http://127.0.0.1:8000/image/")
    return redirect("http://127.0.0.1:8000/image/")


def example(request):
    name = request.GET.get('name')
    datalist = UserInfo.objects.filter(name=name).first()
    print(name)
    return render(request, "example.html", {"datalist": datalist})


def delete(request):
    name = request.GET.get('name')
    UserInfo.objects.filter(name=name).delete()
    return redirect("http://127.0.0.1:8000/image/")
