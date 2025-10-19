from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Petition
from .models import Movie, Review, Petition, Rating
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.serializers import serialize


def petitions_index(request):
    petitions = Petition.objects.all()
    return render(request, 'movies/petitions_index.html', {'petitions': petitions})

@login_required
def petition_create(request):
    if request.method == 'POST':
        petition = Petition()
        petition.movie_name = request.POST['movie_name']
        petition.creator = request.user
        petition.save()
        return redirect('petitions.index')
    else:
        return render(request, 'movies/petitions_create.html')
    
@login_required
def petition_vote(request, id):
    petition = get_object_or_404(Petition, id=id)
    petition.yes_votes += 1
    petition.save()
    return redirect('petitions.index')

def index(request):
    movies_in_stock = Movie.objects.filter(
        Q(amount_left__gt=0) | Q(amount_left__isnull=True)
    )

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies_in_stock

    return render(request, 'movies/index.html', {'template_data': template_data})

template_data = {} 
template_data['title'] = 'Movies'


movies = Movie.objects.all()
template_data['movies'] = movies 

@login_required
def purchase_movie(request, id):
    movie = get_object_or_404(Movie, id=id)

    if movie.amount_left is None or movie.amount_left > 0:
        movie.purchase()

    return redirect('movies.show', id=movie.id)

def show(request, id):
     movie = Movie.objects.get(id=id)
     reviews = Review.objects.filter(movie=movie)

     template_data = {}
     template_data['title'] = movie.name
     template_data['movie'] = movie
     template_data['reviews'] = reviews
     return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
   if request.method == 'POST' and request.POST['comment'] != '':
    movie = Movie.objects.get(id=id)
    review = Review()
    review.comment = request.POST['comment']
    review.movie = movie
    review.user = request.user
    review.save()
    return redirect('movies.show', id=id)
   else:
    return redirect('movies.show', id=id)
   
@login_required
def edit_review(request, id, review_id):
  review = get_object_or_404(Review, id=review_id)
  if request.user != review.user:
    return redirect('movies.show', id=id)
  if request.method == 'GET':
    template_data = {}
    template_data['title'] = 'Edit Review'
    template_data['review'] = review
    return render(request, 'movies/edit_review.html', {'template_data': template_data})
  elif request.method == 'POST' and request.POST['comment'] != '':
    review = Review.objects.get(id=review_id)
    review.comment = request.POST['comment']
    review.save()
    return redirect('movies.show', id=id)
  else:
    return redirect('movies.show', id=id)
  
@login_required
def delete_review(request, id, review_id):
 review = get_object_or_404(Review, id=review_id,
     user=request.user)
 review.delete()
 return redirect('movies.show', id=id)

@login_required
def rate_movie(request, id):
   movie = get_object_or_404(Movie, id=id)
   if request.method == 'POST':
      value = int(request.POST.get('rating', 0))
      if 1 <= value <= 5:
         rating, created = Rating.objects.update_or_create(
            movie=movie, user=request.user,
            defaults={'value': value}
         )
   return redirect('movies.show', id=movie.id)

def show(request, id):
     movie = Movie.objects.get(id=id)
     reviews = Review.objects.filter(movie=movie)
     ratings = Rating.objects.filter(movie=movie)
     
     avg_rating = ratings.aggregate(models.Avg('value'))['value__avg'] or 0
     user_rating = None
     if request.user.is_authenticated:
        user_rating = Rating.objects.filter(movie=movie, user=request.user).first()

     template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'user_rating': user_rating,
    }   
     return render(request, 'movies/show.html', {'template_data': template_data})


@require_GET
def locations_geojson(request):
    """
    Return US MovieLocation objects as GeoJSON, and top trending movies per region.

    Query params:
      region (optional) - filter by region (place)
      min_score (optional) - filter by minimum trend_score
    """
    from .models import MovieLocation
    # US bounding box
    US_LAT_MIN, US_LAT_MAX = 24.5, 49.5
    US_LON_MIN, US_LON_MAX = -125, -66

    qs = MovieLocation.objects.filter(latitude__gte=US_LAT_MIN, latitude__lte=US_LAT_MAX, longitude__gte=US_LON_MIN, longitude__lte=US_LON_MAX)
    region = request.GET.get('region')
    if region:
        qs = qs.filter(place__icontains=region)
    min_score = request.GET.get('min_score')
    if min_score is not None:
        try:
            ms = int(min_score)
            qs = qs.filter(trend_score__gte=ms)
        except ValueError:
            pass

    features = []
    region_movies = {}
    for loc in qs:
        features.append({
            'type': 'Feature',
            'properties': {
                'id': loc.id,
                'movie_id': loc.movie_id,
                'movie_name': loc.movie.name,
                'name': loc.name,
                'place': loc.place,
                'trend_score': loc.trend_score,
                'purchase_count': loc.purchase_count,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [loc.longitude, loc.latitude],
            }
        })
        # Aggregate top movies per region
        region_key = loc.place or 'Unknown'
        if region_key not in region_movies:
            region_movies[region_key] = {}
        region_movies[region_key][loc.movie.name] = region_movies[region_key].get(loc.movie.name, 0) + loc.purchase_count

    # For each region, get top 3 movies by purchase_count
    top_movies_by_region = {}
    for region, movies in region_movies.items():
        sorted_movies = sorted(movies.items(), key=lambda x: x[1], reverse=True)
        top_movies_by_region[region] = [{'movie': m, 'purchase_count': c} for m, c in sorted_movies[:3]]

    return JsonResponse({'type': 'FeatureCollection', 'features': features, 'top_movies_by_region': top_movies_by_region})


def map_view(request):
    """Render a page with an interactive map (Leaflet) that fetches /locations-geojson."""
    return render(request, 'movies/map.html')