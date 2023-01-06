from csv import DictReader

from django.core.management import BaseCommand
# Import the model
from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):
        print("Loading data")

        # Code to load the data into database
        for row in DictReader(open(
            'data/ingredients.csv', encoding="utf-8"
        )):
            if Ingredient.objects.filter(name=row['название']).exists():
                print('data already loaded')
            else:
                ing = Ingredient(
                    name=row['название'],
                    measurement_unit=row['мера измерения']
                )
                ing.save()
