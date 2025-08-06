from fastapi import APIRouter
from app.models.notification import Notification
from app.schemas.notificationCreate import NotificationCreate
from app.models.etablissement import Etablissement
from app.websocket.notification_manager import notification_manager
from app.models.notification import Notification

router = APIRouter()


@router.get("")
async def getallNotif():
    notif = await Notification.all().order_by("-id")
    
    return {
        "message": "notis",
        "notifications": notif
    }


@router.get("/etablissement/{id_etab}")
async def getNotifByEtab(id_etab : int):
    etab = await Etablissement.get_or_none(id = id_etab)
    if not etab:
        return {
            "message": "etablissement inexistant"
        }
        
    allNotif = await Notification.filter(etablissement = etab).all().order_by("-id")
    
    return {
        "message" : "voici la liste de tout les etablissement",
        "notifications" : allNotif
    }

@router.patch("/{id_notif}")
async def patchLu(id_notif : int):
    notif = await Notification.get_or_none(id = id_notif)
    if not notif:
        return {
            "message" : "Notification inexsistante"
        }
        
    notif.lu = True
    await notif.save()
    
    await notification_manager.broadcast(
        event="notification_patch",
        payload={"message": f"notif lu"}
    )
    
    return {
        "message" : "Notification patcher",
        "notification" : notif
    }
    
    
@router.delete("/{id_notif}")
async def patchLu(id_notif : int):
    
    notif = await Notification.get_or_none(id = id_notif)
    if not notif:
        return {
            "message" : "Notification inexsistante"
        }
    
    await notif.delete()
    
    await notification_manager.broadcast(
        event="notification_delete",
        payload={"message": f"notif effacer"}
    )
    
    return {
        "message" : "Notification effacer"
    }
    
