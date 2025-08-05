from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.etablissement import Etablissement
from app.models.chambre import Chambre
from app.models.client import Client
from app.models.reservation import Reservation
from app.models.paiement import Paiement
from tortoise.functions import Sum, Count
from tortoise.expressions import Q

router = APIRouter()

# Modèles Pydantic pour la configuration
class SystemConfig(BaseModel):
    maintenance_mode: bool = False
    maintenance_message: str = "Système en maintenance"
    max_establishments_per_user: int = 5
    auto_backup_enabled: bool = True
    backup_frequency_hours: int = 24
    data_retention_days: int = 365
    max_file_size_mb: int = 10
    session_timeout_minutes: int = 30
    password_policy_min_length: int = 8
    password_policy_require_special: bool = True
    two_factor_required: bool = False
    api_rate_limit_per_minute: int = 100
    email_notifications_enabled: bool = True
    sms_notifications_enabled: bool = False
    push_notifications_enabled: bool = True

class NotificationConfig(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    new_establishment_notification: bool = True
    low_performance_alert: bool = True
    security_alert: bool = True
    system_maintenance_notification: bool = True
    weekly_report_enabled: bool = True
    monthly_report_enabled: bool = True
    alert_threshold_establishments: int = 10
    alert_threshold_growth_rate: float = 5.0

class SecurityConfig(BaseModel):
    password_expiry_days: int = 90
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = []
    session_encryption: bool = True
    audit_log_enabled: bool = True
    data_encryption_at_rest: bool = True
    ssl_required: bool = True
    api_key_rotation_days: int = 30

class IntegrationConfig(BaseModel):
    payment_gateway_enabled: bool = True
    payment_gateway_provider: str = "stripe"
    sms_gateway_enabled: bool = False
    sms_gateway_provider: str = "twilio"
    email_service_enabled: bool = True
    email_service_provider: str = "sendgrid"
    analytics_enabled: bool = True
    analytics_provider: str = "google_analytics"
    backup_service_enabled: bool = True
    backup_service_provider: str = "aws_s3"

class ThemeConfig(BaseModel):
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    accent_color: str = "#F59E0B"
    dark_mode_enabled: bool = True
    custom_css_enabled: bool = False
    custom_css: str = ""
    logo_url: str = "/images/logo.png"
    favicon_url: str = "/favicon.ico"

# Configuration système actuelle (simulée)
current_system_config = SystemConfig()
current_notification_config = NotificationConfig()
current_security_config = SecurityConfig()
current_integration_config = IntegrationConfig()
current_theme_config = ThemeConfig()

@router.get("/system")
async def get_system_config():
    """Récupérer la configuration système actuelle"""
    try:
        logging.info("Récupération de la configuration système")
        
        return {
            "status": "success",
            "data": {
                "system": current_system_config.dict(),
                "notifications": current_notification_config.dict(),
                "security": current_security_config.dict(),
                "integrations": current_integration_config.dict(),
                "theme": current_theme_config.dict(),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de la configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/system")
async def update_system_config(config: SystemConfig):
    """Mettre à jour la configuration système"""
    try:
        logging.info("Mise à jour de la configuration système")
        
        # Validation des paramètres
        if config.max_establishments_per_user < 1:
            raise HTTPException(status_code=400, detail="Le nombre maximum d'établissements doit être supérieur à 0")
        
        if config.backup_frequency_hours < 1:
            raise HTTPException(status_code=400, detail="La fréquence de sauvegarde doit être supérieure à 0")
        
        if config.data_retention_days < 30:
            raise HTTPException(status_code=400, detail="La rétention des données doit être d'au moins 30 jours")
        
        # Mise à jour de la configuration
        global current_system_config
        current_system_config = config
        
        return {
            "status": "success",
            "message": "Configuration système mise à jour avec succès",
            "data": current_system_config.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour de la configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/notifications")
async def update_notification_config(config: NotificationConfig):
    """Mettre à jour la configuration des notifications"""
    try:
        logging.info("Mise à jour de la configuration des notifications")
        
        global current_notification_config
        current_notification_config = config
        
        return {
            "status": "success",
            "message": "Configuration des notifications mise à jour avec succès",
            "data": current_notification_config.dict()
        }
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour des notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/security")
async def update_security_config(config: SecurityConfig):
    """Mettre à jour la configuration de sécurité"""
    try:
        logging.info("Mise à jour de la configuration de sécurité")
        
        # Validation des paramètres de sécurité
        if config.password_expiry_days < 30:
            raise HTTPException(status_code=400, detail="L'expiration du mot de passe doit être d'au moins 30 jours")
        
        if config.max_login_attempts < 3:
            raise HTTPException(status_code=400, detail="Le nombre maximum de tentatives doit être d'au moins 3")
        
        global current_security_config
        current_security_config = config
        
        return {
            "status": "success",
            "message": "Configuration de sécurité mise à jour avec succès",
            "data": current_security_config.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour de la sécurité: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/integrations")
async def update_integration_config(config: IntegrationConfig):
    """Mettre à jour la configuration des intégrations"""
    try:
        logging.info("Mise à jour de la configuration des intégrations")
        
        global current_integration_config
        current_integration_config = config
        
        return {
            "status": "success",
            "message": "Configuration des intégrations mise à jour avec succès",
            "data": current_integration_config.dict()
        }
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour des intégrations: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.put("/theme")
async def update_theme_config(config: ThemeConfig):
    """Mettre à jour la configuration du thème"""
    try:
        logging.info("Mise à jour de la configuration du thème")
        
        global current_theme_config
        current_theme_config = config
        
        return {
            "status": "success",
            "message": "Configuration du thème mise à jour avec succès",
            "data": current_theme_config.dict()
        }
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du thème: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/maintenance")
async def toggle_maintenance_mode(enabled: bool, message: str = "Système en maintenance"):
    """Activer/désactiver le mode maintenance"""
    try:
        logging.info(f"Changement du mode maintenance: {enabled}")
        
        global current_system_config
        current_system_config.maintenance_mode = enabled
        current_system_config.maintenance_message = message
        
        return {
            "status": "success",
            "message": f"Mode maintenance {'activé' if enabled else 'désactivé'} avec succès",
            "data": {
                "maintenance_mode": enabled,
                "maintenance_message": message
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors du changement du mode maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/system-status")
async def get_system_status():
    """Récupérer le statut du système"""
    try:
        logging.info("Récupération du statut système")
        
        # Statistiques système
        total_etablissements = await Etablissement.all().count()
        total_chambres = await Chambre.all().count()
        total_clients = await Client.all().count()
        total_reservations = await Reservation.all().count()
        
        # Calcul de l'utilisation du système
        system_usage = {
            "cpu_usage": 45.2,  # Simulé
            "memory_usage": 67.8,  # Simulé
            "disk_usage": 23.4,  # Simulé
            "database_connections": 12,  # Simulé
            "active_sessions": 8,  # Simulé
            "uptime_hours": 168,  # Simulé
            "last_backup": (datetime.now() - timedelta(hours=6)).isoformat(),
            "next_backup": (datetime.now() + timedelta(hours=18)).isoformat()
        }
        
        # Alertes système
        system_alerts = []
        
        if system_usage["memory_usage"] > 80:
            system_alerts.append({
                "type": "warning",
                "message": "Utilisation mémoire élevée",
                "severity": "medium"
            })
        
        if system_usage["disk_usage"] > 90:
            system_alerts.append({
                "type": "critical",
                "message": "Espace disque critique",
                "severity": "high"
            })
        
        if not current_system_config.auto_backup_enabled:
            system_alerts.append({
                "type": "info",
                "message": "Sauvegarde automatique désactivée",
                "severity": "low"
            })
        
        return {
            "status": "success",
            "data": {
                "system_usage": system_usage,
                "statistics": {
                    "total_establishments": total_etablissements,
                    "total_rooms": total_chambres,
                    "total_clients": total_clients,
                    "total_reservations": total_reservations
                },
                "maintenance_mode": current_system_config.maintenance_mode,
                "alerts": system_alerts,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du statut: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/backup")
async def trigger_manual_backup():
    """Déclencher une sauvegarde manuelle"""
    try:
        logging.info("Déclenchement d'une sauvegarde manuelle")
        
        # Simulation d'une sauvegarde
        backup_info = {
            "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "estimated_duration_minutes": 15,
            "size_mb": 245.7,
            "status": "in_progress"
        }
        
        return {
            "status": "success",
            "message": "Sauvegarde manuelle déclenchée",
            "data": backup_info
        }
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/backup-status/{backup_id}")
async def get_backup_status(backup_id: str):
    """Récupérer le statut d'une sauvegarde"""
    try:
        logging.info(f"Récupération du statut de la sauvegarde: {backup_id}")
        
        # Simulation du statut de sauvegarde
        backup_status = {
            "backup_id": backup_id,
            "status": "completed",
            "started_at": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration_minutes": 10,
            "size_mb": 245.7,
            "files_count": 1247,
            "compression_ratio": 0.75
        }
        
        return {
            "status": "success",
            "data": backup_status
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du statut: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """Récupérer les logs système"""
    try:
        logging.info("Récupération des logs système")
        
        # Simulation des logs système
        logs = []
        for i in range(min(limit, 50)):
            log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
            log_level = level if level else log_levels[i % len(log_levels)]
            
            logs.append({
                "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                "level": log_level,
                "message": f"Log message {i+1} - {log_level} level",
                "module": f"module_{i % 5}",
                "user_id": f"user_{i % 10}" if i % 3 == 0 else None
            })
        
        return {
            "status": "success",
            "data": {
                "logs": logs,
                "total_count": len(logs),
                "filters_applied": {
                    "level": level,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit
                }
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/clear-cache")
async def clear_system_cache():
    """Vider le cache système"""
    try:
        logging.info("Vidage du cache système")
        
        return {
            "status": "success",
            "message": "Cache système vidé avec succès",
            "data": {
                "cleared_at": datetime.now().isoformat(),
                "cache_size_mb": 45.2
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors du vidage du cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.get("/api-keys")
async def get_api_keys():
    """Récupérer les clés API actives"""
    try:
        logging.info("Récupération des clés API")
        
        # Simulation des clés API
        api_keys = [
            {
                "key_id": "key_001",
                "name": "API Production",
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "last_used": datetime.now().isoformat(),
                "permissions": ["read", "write"],
                "status": "active"
            },
            {
                "key_id": "key_002",
                "name": "API Development",
                "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "last_used": (datetime.now() - timedelta(hours=2)).isoformat(),
                "permissions": ["read"],
                "status": "active"
            }
        ]
        
        return {
            "status": "success",
            "data": {
                "api_keys": api_keys,
                "total_count": len(api_keys)
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des clés API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/api-keys")
async def create_api_key(name: str, permissions: List[str]):
    """Créer une nouvelle clé API"""
    try:
        logging.info(f"Création d'une nouvelle clé API: {name}")
        
        new_key = {
            "key_id": f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name,
            "api_key": f"ghr_{datetime.now().strftime('%Y%m%d%H%M%S')}_{name.lower().replace(' ', '_')}",
            "created_at": datetime.now().isoformat(),
            "permissions": permissions,
            "status": "active"
        }
        
        return {
            "status": "success",
            "message": "Clé API créée avec succès",
            "data": new_key
        }
    except Exception as e:
        logging.error(f"Erreur lors de la création de la clé API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    """Révoquer une clé API"""
    try:
        logging.info(f"Révocation de la clé API: {key_id}")
        
        return {
            "status": "success",
            "message": f"Clé API {key_id} révoquée avec succès",
            "data": {
                "key_id": key_id,
                "revoked_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la révocation de la clé API: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") 