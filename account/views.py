# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.decorators import action
# from django.contrib.auth import login, update_session_auth_hash
# from django.core.exceptions import ValidationError
# from django.contrib.auth.forms import PasswordChangeForm
# from .models import Profile
# from rest_framework import serializers
# from django.contrib.auth.models import User
#
# from .serializers import UserLoginSerializer, ProfileSerializer
#
#
# class UserLoginView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         """Process user login"""
#         serializer = UserLoginSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             remember_me = serializer.validated_data['remember_me']
#             login(request, user)
#             if not remember_me:
#                 request.session.set_expiry(0)
#             return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ProfileViewSet(UserLoginView.ViewSet):
#     permission_classes = [IsAuthenticated]
#
#     def retrieve(self, request):
#         """Display user profile information"""
#         try:
#             profile = Profile.objects.select_related('user').get(user=request.user)
#             serializer = ProfileSerializer(profile)
#             return Response(serializer.data)
#         except Profile.DoesNotExist:
#             return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": "Error displaying profile."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     @action(detail=False, methods=['get', 'post'], url_path='edit')
#     def edit(self, request):
#         """Edit user profile"""
#         try:
#             profile = Profile.objects.select_related('user').get(user=request.user)
#             if request.method == 'GET':
#                 user_serializer = UserUpdateSerializer(request.user)
#                 profile_serializer = ProfileUpdateSerializer(profile)
#                 return Response({
#                     'user': user_serializer.data,
#                     'profile': profile_serializer.data
#                 })
#
#             elif request.method == 'POST':
#                 user_serializer = UserUpdateSerializer(request.user, data=request.data.get('user', {}))
#                 profile_serializer = ProfileUpdateSerializer(profile, data=request.data.get('profile', {}))
#
#                 is_valid = user_serializer.is_valid() and profile_serializer.is_valid()
#                 if is_valid:
#                     try:
#                         user_serializer.save()
#                         profile_serializer.save()
#                         return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
#                     except ValidationError as e:
#                         return Response({"error": f"Validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#                     except Exception as e:
#                         return Response({"error": "Error saving information."},
#                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#                 else:
#                     errors = {
#                         'user_errors': user_serializer.errors,
#                         'profile_errors': profile_serializer.errors
#                     }
#                     return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
#
#         except Profile.DoesNotExist:
#             return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": "Error processing request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# class UserSignupView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         """Process user signup"""
#         serializer = UserCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserLoginView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         """Process user login"""
#         serializer = UserLoginSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             remember_me = serializer.validated_data['remember_me']
#             login(request, user)
#             if not remember_me:
#                 request.session.set_expiry(0)
#             return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class PasswordChangeView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         """Process password change"""
#         serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             form = PasswordChangeForm(user=request.user, data=serializer.validated_data)
#             user = form.save()
#             update_session_auth_hash(request, user)
#             return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)