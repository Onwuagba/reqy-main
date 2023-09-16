from django.urls import path
from .views import forgotPassword, SignUp, login, test1

app_name = 'sys_user'

urlpatterns = [
    #auth URL
    path("login/", login, name='login'),
    path("forgot-password/", forgotPassword, name='forgotPass'),
    path("signup/", SignUp, name='signUp'),
    path("test1/", test1, name='test1'),

    #staff URLs
    # path("", home, name='home'),
]