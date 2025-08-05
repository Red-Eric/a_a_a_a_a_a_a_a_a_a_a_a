# Structure API

Cette section contient toutes les APIs organisées par domaine fonctionnel.

## Structure des dossiers

```
api/
├── __init__.py
├── admin/                    # APIs pour l'administration
│   ├── __init__.py
│   ├── statistics.py        # Statistiques admin
│   └── establishments.py    # Gestion des établissements
└── README.md
```

## APIs Admin

### Statistiques (`/admin/statistics`)
- `GET /admin/statistics` - Récupérer toutes les statistiques de la plateforme

### Établissements (`/admin/establishments`)
- `GET /admin/establishments` - Liste tous les établissements avec filtres
- `GET /admin/establishments/{id}` - Détails d'un établissement
- `POST /admin/establishments` - Créer un nouvel établissement
- `PUT /admin/establishments/{id}` - Modifier un établissement
- `DELETE /admin/establishments/{id}` - Supprimer un établissement
- `GET /admin/establishments/{id}/statistics` - Statistiques d'un établissement
- `GET /admin/establishments/statistics/global` - Statistiques globales

## Utilisation

Les routes sont automatiquement incluses dans `main.py` via le router principal :

```python
from app.api.admin import admin_router
app.include_router(admin_router, prefix="/admin", tags=["admin"])
```

## Frontend

Le frontend utilise le fichier `frontend/api/admin.js` pour centraliser les appels API :

```javascript
import { adminStatisticsAPI, adminEstablishmentsAPI } from "@/lib/func/api/admin";

// Exemple d'utilisation
const stats = await adminStatisticsAPI.getStatistics();
const establishments = await adminEstablishmentsAPI.getAll();
``` 