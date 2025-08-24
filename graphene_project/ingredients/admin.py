from django.contrib import admin
# from ingredients.models import Category, Ingredient
from graphene_project.ingredients.models import Category, Ingredient

# Register your models here.
admin.site.register(Category)
admin.site.register(Ingredient)
