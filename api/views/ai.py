from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from ..models import UserRating
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import h5py
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cosine_similarity_path = os.path.join(BASE_DIR, 'model/cosine_similarity_matrix_compressed.h5')
movie_list_path = os.path.join(BASE_DIR, 'model/movie_list.pkl')

with h5py.File(cosine_similarity_path, 'r') as f:
    print("Cosine Similarity Model loaded..")
    cosine_sim_loaded = f['cosine_similarity'][:]
    
movie_list_loaded = pickle.load(open(movie_list_path, 'rb'))


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
            movie_id = data.get("movie_id")
            rating = data.get("rating") 
            genre = data.get("genre")  

            print(data)

            # Validasi input
            # if user_id or movie_id or rating or genre is None:
            #     return JsonResponse({
            #         "success": False,
            #         "message": "user_id, movie_id, rating, and genre are required."
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
                movie_id=movie_id,
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
                        "movie_id": user_rating.movie_id,
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
                        "movie_id": user_rating.movie_id,
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

@csrf_exempt
def get_recommendation_movies(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "User not found."
                }, status=404)

            # Cek apakah pengguna sudah memberikan rating untuk film tertentu
            try:
                user_rating = UserRating.objects.filter(user=user).latest('created_at')

                # Ambil genre dari rating terakhir pengguna
                genre = user_rating.genre.lower()

                # Cari indeks berdasarkan genre
                matching_movies = movie_list_loaded[movie_list_loaded['genres'] == genre]
                if matching_movies.empty:
                    return JsonResponse({
                        'success': False,
                        'message': f'No movies found for the given genre: {genre}.',
                        'data': []
                    }, status=404)

                idx = matching_movies.index[0]  # Ambil indeks pertama dari hasil pencarian
                
                # Hitung skor kemiripan
                sim_scores = list(enumerate(cosine_sim_loaded[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = sim_scores[1:30]  # Ambil 30 film teratas
                movie_indices = [i[0] for i in sim_scores]
                
                # Ambil data film rekomendasi
                recommended_movies = movie_list_loaded.iloc[movie_indices][['id', 'title', 'poster_path', 'genres']]
                recommended_movies_list = recommended_movies.to_dict(orient='records')

                return JsonResponse({
                    "success": True,
                    "message": "Recommendations fetched successfully.",
                    "data": recommended_movies_list
                }, status=200)

            except UserRating.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "User has not rated any movies yet.",
                    "data": []
                }, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            return JsonResponse({
                "success": False,
                "message": str(e),
                "details": error_details
            }, status=500)

    return JsonResponse({"success": False, "message": "Method not allowed."}, status=405)
