"""wireform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.urls import path, include, re_path
from django.views.i18n import JavaScriptCatalog
from formpage import views
from formpage.views import  render_entry_view, CloneView, create_template, update_template,update_order,TemplateView, order_confirmation, CompletedOrderListView,RecurrentOrderListView,PendingOrderListView,ProccesingOrderListView,staff_registration,render_authorization_entry_view
import django
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'formpage.views.custom_404_page'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('register/staff', views.staff_registration, name='staff_registration'),
    path('login/', views.login_page,name='login'),
    path('logout/', views.logout_page,name='logout'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),

    path('', views.index, name='home'),
    path('authorization/', views.render_authorization_entries, name='authorization'),
    path('authorization_entry/<int:pk>/', render_authorization_entry_view.as_view(), name='authorization_entry'),
    path('authorize_wire/<int:pk>/', views.authorize_wire, name='authorize_wire'),
    path('reject_unauthorized_wire/<int:pk>/', views.reject_unauthorized_wire, name='reject_unauthorized_wire'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/recurrent', RecurrentOrderListView.as_view() , name='recurrent_orders'),
    path('order/pending', PendingOrderListView.as_view() , name='pending_orders'),
    path('order/processing', ProccesingOrderListView.as_view() , name='processing_orders'),
    path('order/completed', CompletedOrderListView.as_view() , name='completed_orders'),

    path('order/<str:pk>/update/', views.update_order, name="update_order"),
    path('order/<str:pk>/delete/', views.delete_order, name="delete_order"),

    path('submit_order/', views.submit_wire_info, name='submit_form'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('submit_order/last_entry/', views.render_entries, name='wire_requests'),
    path('submit_order/wire_requests/<int:pk>/', render_entry_view.as_view(), name='entry'),
    path('submit_order/wire_requests/<int:pk>/resubmit/', CloneView.as_view(), name='clone'),
    path('resubmit_order/', views.submit_cloned_wire_info, name='submit_cloned_form'),


    path('templates/', views.get_form_templates,name='template-list'),
    path('templates/create_template', views.create_template, name="create_template"),
    path('templates/<str:pk>/update/', views.update_template, name="update_template"),
    path('templates/<str:pk>/delete/', views.delete_template, name="delete_template"),
    path('templates/<int:pk>/submit?/', TemplateView.as_view(), name='submit_template'),

    path('recurrence/', views.get_reccurent_list, name='recurrence-list'),
    path('recurrence/<str:pk>/update/', views.update_recurrence, name="update_recurrence"),
    path('jsi18n/recurrence/',JavaScriptCatalog.as_view(packages=['recurrence']),name='javascript-catalog'),
    path('jsi18n.js', JavaScriptCatalog.as_view(packages=['recurrence']), name='jsi18n'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
