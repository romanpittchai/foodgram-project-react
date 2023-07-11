from django.shortcuts import get_object_or_404
from django_filters import rest_framework as rf_filters
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, viewsets, views, filters
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.models import User, Follow
from ..filters import IngredientFilter, RecipeFilter
from ..permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrReadOnly,
    IsAuthorOrAdmin,
)  
from .serializers import (
    ChangePasswordSerializer,
    RegistrationSerializer,
    CustUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeLightSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import Recipe, RecipeAndIngredient, Tag, Ingredient, FavoriteRecipe, ShoppingList
from utils.constants import (
    HEADER_FONT_SIZE, BODY_FONT_SIZE, HEADER_LEFT_MARGIN,
    BODY_LEFT_MARGIN, HEADER_HEIGHT, BODY_FIRST_LINE_HEIGHT,
    LINE_SPACING, BOTTOM_MARGIN, BULLET_POINT_SYMBOL
)

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для класса User."""
    queryset = User.objects.all()
    serializer_class = CustUserSerializer
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
        return CustUserSerializer

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
        permission_classes=[permissions.AllowAny],
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

    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustUserSerializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class SelfUserView(GenericAPIView):
    """Класс просмотра для отображения текущего пользователя."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['user'] = self.request.user
        return context

    def get(self, request):
        serializer = CustUserSerializer(
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(GenericAPIView):
    """Для изменения пароля текущего пользователя."""
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context=self.get_serializer_context()
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
    filter_backends = [rf_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ['name', 'author__username']
    ordering_fields = ['name', 'pub_date']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def create_delete_or_scold(self, model, recipe, request):
        instance = model.objects.filter(recipe=recipe, user=request.user)
        name = model.__name__
        if request.method == 'DELETE':
            if not instance.exists():
                content = {
                    'errors': f'Этого рецепта нет в вашем списке.'
                }
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if instance.exists():
            content = {
                'errors': f'Этот рецепт уже был в вашем списке.'
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
        permission_classes=[
            permissions.IsAuthenticated
        ]
    )
    def download_shopping_cart(self, request):
        recipes_ingredients = RecipeIngredients.objects.filter(
            recipe__shopping__user=request.user
        ).order_by('ingredient')
        cart = recipes_ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total=Sum('amount'))

        shopping_list: list = []
        for ingredient in cart:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            line = f"{BULLET_POINT_SYMBOL} {name} - {total} {unit}"
            recipes = recipes_ingredients.filter(ingredient__name=name)
            recipes_names = [
                (item.recipe.name, item.amount) for item in recipes
            ]
            shopping_list.append((line, recipes_names))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping.pdf"'
        paper_sheet = canvas.Canvas(response, pagesize=A4)
        registerFont(TTFont('FreeSans', 'FreeSans.ttf'))

        paper_sheet.setFont('FreeSans', HEADER_FONT_SIZE)
        paper_sheet.drawString(
            HEADER_LEFT_MARGIN, HEADER_HEIGHT, 'Список покупок'
        )

        paper_sheet.setFont('FreeSans', BODY_FONT_SIZE)
        y_coordinate = BODY_FIRST_LINE_HEIGHT
        for ingredient, recipes_names in shopping_list:
            paper_sheet.drawString(BODY_LEFT_MARGIN, y_coordinate, ingredient)
            y_coordinate -= LINE_SPACING

            for recipe_name in recipes_names:
                if y_coordinate <= BOTTOM_MARGIN:
                    paper_sheet.showPage()
                    y_coordinate = BODY_FIRST_LINE_HEIGHT
                    paper_sheet.setFont('FreeSans', BODY_FONT_SIZE)
                recipe_line = f"  {recipe_name[0]} ({recipe_name[1]})"
                paper_sheet.drawString(
                    BODY_LEFT_MARGIN, y_coordinate, recipe_line
                )
                y_coordinate -= LINE_SPACING

        paper_sheet.save()
        return response