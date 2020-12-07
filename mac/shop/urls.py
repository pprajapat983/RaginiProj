from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path("",views.index,name="ShopHome"),
   path("about/",views.about,name="AboutUs"),
   path("contact/",views.contact,name="ContactUs"),
   path("tracker/",views.tracker,name="TrackingStatus"),
   path("search/",views.search,name="Search"),
   path("products/<int:myid>",views.productView,name="ProductView"),
   path("checkout/",views.checkout,name="Checkout"),
   path('signup',views.handleSignup,name='signup'),
   path('login',views.handleLogin,name='login'),
   path('logout',views.handleLogout,name='logout'),
   path('handlerequest',views.handlerequest,name='HandleRequest'),
   path('productcomment/',views.productcom,name='productcomment'),
]