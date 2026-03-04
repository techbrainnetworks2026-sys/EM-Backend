from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer, UserProfileUpdateSerializer
from .permissions import IsManager
from django.shortcuts import get_object_or_404
from notifications.models import Notification

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

class CustomAuthToken(ObtainAuthToken):
    serializer_class = LoginSerializer # Use our custom serializer that checks email
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if not user.is_approved:
            if user.is_rejected:
                return Response({
                    'error': 'Account was rejected by manager.'
                }, status=status.HTTP_403_FORBIDDEN)
            return Response({
                'error': 'Account not approved by manager yet.'
            }, status=status.HTTP_403_FORBIDDEN)
            
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'massage': 'Login successful',
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'role': user.role,
            'is_approved': user.is_approved
        })

class PendingUsersView(generics.ListAPIView):
    """
    List all Key employees who are not approved yet.
    Only Managers can see this.
    """
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        # Return users who are employees and NOT approved.
        # This includes new requests (is_rejected=False) and previously rejected ones (is_rejected=True).
        # Put new requests at the top, rejected at the bottom using ordering.
        return User.objects.filter(
            role=User.EMPLOYEE, 
            is_approved=False
        ).order_by('is_rejected', '-date_joined')

# class ApproveUserView(APIView):
#     """
#     Approve a specific user.
#     Only Managers can do this.
#     """
#     permission_classes = [IsManager]

#     def post(self, request, pk):
#         try:
#             user = User.objects.get(pk=pk, role=User.EMPLOYEE)
#             user.is_approved = True
#             user.save()
#             return Response({"message": f"User {user.username} approved successfully."})
#         except User.DoesNotExist:
#             return Response({"error": "User not found or not an employee."}, status=status.HTTP_404_NOT_FOUND)



class ApproveUserView(APIView):
    """
    Manager approves an employee account
    """
    permission_classes = [IsManager]

    def post(self, request, pk):

        user = get_object_or_404(User, pk=pk, role=User.EMPLOYEE)

        if user.is_approved:
            return Response(
                {"message": "User already approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_approved = True
        user.is_rejected = False # Ensure rejected status is cleared if approving
        user.save(update_fields=["is_approved", "is_rejected"])

        # Create Notification for the employee
        Notification.objects.create(
            user=user,
            title="🎉 Account Approved",
            message=f"Your account has been approved by the manager. You can now access all features.",
            notification_type='account_update'
        )

        return Response(
            {"message": f"{user.username} approved successfully."},
            status=status.HTTP_200_OK
        )

class RejectUserView(APIView):
    """
    Manager rejects an employee account
    """
    permission_classes = [IsManager]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=User.EMPLOYEE)

        if user.is_approved:
            return Response(
                {"message": "Cannot reject an already approved user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_approved = False
        user.is_rejected = True
        user.save(update_fields=["is_approved", "is_rejected"])

        # Create Notification for the employee
        Notification.objects.create(
            user=user,
            title="⚠️ Account Rejected",
            message=f"Your account request has been rejected by the manager. Please contact support for more information.",
            notification_type='account_update'
        )

        return Response(
            {"message": f"{user.username} rejected successfully."},
            status=status.HTTP_200_OK
        )
    
class ApprovedUsersView(generics.ListAPIView):
    """
    List all approved employees.
    Only managers can see this.
    """
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return User.objects.filter(
            role=User.EMPLOYEE,
            is_approved=True
        )
    
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    """
    Update user profile including profile picture.
    Both managers and employees can update their own profile.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profile updated successfully',
                    'user': UserSerializer(request.user, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profile updated successfully',
                    'user': UserSerializer(request.user, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

# ... existing code ...

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate 6 digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Cache OTP for 5 minutes (300 seconds)
        try:
            cache.set(f'otp_{email}', otp, timeout=300)
        except Exception as e:
             # If cache fails (e.g. redis not running), we might fallback or log. For dev we proceed.
             pass
        
        # Send Email
        try:
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}. It is valid for 5 minutes.',
                settings.EMAIL_HOST_USER, # Sender
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        cached_otp = cache.get(f'otp_{email}')
        
        if cached_otp and str(cached_otp) == str(otp):
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not email or not new_password or not confirm_password:
             return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear OTP after successful reset
            cache.delete(f'otp_{email}')
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
