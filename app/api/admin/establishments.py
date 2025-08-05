from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.models.client import Client
from app.models.reservation import Reservation
from app.models.paiement import Paiement
from app.schemas.etablissementCreate import EtablissementCreate
from tortoise.functions import Sum, Count
from tortoise.expressions import Q
# Import des enums pour référence
from app.enum.etat_chambre import EtatChambre
from app.enum.type_etablissement import Type_etablissement
from app.enum.etablissement_statu import Etablissement_status

router = APIRouter()

@router.get("/establishments")
async def get_all_establishments_admin(
    skip: int = 0,
    limit: int = 100,
    type_: Optional[str] = None,
    ville: Optional[str] = None,
    statut: Optional[str] = None
):
    """Récupérer tous les établissements avec filtres pour le Super Admin"""
    query = Etablissement.all()
    
    if type_:
        query = query.filter(type_=type_)
    if ville:
        query = query.filter(ville=ville)
    if statut:
        query = query.filter(statut=statut)
    
    total = await query.count()
    etablissements = await query.offset(skip).limit(limit)
    
    # Enrichir avec des statistiques
    result = []
    for etab in etablissements:
        nb_chambres = await Chambre.filter(etablissement=etab).count()
        nb_clients = await Client.filter(etablissement=etab).count()
        nb_reservations = await Reservation.filter(etablissement=etab).count()
        
        # Calculer le CA
        # TODO: Décommenter quand la colonne commande_id sera créée dans la base
        # paiements = await Paiement.filter(commande__etablissement=etab)
        # ca = sum(p.montant for p in paiements)
        ca = 0  # Temporaire en attendant la migration
        
        # Calculer le taux d'occupation
        chambres_occupees = await Chambre.filter(
            etablissement=etab, 
            etat=EtatChambre.OCCUPEE
        ).count()
        taux_occupation = (chambres_occupees / nb_chambres * 100) if nb_chambres > 0 else 0
        
        result.append({
            **etab.__dict__,
            "nb_chambres": nb_chambres,
            "nb_clients": nb_clients,
            "nb_reservations": nb_reservations,
            "ca_mensuel": ca,
            "taux_occupation": round(taux_occupation, 2)
        })
    
    return {
        "total": total,
        "etablissements": result,
        "skip": skip,
        "limit": limit
    }

@router.get("/establishments/{establishment_id}")
async def get_establishment_details_admin(establishment_id: int):
    """Récupérer les détails complets d'un établissement pour le Super Admin"""
    etab = await Etablissement.get_or_none(id=establishment_id)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    
    # Statistiques détaillées
    nb_chambres = await Chambre.filter(etablissement=etab).count()
    nb_clients = await Client.filter(etablissement=etab).count()
    nb_reservations = await Reservation.filter(etablissement=etab).count()
    
    # CA par mois (12 derniers mois)
    # TODO: Décommenter quand la colonne commande_id sera créée dans la base
    # paiements = await Paiement.filter(commande__etablissement=etab)
    # ca = sum(p.montant for p in paiements)
    ca = 0  # Temporaire en attendant la migration
    
    # Taux d'occupation
    chambres_occupees = await Chambre.filter(
        etablissement=etab, 
        etat=EtatChambre.OCCUPEE
    ).count()
    taux_occupation = (chambres_occupees / nb_chambres * 100) if nb_chambres > 0 else 0
    
    # Répartition des chambres par état
    etats_chambres = await Chambre.filter(etablissement=etab).annotate(
        count=Count("id")
    ).group_by("etat").values("etat", "count")
    
    return {
        **etab.__dict__,
        "statistiques": {
            "nb_chambres": nb_chambres,
            "nb_clients": nb_clients,
            "nb_reservations": nb_reservations,
            "ca_mensuel": ca,
            "taux_occupation": round(taux_occupation, 2),
            "etats_chambres": etats_chambres
        }
    }

@router.post("/establishments")
async def create_establishment_admin(etablissement: EtablissementCreate):
    """Créer un nouvel établissement (Super Admin)"""
    # Vérifier si l'email existe déjà
    existing = await Etablissement.get_or_none(email=etablissement.email)
    if existing:
        raise HTTPException(status_code=400, detail="Un établissement avec cet email existe déjà")
    
    etab = await Etablissement.create(**etablissement.dict())
    return {
        "message": "Établissement créé avec succès",
        "etablissement": etab
    }

@router.put("/establishments/{establishment_id}")
async def update_establishment_admin(establishment_id: int, etablissement: EtablissementCreate):
    """Modifier un établissement (Super Admin)"""
    etab = await Etablissement.get_or_none(id=establishment_id)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    
    # Vérifier si l'email existe déjà (sauf pour cet établissement)
    existing = await Etablissement.get_or_none(email=etablissement.email)
    if existing and existing.id != establishment_id:
        raise HTTPException(status_code=400, detail="Un établissement avec cet email existe déjà")
    
    await etab.update_from_dict(etablissement.dict())
    await etab.save()
    
    return {
        "message": "Établissement modifié avec succès",
        "etablissement": etab
    }

@router.delete("/establishments/{establishment_id}")
async def delete_establishment_admin(establishment_id: int):
    """Supprimer un établissement (Super Admin)"""
    etab = await Etablissement.get_or_none(id=establishment_id)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    
    # Supprimer les données associées
    await Chambre.filter(etablissement=etab).delete()
    await Client.filter(etablissement=etab).delete()
    await Reservation.filter(etablissement=etab).delete()
    
    await etab.delete()
    return {"message": "Établissement supprimé avec succès"}

@router.get("/establishments/{establishment_id}/statistics")
async def get_establishment_statistics_admin(establishment_id: int):
    """Récupérer les statistiques détaillées d'un établissement"""
    etab = await Etablissement.get_or_none(id=establishment_id)
    if not etab:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    
    # Statistiques de base
    nb_chambres = await Chambre.filter(etablissement=etab).count()
    nb_clients = await Client.filter(etablissement=etab).count()
    nb_reservations = await Reservation.filter(etablissement=etab).count()
    
    # CA total
    # TODO: Décommenter quand la colonne commande_id sera créée dans la base
    # paiements = await Paiement.filter(commande__etablissement=etab)
    # ca = sum(p.montant for p in paiements)
    ca = 0  # Temporaire en attendant la migration
    
    # Taux d'occupation
    chambres_occupees = await Chambre.filter(
        etablissement=etab, 
        etat=EtatChambre.OCCUPEE
    ).count()
    taux_occupation = (chambres_occupees / nb_chambres * 100) if nb_chambres > 0 else 0
    
    # Répartition des chambres par type
    types_chambres = await Chambre.filter(etablissement=etab).annotate(
        count=Count("id")
    ).group_by("categorie").values("categorie", "count")
    
    # Répartition des chambres par état
    etats_chambres = await Chambre.filter(etablissement=etab).annotate(
        count=Count("id")
    ).group_by("etat").values("etat", "count")
    
    # Réservations par statut
    reservations_par_statut = await Reservation.filter(etablissement=etab).annotate(
        count=Count("id")
    ).group_by("statut").values("statut", "count")
    
    return {
        "etablissement": {
            "id": etab.id,
            "nom": etab.nom,
            "type": etab.type_,
            "ville": etab.ville
        },
        "statistiques": {
            "nb_chambres": nb_chambres,
            "nb_clients": nb_clients,
            "nb_reservations": nb_reservations,
            "ca_total": ca,
            "taux_occupation": round(taux_occupation, 2),
            "types_chambres": types_chambres,
            "etats_chambres": etats_chambres,
            "reservations_par_statut": reservations_par_statut
        }
    }

@router.get("/establishments/statistics/global")
async def get_global_establishment_statistics():
    """Récupérer les statistiques globales de tous les établissements"""
    # Statistiques de base
    total_etablissements = await Etablissement.all().count()
    hotels = await Etablissement.filter(type_=Type_etablissement.HOTELERIE).count()
    restaurants = await Etablissement.filter(type_=Type_etablissement.RESTAURATION).count()
    hotel_restaurants = await Etablissement.filter(type_=Type_etablissement.HOTELERIE_RESTAURATION).count()
    
    # Répartition par ville
    etablissements_par_ville = await Etablissement.all().annotate(
        count=Count("id")
    ).group_by("ville").values("ville", "count")
    
    # Répartition par statut
    etablissements_par_statut = await Etablissement.all().annotate(
        count=Count("id")
    ).group_by("statut").values("statut", "count")
    
    # Établissements récents (30 derniers jours)
    from datetime import datetime, timedelta
    date_30_jours = datetime.now() - timedelta(days=30)
    etablissements_recents = await Etablissement.filter(
        created_at__gte=date_30_jours
    ).count()
    
    return {
        "total_etablissements": total_etablissements,
        "repartition_par_type": {
            "hotels": hotels,
            "restaurants": restaurants,
            "hotel_restaurants": hotel_restaurants
        },
        "etablissements_par_ville": etablissements_par_ville,
        "etablissements_par_statut": etablissements_par_statut,
        "etablissements_recents_30_jours": etablissements_recents
    } 