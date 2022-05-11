from django.shortcuts import render,HttpResponse

# Create your views here.

def image(request):
    return render(request,"image.html")

def director(request):
    return render(request,"director.html")

def api(request):
    return render(request,"api.html")

def about(request):
    return render(request,"about.html")

def login(request):

    return render(request,"login.html")