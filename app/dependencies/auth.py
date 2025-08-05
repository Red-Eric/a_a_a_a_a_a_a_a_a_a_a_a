# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from typing import Optional, List
# from app.services.auth_service import AuthService
# from app.models.user import User
# from app.enum.role import Role

# security = HTTPBearer()

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
#     """Dépendance pour récupérer l'utilisateur actuel"""
#     return await AuthService.get_current_user(credentials.credentials)

# async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
#     """Dépendance pour vérifier que l'utilisateur est actif"""
#     if current_user.statut_compte != "active":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Compte désactivé"
#         )
#     return current_user

# def require_roles(allowed_roles: List[Role]):
#     """Décorateur pour vérifier les rôles autorisés"""
#     def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
#         if current_user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Permissions insuffisantes"
#             )
#         return current_user
#     return role_checker

# # Dépendances spécifiques par niveau hiérarchique

# # Niveau 1: Super Admin (Système) - Utilise le rôle Manager sans établissement
# async def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
#     """Vérifie que l'utilisateur est super admin (Manager sans établissement)"""
#     if current_user.role != Role.MANAGER or current_user.etablissement is not None:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Accès réservé au Super Admin"
#         )
#     return current_user

# # Niveau 2: Propriétaire d'Établissement - Utilise le rôle Manager
# require_etablissement_owner = require_roles([Role.MANAGER])

# # Niveau 3: Personnel d'Établissement
# require_direction_etablissement = require_roles([Role.DIRECTEUR])
# require_reception = require_roles([Role.RECEPTIONNISTE])
# require_caissier = require_roles([Role.CAISSIER])
# require_rh = require_roles([Role.RH])
# require_technicien = require_roles([Role.TECHNICIEN])

# # Dépendance pour vérifier l'accès à un établissement spécifique
# async def require_establishment_access(
#     establishment_id: int,
#     current_user: User = Depends(get_current_active_user)
# ) -> User:
#     """Vérifie que l'utilisateur a accès à l'établissement spécifié"""
#     # Super admin a accès à tous les établissements (pour la gestion système)
#     if current_user.role == Role.MANAGER and current_user.etablissement is None:
#         return current_user
    
#     # Propriétaire d'établissement (Manager) peut accéder à son établissement
#     if current_user.role == Role.MANAGER and current_user.etablissement and current_user.etablissement.id == establishment_id:
#         return current_user
    
#     # Personnel d'établissement peut accéder à son établissement
#     if current_user.etablissement and current_user.etablissement.id == establishment_id:
#         return current_user
    
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Accès non autorisé à cet établissement"
#     )

# # Dépendance pour vérifier que l'utilisateur appartient à un établissement
# async def require_establishment_membership(
#     current_user: User = Depends(get_current_active_user)
# ) -> User:
#     """Vérifie que l'utilisateur appartient à un établissement"""
#     if current_user.role == Role.MANAGER and current_user.etablissement is None:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Cette fonctionnalité n'est pas disponible pour le super admin"
#         )
    
#     if not current_user.etablissement:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Vous devez appartenir à un établissement"
#         )
    
#     return current_user 