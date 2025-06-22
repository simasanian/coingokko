from django.urls import path
from .views import send_coin
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_coin, name='send_coin'),
    path('adduser/', views.add_user_view, name='add_user'),
    path('history/', views.history_view, name='history'),
#    path('mypage/<int:user_id>/', views.mypage_view, name='mypage'), #ログイン処理作り直したらコメントアウト外す
    # ==========================
    # 簡易ログイン処理（本番実装時には変更予定）
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', views.mypage_view, name='mypage'), #簡易ログイン用のマイページURL

    # ==========================
]