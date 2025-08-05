from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from tortoise.functions import Count
from tortoise.expressions import Q

from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.models.reservation import Reservation
from app.enum.etablissement_statu import Etablissement_status

router = APIRouter(prefix="/admin", tags=["Admin Alerts"])

@router.get("/alerts/urgent")
async def get_urgent_alerts():
    """
    Get urgent alerts that require immediate attention
    """
    try:
        urgent_alerts = []
        
        # Check for establishments inactive for more than 30 days
        date_30_days_ago = datetime.now() - timedelta(days=30)
        inactive_establishments = await Etablissement.filter(
            statut=Etablissement_status.INACTIVE,
            updated_at__lte=date_30_days_ago
        ).count()
        
        if inactive_establishments > 0:
            urgent_alerts.append({
                "id": "inactive_establishments",
                "type": "warning",
                "severity": "high" if inactive_establishments > 20 else "medium",
                "title": "Établissements inactifs",
                "message": f"{inactive_establishments} établissements inactifs depuis plus de 30 jours",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "review_inactive_establishments",
                "count": inactive_establishments
            })
        
        # Check for cities with very few establishments
        cities_low_representation = await Etablissement.all().annotate(
            count=Count("id")
        ).group_by("ville").filter(count__lt=2).count()
        
        if cities_low_representation > 5:
            urgent_alerts.append({
                "id": "low_representation_cities",
                "type": "info",
                "severity": "medium",
                "title": "Villes peu représentées",
                "message": f"{cities_low_representation} villes avec moins de 2 établissements",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "expand_geographic_coverage",
                "count": cities_low_representation
            })
        
        # Check for no new establishments in the last 7 days
        date_7_days_ago = datetime.now() - timedelta(days=7)
        recent_establishments = await Etablissement.filter(
            created_at__gte=date_7_days_ago
        ).count()
        
        if recent_establishments == 0:
            urgent_alerts.append({
                "id": "no_recent_establishments",
                "type": "warning",
                "severity": "medium",
                "title": "Aucun nouvel établissement",
                "message": "Aucun nouvel établissement inscrit cette semaine",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "review_registration_process",
                "count": 0
            })
        
        # Check for establishments with potential issues (no recent activity)
        date_14_days_ago = datetime.now() - timedelta(days=14)
        establishments_no_activity = await Etablissement.filter(
            updated_at__lte=date_14_days_ago,
            statut=Etablissement_status.ACTIVE
        ).count()
        
        if establishments_no_activity > 10:
            urgent_alerts.append({
                "id": "establishments_no_activity",
                "type": "warning",
                "severity": "medium",
                "title": "Établissements sans activité",
                "message": f"{establishments_no_activity} établissements actifs sans activité récente",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "check_establishment_activity",
                "count": establishments_no_activity
            })
        
        return {
            "urgent_alerts": urgent_alerts,
            "total_alerts": len(urgent_alerts),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des alertes urgentes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'alertes: {str(e)}")

@router.get("/alerts/performance")
async def get_performance_alerts():
    """
    Get performance-related alerts
    """
    try:
        performance_alerts = []
        
        # Calculate retention rate
        total_establishments = await Etablissement.all().count()
        active_establishments = await Etablissement.filter(statut=Etablissement_status.ACTIVE).count()
        retention_rate = (active_establishments / total_establishments * 100) if total_establishments > 0 else 0
        
        if retention_rate < 80:
            performance_alerts.append({
                "id": "low_retention_rate",
                "type": "warning",
                "severity": "high" if retention_rate < 60 else "medium",
                "title": "Taux de rétention faible",
                "message": f"Taux de rétention: {retention_rate:.1f}% (objectif: 80%)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "improve_retention_strategy",
                "metric": retention_rate,
                "target": 80
            })
        
        # Check growth rate (last 30 days vs previous 30 days)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        date_60_days_ago = datetime.now() - timedelta(days=60)
        
        recent_growth = await Etablissement.filter(
            created_at__gte=date_30_days_ago
        ).count()
        
        previous_growth = await Etablissement.filter(
            created_at__gte=date_60_days_ago,
            created_at__lt=date_30_days_ago
        ).count()
        
        growth_rate = ((recent_growth - previous_growth) / previous_growth * 100) if previous_growth > 0 else 0
        
        if growth_rate < 0:
            performance_alerts.append({
                "id": "negative_growth",
                "type": "warning",
                "severity": "high" if growth_rate < -20 else "medium",
                "title": "Croissance négative",
                "message": f"Taux de croissance: {growth_rate:.1f}% (moins d'établissements que le mois précédent)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "review_growth_strategy",
                "metric": growth_rate,
                "target": 0
            })
        
        # Check geographic distribution
        cities_count = await Etablissement.all().annotate(
            count=Count("id")
        ).group_by("ville").count()
        
        if cities_count < 10:
            performance_alerts.append({
                "id": "limited_geographic_coverage",
                "type": "info",
                "severity": "medium",
                "title": "Couverture géographique limitée",
                "message": f"Présent dans seulement {cities_count} villes",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "expand_geographic_presence",
                "metric": cities_count,
                "target": 10
            })
        
        return {
            "performance_alerts": performance_alerts,
            "total_alerts": len(performance_alerts),
            "metrics": {
                "retention_rate": retention_rate,
                "growth_rate": growth_rate,
                "cities_count": cities_count
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des alertes de performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'alertes: {str(e)}")

@router.get("/alerts/system")
async def get_system_alerts():
    """
    Get system-related alerts
    """
    try:
        system_alerts = []
        
        # Check for establishments with potential data issues
        establishments_no_email = await Etablissement.filter(email__isnull=True).count()
        if establishments_no_email > 0:
            system_alerts.append({
                "id": "establishments_no_email",
                "type": "warning",
                "severity": "medium",
                "title": "Établissements sans email",
                "message": f"{establishments_no_email} établissements n'ont pas d'email renseigné",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "complete_establishment_data",
                "count": establishments_no_email
            })
        
        # Check for establishments without phone
        establishments_no_phone = await Etablissement.filter(telephone__isnull=True).count()
        if establishments_no_phone > 0:
            system_alerts.append({
                "id": "establishments_no_phone",
                "type": "warning",
                "severity": "low",
                "title": "Établissements sans téléphone",
                "message": f"{establishments_no_phone} établissements n'ont pas de téléphone renseigné",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "complete_establishment_data",
                "count": establishments_no_phone
            })
        
        # Check for duplicate establishment names
        duplicate_names = await Etablissement.all().annotate(
            count=Count("id")
        ).group_by("nom").filter(count__gt=1).values("nom", "count")
        
        if duplicate_names:
            system_alerts.append({
                "id": "duplicate_establishment_names",
                "type": "warning",
                "severity": "medium",
                "title": "Noms d'établissements en double",
                "message": f"{len(duplicate_names)} noms d'établissements sont en double",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action_required": "review_duplicate_names",
                "details": duplicate_names
            })
        
        return {
            "system_alerts": system_alerts,
            "total_alerts": len(system_alerts),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des alertes système: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'alertes: {str(e)}")

@router.get("/alerts/all")
async def get_all_alerts():
    """
    Get all types of alerts combined
    """
    try:
        # Get all types of alerts
        urgent_alerts_response = await get_urgent_alerts()
        performance_alerts_response = await get_performance_alerts()
        system_alerts_response = await get_system_alerts()
        
        all_alerts = {
            "urgent": urgent_alerts_response["urgent_alerts"],
            "performance": performance_alerts_response["performance_alerts"],
            "system": system_alerts_response["system_alerts"]
        }
        
        # Calculate total alerts
        total_alerts = (
            len(all_alerts["urgent"]) + 
            len(all_alerts["performance"]) + 
            len(all_alerts["system"])
        )
        
        # Count by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for alert_type in all_alerts.values():
            for alert in alert_type:
                severity = alert.get("severity", "low")
                severity_counts[severity] += 1
        
        return {
            "all_alerts": all_alerts,
            "summary": {
                "total_alerts": total_alerts,
                "urgent_count": len(all_alerts["urgent"]),
                "performance_count": len(all_alerts["performance"]),
                "system_count": len(all_alerts["system"]),
                "severity_breakdown": severity_counts
            },
            "metrics": performance_alerts_response.get("metrics", {}),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de toutes les alertes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur d'alertes: {str(e)}")

@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """
    Dismiss an alert (mark as read/acknowledged)
    """
    try:
        # In a real implementation, you would store dismissed alerts in a database
        # For now, we'll just return a success response
        return {
            "message": f"Alerte {alert_id} marquée comme lue",
            "alert_id": alert_id,
            "dismissed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de l'alerte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}") 