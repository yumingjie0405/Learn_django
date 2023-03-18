from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm, BookForm
import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from django.http import HttpResponse

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
    return render(request, 'main.html', {'books': books})


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


from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy


class BookListView(ListView):
    model = Book
    template_name = 'main.html'
    context_object_name = 'books'


class BookUpdateView(UpdateView):
    model = Book
    fields = ['book_name', 'price', 'publish_date', 'category', 'editor']
    template_name_suffix = '_update_form'


class BookDeleteView(DeleteView):
    model = Book
    success_url = reverse_lazy('main')
    template_name_suffix = '_confirm_delete'


from .forms import BookForm


def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form})


# 删除图书信息


def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('book_list')


from django.views.generic.edit import CreateView


class CreateBookView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'create_book.html'


from django.shortcuts import render, redirect
from .forms import BookForm


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})


from django.views.generic import TemplateView


class AnalysisView(TemplateView):
    template_name = 'analysis.html'


from django.shortcuts import redirect


def delete_books(request):
    if request.method == 'POST':
        selected_books = request.POST.getlist('book_ids')
        Book.objects.filter(id__in=selected_books).delete()
    return redirect('main')


def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('main')
        else:
            messages.error(request, 'Book update failed. Please check the form data.')
    context = {'form': form}
    return render(request, 'edit_book.html', context)


def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('main')
    context = {'book': book}
    return render(request, 'delete_book.html', context)
