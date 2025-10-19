# Trending Movies Map Feature

This feature adds a map to your moviesstore app showing trending movies near you.

## How it works
- Admins (or scripts) create `MovieLocation` objects for each trending spot (cinema, city, etc.)
- Each location is tied to a `Movie` and has latitude, longitude, and a `trend_score`
- The `/movies/map/` page displays a Leaflet map with markers for all trending locations
- The map fetches data from `/movies/locations-geojson/` (GeoJSON format)

## How to add locations
- Use the Django admin or shell to create `MovieLocation` objects
- Example (in Django shell):

```python
from movies.models import Movie, MovieLocation
m = Movie.objects.first()
MovieLocation.objects.create(movie=m, name='Cinema', latitude=51.5, longitude=-0.1, trend_score=10, place='London')
```

## Customization ideas
- Filter by user location (use browser geolocation and pass to API)
- Show only top N trending movies
- Add analytics to update `trend_score` automatically
- Style markers by trend score or movie genre

## Requirements
- Python package: `pymysql` (already installed)
- No other dependencies needed; Leaflet is loaded from CDN

## Troubleshooting
- If you see no markers, make sure you have at least one `MovieLocation` in the database
- If you use MySQL, ensure your DB is running and credentials are correct

---

Enjoy your new trending movies map!
