from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Petition
from .models import Movie, Review, Petition, Rating
from django.db import models
from .models import MovieLocation
import json
import pkgutil
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.db.models import Sum


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

@login_required
def map_view(request):
    locations = MovieLocation.objects.select_related('movie').all()
    data = [
        {
            'movie': loc.movie.name,
            'lat': loc.latitude,
            'lng': loc.longitude,
            'trend': loc.trend_score,
            'place': loc.place or loc.name or "Unknown",
            'region_id': loc.id,
        }
        for loc in locations
    ]

    regions = {}
    try:
        data_bytes = pkgutil.get_data('movies', 'static/movies/regions.geojson')
        if data_bytes:
            regions = json.loads(data_bytes.decode())
    except Exception:
        regions = {}

    return render(request, 'movies/map.html', {
        'data_json': json.dumps(data),
        'regions_geojson': json.dumps(regions),
    })


def locations_geojson(request):
    locations = MovieLocation.objects.select_related('movie').all()
    features = []
    for loc in locations:
        features.append({
           "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [loc.longitude, loc.latitude]},
            "properties": {
                "id": loc.id,
               "movie_name": loc.movie.name,
                "name": loc.name,
                "place": loc.place,
                "trend_score": loc.trend_score,
                "purchase_count": getattr(loc, "purchase_count", 0)
            }
        })
    # Build a simple "top movies by region" structure for the sidebar
    top = {}
    for loc in locations:
       region = loc.place or 'Unknown'
       top.setdefault(region, {})
       movie_name = loc.movie.name
       top[region][movie_name] = max(top[region].get(movie_name, 0), getattr(loc, "purchase_count", 0))

    top_movies_by_region = {
        region: [{"movie": m, "purchase_count": cnt} for m, cnt in sorted(mdict.items(), key=lambda x: -x[1])[:5]]
        for region, mdict in top.items()
    }

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features,
        "top_movies_by_region": top_movies_by_region
   })


@login_required
def region_top(request, region_id):
    """
    Return JSON top movies for the clicked MovieLocation (aggregated by place).
    Falls back to the clicked location's movie if no aggregation results.
    """
    if request.method != "GET":
        return HttpResponseForbidden()

    # ensure we use the real MovieLocation model
    loc = get_object_or_404(MovieLocation, pk=region_id)
    place = loc.place or loc.name

    # aggregate purchase_count by movie name for the same place
    qs = (
        MovieLocation.objects.filter(place=place)
        .values("movie__name")
        .annotate(total_purchases=Sum("purchase_count"))
        .order_by("-total_purchases")[:10]
    )

    top = [{"title": x["movie__name"], "count": x["total_purchases"] or 0} for x in qs]

    # fallback to the clicked location's movie if nothing aggregated
    if not top:
        top = [{"title": getattr(loc.movie, "name", "Unknown"), "count": getattr(loc, "purchase_count", 0) or 0}]

    return JsonResponse({"top": top})

try:
    from .models import Purchase  # optional model in your app
except Exception:
    Purchase = None

@login_required
def my_purchases(request):
    """
    Return the logged-in user's recent purchases as JSON:
    { "purchases": [{"movie": "Inception", "count": 3}, ...] }
    Falls back to Review-based counts if Purchase model isn't available.
    """
    purchases = []
    try:
        from .models import Purchase
    except Exception:
        Purchase = None
    if Purchase is not None:
        qs = (
            Purchase.objects.filter(user=request.user)
            .values("movie__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:50]
        )
        purchases = [{"movie": x["movie__name"], "count": x["count"]} for x in qs]
    else:
        # Fallback: use Review counts as a proxy for recent activity
        try:
            from .models import Review
            qs = (
                Review.objects.filter(user=request.user)
                .values("movie__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:50]
            )
            purchases = [{"movie": x["movie__name"], "count": x["count"]} for x in qs]
        except Exception:
            purchases = []

        Purchase.objects.create(user=request.user, movie=Movie)
        loc = MovieLocation.objects.filter(movie=Movie).first()
        if loc:
            loc.purchase_count = Purchase.objects.filter(movie=Movie).count()
            loc.save()

        from .models import MovieLocation
        try:
            loc = MovieLocation.objects.filter(movie=Movie).first()
            if loc:
                loc.purchase_count = (loc.purchase_count or 0) + 1
                loc.save()
        except Exception as e:
            print("Error updating location purchase count:", e)

    return JsonResponse({"purchases": purchases})