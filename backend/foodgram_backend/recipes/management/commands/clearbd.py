from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from users.models import User

MODELS = (User, Ingredient)


class Command(BaseCommand):
    """Для очистики БД."""

    help = 'Для очистки БД.'

    def handle(self, *args, **options):
        for model in MODELS:
            model.objects.all().delete()