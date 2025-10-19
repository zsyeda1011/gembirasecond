from django.contrib import admin
from .models import Movie, Review

class MovieAdmin(admin.ModelAdmin):
 ordering = ['name']
 search_fields = ['name']
 list_display = ('name', 'price', 'amount_left')

def get_readonly_fields(self, request, obj=None):
        """
        Make 'amount_left' readonly if the movie exists and amount_left is 0.
        Admins can edit it otherwise.
        """
        if obj and obj.amount_left == 0:
            return self.readonly_fields + ('amount_left',)
        return self.readonly_fields

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)