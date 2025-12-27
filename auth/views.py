from typing import Any

from django.middleware.csrf import get_token
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .services.auth_service import get_auth_service


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        self.auth_service.validate_login_data(username, password)

        ip_address = self.auth_service.get_client_ip(request)

        self.auth_service.check_account_lockout(username, ip_address)

        login_result = self.auth_service.perform_login(request, username, password)

        if login_result['success']:
            self.auth_service.reset_failed_attempts(username, ip_address)
            user_data = UserSerializer(login_result['user'], context={'request': request}).data

            return Response({
                'success': True,
                'message': login_result['message'],
                'user': user_data
            })
        else:
            self.auth_service.handle_failed_login(username, ip_address)


class LogoutView(APIView):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def post(self, request):
        result = self.auth_service.perform_logout(request)
        return Response({
            'success': True,
            'message': result['message']
        })


class SessionCheckView(APIView):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def get(self, request):
        if request.user.is_authenticated:
            user_data = UserSerializer(request.user, context={'request': request}).data
            return Response({
                'authenticated': True,
                'user': user_data
            })
        else:
            return Response({
                'authenticated': False
            })


class GetCSRFTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def get(self, request):
        token = get_token(request)
        response = Response({
            'csrfToken': token
        })
        response.set_cookie(
            'csrftoken',
            token,
            max_age=31449600,
            httponly=False,
            samesite='Lax'
        )
        return response


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        self.auth_service.validate_registration_data(username, password, email)

        user = self.auth_service.create_user(username, password, email, first_name, last_name)

        self.auth_service.perform_registration_login(request, user)

        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'message': 'Registration successful.',
            'user': user_data
        }, status=status.HTTP_201_CREATED)


class SendAlertEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def post(self, request):
        email_data = self.auth_service.validate_alert_email_data(request.data)

        self.auth_service.send_alert_email_notification(
            email_data['user_email'],
            email_data['crypto'],
            email_data['symbol'],
            email_data['condition'],
            email_data['target_price'],
            email_data['current_price']
        )

        return Response({
            'message': 'Email sent successfully',
            'success': True
        })


class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def post(self, request):
        avatar_file = self.auth_service.validate_avatar_upload(request)

        profile = self.auth_service.upload_user_avatar(request.user, avatar_file)

        return Response(
            {"avatar_url": request.build_absolute_uri(profile.avatar.url)},
            status=status.HTTP_200_OK
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = get_auth_service()

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        """Update user profile (email, first_name, last_name)"""
        self.auth_service.validate_user_update_data(request.user, request.data)

        updated_user = self.auth_service.update_user_profile(request.user, request.data)

        serializer = UserSerializer(updated_user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
