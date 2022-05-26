from django.shortcuts import render, HttpResponse, redirect
from datetime import datetime

from django.utils.encoding import escape_uri_path

from OTA import models
from django.http import FileResponse
# Create your views here.
from OTA.models import UserInfo
from django.http import StreamingHttpResponse

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
        file = request.FILES.get("file")
        fn = file.name
        models.UserInfo.objects.create(
            name=u,
            device=d,
            version=v,
            reporter=r,
            file_name=fn,
            file=file,
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


def download(request):
    # do something...
    def down_chunk_file_manager(file_path, chuck_size=1024):
        with open(file_path, "rb") as file:
            while True:
                chuck_stream = file.read(chuck_size)
                if chuck_stream:
                    yield chuck_stream
                else:
                    break

    fn = request.GET.get('file_name')
    the_file_name = str(fn).split("/")[-1]  # 显示在弹出对话框中的默认的下载文件名
    filename = 'E://Uptane_django/media/files/{}'.format(the_file_name)  # 要下载的文件路径
    response = StreamingHttpResponse(down_chunk_file_manager(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(the_file_name))

    return response


