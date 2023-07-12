import csv
import os
import sys

from django.core.management.base import BaseCommand

from foodgram_backend.settings import STATIC_CSV_JSON_FILES_DIRS
from recipes.models import Ingredient, Tag

DICT_FILE = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


def open_csv_file(csv_file):
    """Для открытия, прочитывания csv-файлов."""
    file_path = os.path.join(STATIC_CSV_JSON_FILES_DIRS, csv_file)
    try:
        with open(file_path, newline='', encoding='utf-8') as open_csv_file:
            return list(csv.DictReader(open_csv_file, delimiter=','))
    except (FileNotFoundError, IsADirectoryError) as error:
        print(error)
        sys.exit()


def load_to_bd(model, data):
    """Для выгрузки данных в БД."""
    list_data: list = list()
    for data_item in data:
        list_data.append(model(**data_item))
    model.objects.bulk_create(list_data)
    list_data.clear()


class Command(BaseCommand):
    """Для выгрузки данных в БД из csv."""
    help = 'Команда вы выгрузки тестовых данных в БД из .csv.'

    def handle(self, *args, **options):
        for key, value in DICT_FILE.items():
            load_to_bd(key, open_csv_file(value))
