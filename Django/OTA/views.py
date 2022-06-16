from django.shortcuts import render

# Create your views here.
import datetime as datetime
from django.shortcuts import render, HttpResponse, redirect
import datetime
import time
from django.utils.encoding import escape_uri_path


from django.http import FileResponse
# Create your views here.
from django.http import StreamingHttpResponse
import json

from django.conf import settings



# Create your views here.
Objects_list = []

def image(request):
    datalist = Objects_list
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
    global Objects_list
    if request.method == "GET":
        return render(request, "upload.html")
    if request.method == "POST":
        now = time.localtime()
        datetime = time.strftime("%Y-%m-%d-%H_%M_%S", now)
        u = request.POST.get("name", None)
        v = request.POST.get("version", None)
        r = request.POST.get("reporter", None)
        vin = request.POST.get("vin", None)
        ut = "normal"
        myfile = request.FILES.get('file', None)
        fn = myfile.name
        object_dict = {"datetime": datetime, "name": u, "timestamp": None, "update_image": fn, "update_type": ut,"version": v,"reporter": r,"vin": vin,}
        Objects_list.append(object_dict)
        try:
            suffix = str(myfile.name.split('.')[-1])
            times = str(time.time()).split('.').pop()  # 生成时间戳，取小数点后的值
            fil = str(myfile.name.split('.')[0])
            filename = times + '_' + fil + '.' + suffix
            filename_dir = settings.MEDIA_ROOT
            with open(filename_dir + filename, 'wb+') as destination:
                for chunk in myfile.chunks():
                    destination.write(chunk)
                destination.close()
        except:
            return HttpResponse("提交失败")
        else:
            return redirect("/image/")
    return redirect("/image/")



def example(request):
    name = request.GET.get('name')
    for obj_dict in Objects_list:
        if obj_dict["name"] == name:
            print(obj_dict)  # item_dict就是要找的那个字典了
            datalist = obj_dict
        else:
            pass
    print(name)
    return render(request, "example.html", {"datalist": datalist})


def delete(request):
    global Objects_list
    name = request.GET.get('name')
    Objects_list = [item for item in Objects_list if not item["name"] == name]
    return redirect("/image/")


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

    fn = request.GET.get('update_image')
    the_file_name = str(fn).split("/")[-1]  # 显示在弹出对话框中的默认的下载文件名
    filename = '/media/files/{}'.format(the_file_name)  # 要下载的文件路径
    response = StreamingHttpResponse(down_chunk_file_manager(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(the_file_name))

    return response


