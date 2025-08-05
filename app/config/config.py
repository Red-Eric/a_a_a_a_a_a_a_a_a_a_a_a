from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

FRONTEND_URL = os.getenv("FRONTEND_URL")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["app.models.client", 
                       "app.models.personnel",
                       "app.models.etablissement", 
                       "app.models.superAdmin",
                       "app.models.chambre",
                       "app.models.commande_plat",
                       "aerich.models",
                       "app.models.reservation",
                       "app.models.plat",
                       "app.models.avis",
                       "app.models.verify_code",
                       "app.models.paiement_reservation",
                       "app.models.paiement_plat",
                       "app.models.planningEvent",
                       "app.models.conge",
                       "app.models.rapport",
                       "app.models.table",
                       "app.models.favoris",
                       "app.models.mouvement_stock",
                       "app.models.product"
                       ],
            "default_connection": "default",
        }
    },
}
