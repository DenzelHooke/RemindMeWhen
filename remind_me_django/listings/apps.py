from django.apps import AppConfig

class ListingsConfig(AppConfig):
    """ 
    Automatically runs scrapyd in DEV when the run server command is ran.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'
