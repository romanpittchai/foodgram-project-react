from rest_framework import routers

from django.urls import include, path

from api.v1.views import (
    UserViewSet, SelfUserView,
    ChangePasswordView, TagViewSet,
    IngredientViewSet, RecipeViewSet,
)

app_name = 'api'

router_for_v1 = routers.DefaultRouter()
router_for_v1.register('users', UserViewSet, basename='users')
router_for_v1.register('tags', TagViewSet, basename='tags')
router_for_v1.register(
    'ingredients', IngredientViewSet,
    basename='ingredients'
)
router_for_v1.register(
    'recipes', RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('', include(router_for_v1.urls)),
    path(
        'users/me/', SelfUserView.as_view(),
        name='self_user'
    ),
    path(
        'users/set_password/',
        ChangePasswordView.as_view(),
        name='set_password'
    ),
    path(
        'auth/', include('djoser.urls.authtoken'),
        name='token'
    )
]
