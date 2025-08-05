from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime, timedelta
import json
import logging
import csv
import io
from tortoise.functions import Count
from tortoise.expressions import Q

from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.models.reservation import Reservation
from app.models.client import Client
from app.enum.etablissement_statu import Etablissement_status

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

@router.get("/reports/establishments")
async def export_establishments_report(
    format: str = Query("csv", regex="^(csv|json)$"),
    type_filter: Optional[str] = Query(None, description="Filter by establishment type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    city_filter: Optional[str] = Query(None, description="Filter by city"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Export establishments report in CSV or JSON format (without pandas)
    """
    try:
        # Build query filters
        filters = Q()
        if type_filter:
            filters &= Q(type_=type_filter)
        if status_filter:
            filters &= Q(statut=status_filter)
        if city_filter:
            filters &= Q(ville__icontains=city_filter)
        if date_from:
            filters &= Q(created_at__gte=datetime.strptime(date_from, "%Y-%m-%d"))
        if date_to:
            filters &= Q(created_at__lte=datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1))

        # Get establishments data
        establishments = await Etablissement.filter(filters).values(
            "id", "nom", "type_", "ville", "pays", "statut", 
            "email", "telephone", "created_at", "updated_at"
        )

        if not establishments:
            raise HTTPException(status_code=404, detail="Aucun établissement trouvé")

        # Format dates
        for etab in establishments:
            if etab['created_at']:
                etab['created_at'] = etab['created_at'].strftime('%Y-%m-%d %H:%M')
            if etab['updated_at']:
                etab['updated_at'] = etab['updated_at'].strftime('%Y-%m-%d %H:%M')

        filename = f"rapport_etablissements_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if format == "csv":
            # Create CSV content
            output = io.StringIO()
            if establishments:
                fieldnames = establishments[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(establishments)
            
            csv_content = output.getvalue()
            output.close()
            
            # Return CSV as file response
            return {
                "content": csv_content,
                "filename": f"{filename}.csv",
                "format": "csv"
            }
        
        elif format == "json":
            return {
                "data": establishments,
                "filename": f"{filename}.json",
                "format": "json"
            }

    except Exception as e:
        logging.error(f"Erreur lors de l'export du rapport: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'export: {str(e)}")

@router.get("/reports/geographic-analysis")
async def get_geographic_analysis():
    """
    Get detailed geographic analysis of establishments
    """
    try:
        # Top cities with establishment count
        top_cities = await Etablissement.all().annotate(
            count=Count("id")
        ).group_by("ville").order_by("-count").limit(20).values("ville", "count")

        # Growth by city (last 30 days vs previous 30 days)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        date_60_days_ago = datetime.now() - timedelta(days=60)

        recent_establishments = await Etablissement.filter(
            created_at__gte=date_30_days_ago
        ).annotate(count=Count("id")).group_by("ville").values("ville", "count")

        previous_establishments = await Etablissement.filter(
            created_at__gte=date_60_days_ago,
            created_at__lt=date_30_days_ago
        ).annotate(count=Count("id")).group_by("ville").values("ville", "count")

        # Calculate growth rates
        growth_analysis = []
        for city_data in top_cities:
            city = city_data["ville"]
            current_count = city_data["count"]
            
            recent_count = next((item["count"] for item in recent_establishments if item["ville"] == city), 0)
            previous_count = next((item["count"] for item in previous_establishments if item["ville"] == city), 0)
            
            growth_rate = ((recent_count - previous_count) / previous_count * 100) if previous_count > 0 else 0
            
            growth_analysis.append({
                "ville": city,
                "total_etablissements": current_count,
                "nouveaux_30_jours": recent_count,
                "nouveaux_60_jours": previous_count,
                "taux_croissance": round(growth_rate, 1),
                "potentiel": min(10, max(1, current_count // 3))
            })

        # Cities with low representation
        low_representation = await Etablissement.all().annotate(
            count=Count("id")
        ).group_by("ville").filter(count__lt=3).values("ville", "count")

        return {
            "top_villes": growth_analysis,
            "villes_peu_representees": [
                {"ville": item["ville"], "nb_etablissements": item["count"]}
                for item in low_representation
            ],
            "analyse_croissance": {
                "villes_en_croissance": [city for city in growth_analysis if city["taux_croissance"] > 0],
                "villes_stables": [city for city in growth_analysis if city["taux_croissance"] == 0],
                "villes_en_declin": [city for city in growth_analysis if city["taux_croissance"] < 0]
            }
        }

    except Exception as e:
        logging.error(f"Erreur lors de l'analyse géographique: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {str(e)}")

@router.get("/reports/performance-analysis")
async def get_performance_analysis():
    """
    Get performance analysis of establishments
    """
    try:
        # Get establishments with their basic stats
        establishments = await Etablissement.all().values(
            "id", "nom", "type_", "ville", "statut", "created_at"
        )

        # Calculate performance metrics
        total_establishments = len(establishments)
        active_establishments = len([e for e in establishments if e["statut"] == Etablissement_status.ACTIVE.value])
        
        # Performance by type
        performance_by_type = {}
        for etab in establishments:
            etab_type = etab["type_"]
            if etab_type not in performance_by_type:
                performance_by_type[etab_type] = {
                    "total": 0,
                    "actifs": 0,
                    "inactifs": 0
                }
            
            performance_by_type[etab_type]["total"] += 1
            if etab["statut"] == Etablissement_status.ACTIVE.value:
                performance_by_type[etab_type]["actifs"] += 1
            else:
                performance_by_type[etab_type]["inactifs"] += 1

        # Calculate retention rates
        for etab_type, stats in performance_by_type.items():
            stats["taux_retention"] = (stats["actifs"] / stats["total"] * 100) if stats["total"] > 0 else 0

        # Recent activity analysis
        date_7_days_ago = datetime.now() - timedelta(days=7)
        recent_activity = await Etablissement.filter(
            updated_at__gte=date_7_days_ago
        ).count()

        # Inactive establishments (not updated in 30 days)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        inactive_establishments = await Etablissement.filter(
            updated_at__lt=date_30_days_ago
        ).count()

        return {
            "statistiques_generales": {
                "total_etablissements": total_establishments,
                "etablissements_actifs": active_establishments,
                "taux_activation": (active_establishments / total_establishments * 100) if total_establishments > 0 else 0,
                "activite_recente": recent_activity,
                "etablissements_inactifs": inactive_establishments
            },
            "performance_par_type": performance_by_type,
            "tendances": {
                "croissance_7_jours": recent_activity,
                "stabilite": total_establishments - inactive_establishments
            }
        }

    except Exception as e:
        logging.error(f"Erreur lors de l'analyse de performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {str(e)}")

@router.get("/reports/monthly-report")
async def get_monthly_report(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020)
):
    """
    Get monthly report for establishments
    """
    try:
        # Use current month/year if not specified
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get establishments created in this month
        establishments = await Etablissement.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).values("id", "nom", "type_", "ville", "statut", "created_at")

        # Get establishments by type
        establishments_by_type = {}
        for etab in establishments:
            etab_type = etab["type_"]
            if etab_type not in establishments_by_type:
                establishments_by_type[etab_type] = []
            establishments_by_type[etab_type].append(etab)

        # Get establishments by city
        establishments_by_city = {}
        for etab in establishments:
            city = etab["ville"]
            if city not in establishments_by_city:
                establishments_by_city[city] = []
            establishments_by_city[city].append(etab)

        return {
            "periode": {
                "mois": month,
                "annee": year,
                "debut": start_date.strftime("%Y-%m-%d"),
                "fin": (end_date - timedelta(days=1)).strftime("%Y-%m-%d")
            },
            "statistiques": {
                "total_nouveaux": len(establishments),
                "par_type": {k: len(v) for k, v in establishments_by_type.items()},
                "par_ville": {k: len(v) for k, v in establishments_by_city.items()}
            },
            "etablissements": establishments,
            "analyse_detaille": {
                "types": establishments_by_type,
                "villes": establishments_by_city
            }
        }

    except Exception as e:
        logging.error(f"Erreur lors de la génération du rapport mensuel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de rapport: {str(e)}")

@router.get("/reports/export-csv")
async def export_csv_report():
    """
    Export all establishments as CSV
    """
    try:
        establishments = await Etablissement.all().values(
            "id", "nom", "type_", "ville", "pays", "statut", 
            "email", "telephone", "created_at", "updated_at"
        )

        if not establishments:
            raise HTTPException(status_code=404, detail="Aucun établissement trouvé")

        # Format dates
        for etab in establishments:
            if etab['created_at']:
                etab['created_at'] = etab['created_at'].strftime('%Y-%m-%d %H:%M')
            if etab['updated_at']:
                etab['updated_at'] = etab['updated_at'].strftime('%Y-%m-%d %H:%M')

        # Create CSV content
        output = io.StringIO()
        if establishments:
            fieldnames = establishments[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(establishments)
        
        csv_content = output.getvalue()
        output.close()

        filename = f"export_etablissements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return {
            "content": csv_content,
            "filename": filename,
            "format": "csv",
            "total_records": len(establishments)
        }

    except Exception as e:
        logging.error(f"Erreur lors de l'export CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'export: {str(e)}")

@router.get("/reports/export-json")
async def export_json_report():
    """
    Export all establishments as JSON
    """
    try:
        establishments = await Etablissement.all().values(
            "id", "nom", "type_", "ville", "pays", "statut", 
            "email", "telephone", "created_at", "updated_at"
        )

        if not establishments:
            raise HTTPException(status_code=404, detail="Aucun établissement trouvé")

        # Format dates
        for etab in establishments:
            if etab['created_at']:
                etab['created_at'] = etab['created_at'].strftime('%Y-%m-%d %H:%M')
            if etab['updated_at']:
                etab['updated_at'] = etab['updated_at'].strftime('%Y-%m-%d %H:%M')

        filename = f"export_etablissements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return {
            "data": establishments,
            "filename": filename,
            "format": "json",
            "total_records": len(establishments)
        }

    except Exception as e:
        logging.error(f"Erreur lors de l'export JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'export: {str(e)}") 