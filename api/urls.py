from django.urls import path, re_path
from .views import (
    CustomTokenObtainPairView,
    register_view,
    profile_view,
    frontend,
    frontend_page,
    logout_view,
    financial_services_list,
    financial_service_detail,
    advisory_applications_list,
    advisory_application_detail,
    user_all_applications,
    admin_all_applications,
    change_password,
    reset_user_password,
    forgot_password,

)

urlpatterns = [
    # Authentication Endpoints
    path('api/register/', register_view, name='register'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/profile/', profile_view, name='profile'),
    path('api/logout/', logout_view, name='logout'),

    # Financial Services Endpoints
    path('api/financial-services/', financial_services_list,
         name='financial-services-list'),
    path('api/financial-services/<int:pk>/',
         financial_service_detail, name='financial-service-detail'),

    # Advisory Application Endpoints
    path('api/advisory-applications/', advisory_applications_list,
         name='advisory-applications-list'),
    path('api/advisory-applications/<int:pk>/',
         advisory_application_detail, name='advisory-application-detail'),
    path('api/user-applications/', user_all_applications,
         name='user-all-applications'),
    path('api/admin-applications/', admin_all_applications,
         name='admin-all-applications'),

    # Password Management Endpoints
    path('api/change-password/', change_password, name='change-password'),
    path('api/reset-user-password/', reset_user_password,
         name='reset-user-password'),
    path('api/forgot-password/', forgot_password, name='forgot-password'),

    # Frontend Serving
    path('', frontend, name='frontend'),
    re_path(r'^(?P<page>[\w\-/]+?)(?:\.html)?/?$',
            frontend_page, name='frontend_page'),
    re_path(r'^(?P<page>.+)/?$', frontend_page),


]
