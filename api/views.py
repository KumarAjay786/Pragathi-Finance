from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
import os
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required  # Add this import
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .models import CustomUser, FinancialServices, AdvisoryApplication
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserRegisterSerializer,
    FinancialServicesSerializer,
    AdvisoryApplicationSerializer,
    ChangePasswordSerializer,
    ResetUserPasswordSerializer
)

# Authentication Views


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            # Always set role to 'admin' for superusers
            role = 'admin' if getattr(
                user, 'is_superuser', False) else user.role
            return Response({
                "message": "User created successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": role
            }, status=status.HTTP_201_CREATED)
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    # Always set role to 'admin' for superusers
    role = 'admin' if getattr(
        request.user, 'is_superuser', False) else request.user.role
    return Response({**serializer.data, "role": role})


@api_view(['POST'])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# Financial Services Views (updated)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def financial_services_list(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        services = FinancialServices.objects.filter(user=request.user)
        serializer = FinancialServicesSerializer(services, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = {
            'company_name': request.data.get('company_name'),
            'legal_status': request.data.get('legal_status'),
            'contact_person': request.data.get('contact_person'),
            'email': request.data.get('email'),
            'mobile': request.data.get('mobile'),
            'city': request.data.get('city'),
            'country': request.data.get('country'),
            'nature_of_business': request.data.get('nature_of_business'),
            'net_worth': request.data.get('net_worth'),
            'last_turnover': request.data.get('last_turnover'),
            'current_loan_liability': request.data.get('current_loan_liability'),
            'last_it_paid': request.data.get('last_it_paid'),
            'fund_looking_for': request.data.get('fund_looking_for'),
            'purpose_of_funding': request.data.get('purpose_of_funding'),
            'nature_of_funding': request.data.get('nature_of_funding'),
            'offered_roi': request.data.get('offered_roi'),
        }
        serializer = FinancialServicesSerializer(data=data)
        if serializer.is_valid():
            if request.user.is_authenticated:
                serializer.save(user=request.user)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def financial_service_detail(request, pk):
    service = get_object_or_404(FinancialServices, pk=pk)

    if request.method == 'GET':
        serializer = FinancialServicesSerializer(service)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FinancialServicesSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Advisory Application Views

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def advisory_applications_list(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Show only applications of the logged in user
        apps = AdvisoryApplication.objects.filter(user=request.user)
        serializer = AdvisoryApplicationSerializer(apps, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = {
            'name': request.data.get('name'),
            'gender': request.data.get('gender'),
            'dob': request.data.get('dob'),
            'email': request.data.get('email'),
            'mobile': request.data.get('mobile'),
            'address': request.data.get('address'),
            'interest_invest': request.data.get('interest_invest'),
            'interest': request.data.get('interest'),
            'range_investment': request.data.get('range_investment'),
            'expected_roi': request.data.get('expected_roi'),
            'duration': request.data.get('duration'),
        }
        serializer = AdvisoryApplicationSerializer(data=data)
        if serializer.is_valid():
            if request.user.is_authenticated:
                serializer.save(user=request.user)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def advisory_application_detail(request, pk):
    # User can access only their own applications
    application = get_object_or_404(
        AdvisoryApplication, pk=pk, user=request.user)

    if request.method == 'GET':
        serializer = AdvisoryApplicationSerializer(application)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AdvisoryApplicationSerializer(
            application, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_all_applications(request):
    user_email = request.user.email
    advisory_apps = AdvisoryApplication.objects.filter(email=user_email)
    financial_services = FinancialServices.objects.filter(email=user_email)

    advisory_serializer = AdvisoryApplicationSerializer(
        advisory_apps, many=True)
    financial_serializer = FinancialServicesSerializer(
        financial_services, many=True)

    return Response({
        'advisory_applications': advisory_serializer.data,
        'financial_services': financial_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_all_applications(request):
    app_type = request.GET.get('type')  # ?type=advisory or ?type=financial

    if app_type == 'advisory':
        advisory_apps = AdvisoryApplication.objects.all()
        advisory_serializer = AdvisoryApplicationSerializer(
            advisory_apps, many=True)
        return Response({'advisory_applications': advisory_serializer.data})

    elif app_type == 'financial':
        financial_apps = FinancialServices.objects.all()
        financial_serializer = FinancialServicesSerializer(
            financial_apps, many=True)
        return Response({'financial_services': financial_serializer.data})

    else:
        advisory_apps = AdvisoryApplication.objects.all()
        financial_apps = FinancialServices.objects.all()
        advisory_serializer = AdvisoryApplicationSerializer(
            advisory_apps, many=True)
        financial_serializer = FinancialServicesSerializer(
            financial_apps, many=True)
        return Response({
            'advisory_applications': advisory_serializer.data,
            'financial_services': financial_serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=400)
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'success': True, 'message': 'Password changed successfully'})
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reset_user_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=400)

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    new_password = get_random_string(12)
    user.set_password(new_password)
    user.save()

    subject = "Your Password Has Been Reset"
    message = f"""
    Dear {user.name},\n\nYour password has been reset by the administrator.\n\nYour new login credentials are:\nEmail: {user.email}\nPassword: {new_password}\n\nPlease log in and change your password immediately for security reasons.\n\nBest Regards,\nPragathi Finance Solutions
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response({'success': True, 'message': "Password has been reset and sent to user's email"})


@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'success': False, 'error': 'Email is required.'}, status=400)
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'No user found with this email.'}, status=404)
    new_password = get_random_string(12)
    user.set_password(new_password)
    user.save()
    subject = "Password Reset Request"
    message = f"""
    Dear {user.name or user.email},\n\nYour password has been reset.\n\nYour new login credentials are:\nEmail: {user.email}\nPassword: {new_password}\n\nPlease log in and change your password immediately for security reasons.\n\nBest Regards,\nPragathi Finance Solutions
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return Response({'success': True, 'message': 'Password reset instructions sent to your email.'})


# Frontend Views

def frontend(request):
    return render(request, 'index.html')


def frontend_page(request, page):
    safe_page = os.path.basename(page)
    # Only allow alphanumeric, dash, and underscore for security
    if not safe_page or not all(c.isalnum() or c in ('-', '_') for c in safe_page.replace('.html', '')):
        raise Http404()
    # Remove .html if user includes it in the URL
    if safe_page.endswith('.html'):
        safe_page = safe_page[:-5]
    # Prevent static file requests (js, css, png, jpg, etc.)
    static_exts = ('.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
                   '.ico', '.map', '.woff', '.woff2', '.ttf', '.eot', '.json')
    if any(safe_page.endswith(ext) for ext in static_exts):
        raise Http404()
    template_name = f"{safe_page}.html"
    return render(request, template_name)
