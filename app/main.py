from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import TORTOISE_ORM
from tortoise.contrib.fastapi import register_tortoise

from app.routes.client import route_client
from app.routes.etablissement import route_etablissement
from app.routes.chambre import route_chambre
from app.routes.reservation import route_reservation
from app.routes.plat import route_plat
from app.routes.avis import route_avis
from app.routes.personnel import route_personnel
from app.routes.superAdmin import route_superAdmin
from app.routes.commande_plat import route_commande_plat
from app.routes.auth import route_auth
from app.routes.oauth import route_oauth_social
from app.services.auth_service import AuthService
from app.routes.paiement_reservation import route_paiement_reservation
from app.routes.planning import route_planning
from app.routes.conge import route_conge
from app.routes.rapport import route_rapport
from fastapi.staticfiles import StaticFiles
from app.routes.table import route_table
from app.routes.produit import route_produit

app = FastAPI(
    title="API systeme GHR",
    description="GHR",
    version="1.0.0"
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001","http://localhost:3000", "http://192.168.1.211:3000", "http://192.168.1.211:8080", "http://192.168.1.170:3001", "http://192.168.1.139:3000", "http://192.168.1.131:3000", ],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(route_auth.router, prefix="/api/auth", tags=["Authentification"])

app.include_router(route_oauth_social.router, prefix="/api/auth", tags=["OAuth"])

app.include_router(
    route_superAdmin.router, 
    prefix="/api/superAdmin", 
    tags=["SuperAdmin"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_client.router, 
    prefix="/api/client", 
    tags=["clients"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_etablissement.router, 
    prefix="/api/etablissement", 
    tags=["etablissements"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_produit.router, 
    prefix="/api/produit", 
    tags=["Produits"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_personnel.router, 
    prefix="/api/personnel", 
    tags=["Personnels"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_chambre.router, 
    prefix="/api/chambre", 
    tags=["Chambre"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_reservation.router, 
    prefix="/api/reservation", 
    tags=["Reservation"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_planning.router, 
    prefix="/api/planning", 
    tags=["Plannings"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_rapport.router, 
    prefix="/api/rapport", 
    tags=["Rapports"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)

app.include_router(
    route_conge.router, 
    prefix="/api/conge", 
    tags=["Conges"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_paiement_reservation.router, 
    prefix="/api/paiement-reservation", 
    tags=["Paiements-reservation"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_commande_plat.router, 
    prefix="/api/commande", 
    tags=["Commande Plat"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_table.router, 
    prefix="/api/table", 
    tags=["Tables"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_plat.router, 
    prefix="/api/plat", 
    tags=["Plat"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)
app.include_router(
    route_avis.router, 
    prefix="/api/avis", 
    tags=["Avis"], 
    # dependencies=[Depends(AuthService.get_current_user)]
)


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)
