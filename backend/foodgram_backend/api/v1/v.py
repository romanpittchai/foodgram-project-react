from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, RecipeAndIngredient, Tag
from users.models import User, Follow
from .serializers import (
    RegistrationSerializer,
    UserSerializer,
    SubscriptionSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для класса User."""

    queryset = User.objects.all()
    serializer_class = someSerialoizer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistrationSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={
                'request': request,
                'view': self
            }
        )
        return self.get_paginated_response(serializer.data)
    
    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def follow(self, request, pk):
        """Подписка на автора."""

        followed = get_object_or_404(User, id=pk)
        follower = request.user
        following = (
            Follow.objects.filter(
                user=follower,
                author=followed,
            ).exists()
        )
        if request.method == 'DELETE':
            if not following:
                content = {'errors': 'У вас не такой подписки'}
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            following.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        if request.method == 'POST':
            if following:
                content = {'errors': 'Вы уже подписаны на данного автора'}
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif followed == follower:
                content = {'errors': 'Нельзя подписаться самого себя'}
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(user=follower, author=followed)
            serializer = SubscriptionSerializer(
                followed,
                context={
                    'request': request,
                    'view': self
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
