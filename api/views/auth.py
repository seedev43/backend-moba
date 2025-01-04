from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from ..models import UserRating
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import h5py
import pickle
import os


@csrf_exempt
def register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            # password_again = data.get('password_again')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'email already exists'}, status=400)

            # if password != password_again:
                # return JsonResponse({'success': False, 'message': 'password do not match'}, status=400)
            
            user = User.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                username=username, 
                password=password
            )
            return JsonResponse({'success': True, 'message': 'user created successfully'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def login_view(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'id': user.id, 'username': user.username, 'message':'Login successful'}, status=200)
            
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def logout_view(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logout successful'}, status=200)
    

@csrf_exempt
def user_detail_view(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


