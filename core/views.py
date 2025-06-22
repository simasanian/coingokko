from django.shortcuts import render, redirect
from .models import User, Transaction
from .forms import TransactionForm, AddUserForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseForbidden

from functools import wraps


# ==========================
# ここからログイン必須ページの試作
# ==========================

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
#旧
#        if not request.session.get('user_id'):
#            return redirect('login')  # name='login' に設定しているURLに飛ばす
#        return view_func(request, *args, **kwargs)
#   return _wrapped_view
#新提案
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        try:
            request.user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==========================
# ここまで
# ==========================


def index(request):
    return render(request, 'index.html')

@login_required_custom
def send_coin(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
#        form = TransactionForm(request.POST, user=request.user)
        form = TransactionForm(request.POST, user=user)

        if form.is_valid():
            print("送信者:", form.cleaned_data["sender"], type(form.cleaned_data["sender"]))
            print("ログイン中:", request.user, type(request.user))
            sender = form.cleaned_data['sender']
            receiver = form.cleaned_data['receiver']
            amount = form.cleaned_data['amount']
            #セキュリティチェック（不正送信対策）
            if sender != request.user:
                return HttpResponseForbidden("他人のアカウントから送金はできません")

            if sender == receiver:
                messages.error(request, "自分自身には送金できません。")
            elif sender.balance < amount:
                messages.error(request, "残高が足りません。")
            else:
                #残高更新
                sender.balance -= amount
                receiver.balance += amount
                sender.save()
                receiver.save()

                #トランザクション記録
                Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount
                )
                messages.success(request, f"{amount} coinを{receiver.username}に送金しました！")
                return redirect('send_coin')
    else:
        form = TransactionForm(user=user)

    return render(request, 'send.html', {'form': form})



@login_required_custom
def history_view(request):
    transaction_list = Transaction.objects.all().order_by('-timestamp') 
    paginator = Paginator(transaction_list, 10) #1p10件の表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'history.html', {'transactions': page_obj})

def add_user_view(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.balance = form.cleaned_data['balance']
            user.save()
            return redirect('index')
    else:
        form = AddUserForm()
    return render(request, 'add_user.html', {'form': form})

@login_required_custom
def mypage_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = User.objects.get(id=user_id)

    # 送信履歴のページネーション
    sent_list = Transaction.objects.filter(sender=user).order_by('-timestamp')
    sent_paginator = Paginator(sent_list, 5)
    sent_page_number = request.GET.get('sent_page')
    sent_transactions = sent_paginator.get_page(sent_page_number)

    # 受信履歴のページネーション
    received_list = Transaction.objects.filter(receiver=user).order_by('-timestamp')
    received_paginator = Paginator(received_list, 5)
    received_page_number = request.GET.get('received_page')
    received_transactions = received_paginator.get_page(received_page_number)

    context = {
        'user': user,
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
    }
    return render(request, 'mypage.html', context)


def login_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']

        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'ユーザーが存在しません'})

        if check_password(password, user.password):
            request.session['user_id'] = user.id
            return redirect('mypage')
        else:
            return render(request, 'login.html', {'error': 'パスワードが違います'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    request.session.flush()  # セッション削除
    return redirect('index')



