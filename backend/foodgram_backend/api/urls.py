from django.urls import include, path
from rest_framework import routers

from .views import (ChangePasswordView, IngredientViewSet, RecipeViewSet,
                    SelfUserView, TagViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register(
    'ingredients', IngredientViewSet,
    basename='ingredients'
)
router.register(
    'recipes', RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path(
        'users/me/', SelfUserView.as_view(),
        name='me'
    ),
    path(
        'users/set_password/',
        ChangePasswordView.as_view(),
        name='set_password'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(
        'auth/', include('djoser.urls.authtoken'),
        name='token'
    )
]
