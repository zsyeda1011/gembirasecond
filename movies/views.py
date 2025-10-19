from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Petition
from .models import Movie, Review, Petition, Rating
from django.db import models


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