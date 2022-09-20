
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('contactus',views.contactus,name='contactus'),
    path('aboutus',views.aboutus,name='aboutus'),
    path('fetch',views.fetch,name='fetch'),
    path('login',views.login,name='login'),
    path('GPSPORT',views.GPSPORT,name='GPSPORT'),
    path('dbfiller',views.dbfiller,name='dbfiller'),
    path('sendmail',views.sendmail,name='sendmail')
]