from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color')
    search_fields = ('name', 'color',)
    list_filter = ('name',)


admin.site.register(Tag, TagAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)


class IngredientsInline(admin.TabularInline):
    model = Ingredient.recipes.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'is_favorited')
    readonly_fields = ('is_favorited',)
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def is_favorited(self, obj):
        return obj.favorites.count()
    is_favorited.short_description = 'Добавлений в Избранное'

    inlines = [
        IngredientsInline,
    ]


admin.site.register(Recipe, RecipeAdmin)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient',)
    list_filter = ('recipe', 'ingredient')


admin.site.register(RecipeIngredient, RecipeIngredientAdmin)


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'tag')
    search_fields = ('recipe', 'tag',)
    list_filter = ('recipe', 'tag')


admin.site.register(RecipeTag, RecipeTagAdmin)
