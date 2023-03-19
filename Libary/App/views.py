from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.db.models import Count
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import UserLoginForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Book


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # 验证码验证
                code = request.POST.get('verification_code')
                if code != request.session.get('code'):
                    messages.error(request, '验证码错误')
                    return render(request, 'login.html', {'form': form})

                login(request, user)
                return redirect('main')
            else:
                messages.error(request, '对不起，账号或密码输入错误')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


from django.contrib.auth import logout


def user_logout(request):
    return render(request, 'login.html')


def user_registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, '两次输入的密码不一致')
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            messages.success(request, '注册成功')
            return redirect('login')
        except:
            messages.error(request, '注册失败')
            return redirect('register')

    return render(request, 'register.html')


def main_page(request):
    books = Book.objects.all()


    return render(request, 'main.html',{'books': books})


from PIL import Image, ImageDraw, ImageFont
import random
import io


def get_verification_code(request):
    code = ''.join(str(random.randint(0, 9)) for _ in range(4))
    request.session['code'] = code
    # 生成图片
    image = Image.new('RGB', (100, 30), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', 20)
    draw.text((10, 5), code, font=font, fill=(0, 0, 0))
    # 将图片保存到内存中
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    # 将内存中的图片数据返回给客户端
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def logout_view(request):
    logout(request)
    # 处理用户注销后的其他操作
    return redirect('login')


from .forms import BookForm


def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_edit.html', {'form': form})


# 删除图书信息


from django.views.generic.edit import CreateView


class CreateBookView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'create_book.html'


from django.shortcuts import render, redirect
from .forms import BookForm

'''
首先检查请求的方法是否为 POST。如果是，
我们就尝试从 POST 请求中获取图书的相关信息，
并创建一个新的 Book 对象。然后，
我们调用 full_clean 方法来验证该对象的字段是否符合要求。
如果字段验证通过，则将该对象保存到数据库，
并将 book 对象传递给 main.html 模板进行显示。
'''


def add_book(request):
    if request.method == 'POST':
        try:
            book = Book(
                book_name=request.POST['book_name'],
                editor=request.POST['editor'],
                price=request.POST['price'],
                category=request.POST['category'],
                publish_date=request.POST['publish_date']
            )
            book.full_clean()  # 验证字段
            book.save()
            messages.success(request, '图书添加成功！')
            return redirect('main')
        except ValidationError as e:
            return render(request, 'add_book.html', {'error_message': str(e)})
    else:
        return render(request, 'add_book.html')


from django.views.generic import TemplateView


class AnalysisView(TemplateView):
    template_name = 'analysis.html'


from django.shortcuts import redirect


def delete_books(request):
    if request.method == 'POST':
        selected_books = request.POST.getlist('book_ids')
        Book.objects.filter(id__in=selected_books).delete()
    return redirect('main')


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, '图书修改成功！')
            # return render(request, 'book_detail.html', {'form': form, 'book': book})
            return redirect('main')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_detail.html', {'form': form, 'book': book})


def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.delete()
        messages.success(request, '删除成功！')
        return redirect('main')

    return render(request, 'book_detail.html', {'book': book})


from django.shortcuts import render
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from pyecharts.charts import Bar, Line
def chart_view(request):
    # 获取所有的图书和类别信息
    book_category = Book.objects.values('category').annotate(count=Count('book_id'))
    category = [i['category'] for i in book_category]
    book_count = [i['count'] for i in book_category]
    pie_chart = Pie()
    pie_chart.add('', list(zip(category, book_count)))
    pie_chart.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    pie_chart = pie_chart.render_embed()

    # 获取所有的图书和价格信息
    book_price = Book.objects.values_list('book_name', 'price')
    book_title = [i[0] for i in book_price]
    price = [i[1] for i in book_price]
    bar_chart = Bar()
    bar_chart.add_xaxis(book_title)
    bar_chart.add_yaxis('', price)
    bar_chart.set_series_opts(label_opts=opts.LabelOpts(formatter="{c}元"))
    bar_chart = bar_chart.render_embed()

    return render(request, 'chart.html', {'pie_chart': pie_chart, 'bar_chart': bar_chart})

from django.db.models import Q
from django.views.generic import ListView
from .models import Book

class BookSearchView(ListView):
    model = Book
    template_name = 'search_result.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get('search')
        object_list = Book.objects.filter(
            Q(book_name__icontains=query) | Q(category__icontains=query) | Q(editor__icontains=query)
        )
        return object_list

import requests

def get_weather(city):
    api_key = 'ba1a771c3f456c87b89e5d78db03e9cd'  # 替换为你自己的API key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['main']
        temperature = data['main']['temp'] - 273.15  # 转换为摄氏度
        return f"{city}天气：{weather}，温度：{temperature:.1f}℃"
    else:
        return f"{city}天气获取失败"

class IndexView(LoginRequiredMixin, View):
    login_url = 'login.html'

    def get(self, request):
        city = '芜湖'  # 这里可以替换成你要显示的城市
        weather = get_weather(city)
        print(weather)
        context = {
            'weather': weather,
        }
        return render(request, 'index.html', context)