from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserRating
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import h5py
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cosine_similarity_path = os.path.join(BASE_DIR, 'api/model/cosine_similarity_matrix_compressed.h5')
movie_list_path = os.path.join(BASE_DIR, 'api/model/movie_list.pkl')

with h5py.File(cosine_similarity_path, 'r') as f:
    print("Cosine Similarity Model loaded..")
    cosine_sim_loaded = f['cosine_similarity'][:]
    
movie_list_loaded = pickle.load(open(movie_list_path, 'rb'))

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


@csrf_exempt
def similarity(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            query = data.get('query')
            query = query.lower()
            
            # Cari indeks berdasarkan query
            matching_movies = movie_list_loaded[movie_list_loaded['genres'] == query]
            if matching_movies.empty:
                return JsonResponse({
                    'success': False, 
                    'message': 'No movies found for the given genre query.',
                    'data': []
                }, status=404)
            
            idx = matching_movies.index[0]  # Ambil indeks pertama dari hasil pencarian
            
            # Hitung skor kemiripan
            sim_scores = list(enumerate(cosine_sim_loaded[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:30]  # Ambil 30 film teratas
            movie_indices = [i[0] for i in sim_scores]
            
            # Ambil judul film dan konversi ke list
            recommended_movies = movie_list_loaded.iloc[movie_indices][['id', 'title', 'poster_path', 'genres']]
            recommended_movies_list = recommended_movies.to_dict(orient='records') 
            
            return JsonResponse({
                'success': True, 
                'message': 'success get data with genre similarities', 
                'data': recommended_movies_list
            }, status=200)
            
        else:
            return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def add_rating(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            user_id = data.get("user_id")
            id_movie = data.get("movie_id")
            rating = data.get("rating") 
            genre = data.get("genre")  

            print(data)

            # Validasi input
            # if user_id or id_movie or rating or genre is None:
            #     return JsonResponse({
            #         "success": False,
            #         "message": "user_id, id_movie, rating, and genre are required."
            #     }, status=400)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "User not found."
                }, status=404)

            # Simpan rating ke database
            user_rating, created = UserRating.objects.update_or_create(
                user=user,
                id_movie=id_movie,
                defaults={
                    'rating': rating,
                    'genre':genre
                }
            )
            
            if created:
                return JsonResponse({
                    "success": True,
                    "message": "Rating added successfully.",
                    "data": {
                        "id": user_rating.id,
                        "user": user_rating.user.username,
                        "id_movie": user_rating.id_movie,
                        "rating": user_rating.rating,
                        "genre": user_rating.genre,
                        "created_at": user_rating.created_at
                    }
                }, status=201)
            else:
                return JsonResponse({
                    "success": True,
                    "message": "Rating updated successfully.",
                    "data": {
                        "id": user_rating.id,
                        "user": user_rating.user.username,
                        "id_movie": user_rating.id_movie,
                        "rating": user_rating.rating,
                        "genre": user_rating.genre,
                        "updated_at": user_rating.updated_at
                    }
                }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Method not allowed."}, status=405)
