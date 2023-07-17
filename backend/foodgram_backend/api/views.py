from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as rf_filters
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Tag)
from users.models import Follow, User
from utils.constants import (BODY_FONT_SIZE, BULLET_INDENT, HEADER_FONT_SIZE,
                             LEFT_INDENT)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdmin, IsAuthorOrReadOnly
from .serializers import (ChangePasswordSerializer, UserSerializer,
                          IngredientSerializer, RecipeLightSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          RegistrationSerializer, SubscriptionSerializer,
                          TagSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для класса User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['user'] = self.request.user
        return context

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
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk):
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
            Follow.objects.filter(user=follower, author=followed).delete()
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
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class SelfUserView(GenericAPIView):
    """Класс просмотра для отображения текущего пользователя."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(GenericAPIView):
    """Для изменения пароля текущего пользователя."""

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            request.user.set_password(serializer.data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Для отображения тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Для отображения ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [rf_filters.DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Для отображения рецепта."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
        IsAuthorOrAdmin,
    ]
    filter_backends = [
        rf_filters.DjangoFilterBackend,
        filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_class = RecipeFilter
    search_fields = ['name', 'author__username']
    ordering_fields = ['name', 'pub_date']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeSerializer

    def create_delete_or_scold(self, model, recipe, request):
        instance = model.objects.filter(recipe=recipe, user=request.user)
        if request.method == 'DELETE':
            if not instance.exists():
                content = {
                    'errors': 'Этого рецепта нет в вашем списке.'
                }
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if instance.exists():
            content = {
                'errors': 'Этот рецепт уже был в вашем списке.'
            }
            return Response(
                content,
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeLightSerializer(
            recipe,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[
            permissions.IsAuthenticated,
        ]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_delete_or_scold(FavoriteRecipe, recipe, request)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[
            permissions.IsAuthenticated
        ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_delete_or_scold(ShoppingList, recipe, request)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_list = (
            RecipeIngredient.objects
            .filter(recipe__shopping_list__user=request.user)
            .order_by('ingredient')
            .prefetch_related('ingredient', 'recipe')
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
                'recipe__name', 'amount'
            )
            .annotate(total=Sum('amount'))
        )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="Ваш_список_покупок.pdf"'
        )

        pdfmetrics.registerFont(TTFont(
            'Xolonium-Regular', 'Xolonium-Regular.ttf'
        ))
        styles = getSampleStyleSheet()
        header_style = styles['Heading1']
        header_style.fontName = 'Xolonium-Regular'
        header_style.fontSize = HEADER_FONT_SIZE
        body_style = styles['BodyText']
        body_style.fontName = 'Xolonium-Regular'
        body_style.fontSize = BODY_FONT_SIZE

        doc = SimpleDocTemplate(response, pagesize=A4)
        bullet_style = ParagraphStyle(
            'Bullet', parent=body_style,
            leftIndent=LEFT_INDENT,
            bulletIndent=BULLET_INDENT,
            fontSize=BODY_FONT_SIZE,
            fontName="Xolonium-Regular",
        )

        story = []

        header_text = 'Ваш список покупок:'
        header = Paragraph(header_text, header_style)
        story.append(header)

        for item in shopping_list:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            total = item['total']
            line = f"• {name} - {total} {unit}"

            line = Paragraph(line, bullet_style)
            story.append(line)

        doc.build(story)
        return response
