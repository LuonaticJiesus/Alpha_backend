from django.urls import path

from four_s.four_s_notice import *
from four_s.four_s_user import *

urlpatterns = [
    # user
    path('user/signup/', user_signup, name='user_signup'),
    path('user/login/', user_login, name='user_login'),
    path('user/changePwd/', user_change_pwd, name='user_change_pwd'),

    # notice
    path(r'notice/queryRecv/', notice_query_recv, name='notice_query_recv'),
    path(r'notice/querySend/', notice_query_send, name='notice_query_send'),
    path(r'notice/queryBlock/', notice_query_block, name='notice_query_block'),
    path('notice/publish/', notice_publish, name='notice_publish'),
    path('notice/delete/', notice_delete, name='notice_delete'),
]