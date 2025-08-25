from fastapi import APIRouter, Body
from app.models.personnel import Personnel
from app.models.etablissement import Etablissement
from app.schemas.personnel_create import Personnel_Create
from app.services.auth_service import AuthService
from app.services.email_service import send_email
from app.enum.Notification import NotificationTitle, NotificationType

router = APIRouter()

@router.get("")
async def getAllPersonnel():
    allPersonnel = await Personnel.all().order_by("-id")
    return {
        "message" : "Liste de personnel",
        "personnels" : allPersonnel
    }
    
    
@router.get("/etablissement/{id_}")
async def getPersonnelByETablissement(id_: int):
    personnelToGet =  await Personnel.filter(etablissement_id = id_)
    if not personnelToGet:
        return {"message":"introuvable personnel"}
    
    return {
        "message" :" voici le kkk",
        "personnels" : personnelToGet
    }

@router.get("/{id_personnel}")
async def getPersonnelByID(id_personnel : int):
    pers = await Personnel.get_or_none(id = id_personnel)
    
    if not pers:
        return {
            "message" : "personnel introuvable"
        }
    
    return {
        "message" : f"Voici le personnel {pers.id}",
        "personnel" : pers
    }    



@router.post("")
async def addPersonnel(item : Personnel_Create):
    etab_ = await Etablissement.get_or_none(id = item.etablissement_id)
    if not etab_:
        return {
            "message" : "Etab inexistante"
        }
    
    personnelToAdd = await Personnel.create(
        nom = item.nom,
        prenom = item.prenom,
        telephone = item.telephone,
        email = item.email,
        mot_de_passe =  AuthService.get_password_hash(item.mot_de_passe),
        etablissement = etab_,
        role = item.role,
        poste = item.role,
        salaire = item.salaire,
        date_embauche = item.date_embauche,
        statut_compte = item.statut_compte
    )
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">Bienvenue sur notre plateforme</h2>
            <p>Bonjour,</p>
            <p>
                Vous avez été enregistré en tant que <strong>personnel</strong> au sein de l'établissement 
                <strong>{etab_.nom}</strong>.
            </p>
            <p>Voici vos informations de connexion :</p>

            <ul style="font-size: 16px; color: #333;">
                <li><strong>Mot de passe temporaire :</strong> <span style="color: #4CAF50;">{item.mot_de_passe}</span></li>
                <li><strong>Rôle :</strong> <span style="color: #4CAF50;">{item.role.value}</span></li>
                <li><strong>Poste :</strong> <span style="color: #4CAF50;">{item.poste}</span></li>
                <li><strong>Statut du compte :</strong> <span style="color: #4CAF50;">{item.statut_compte.value}</span></li>
            </ul>

            <p>
                Veuillez conserver ces informations en lieu sûr. 
                <br>Nous vous recommandons de modifier votre mot de passe dès votre première connexion.
            </p>

            <hr style="margin-top: 40px;">
            <p style="font-size: 12px; color: #888;">
                Si vous n'êtes pas à l'origine de cette inscription, veuillez ignorer ce message.
            </p>
        </body>
    </html>
    """


    await send_email(
        subject="Vos identifiants de connexion",
        to=item.email,
        body=html_content
    )
    
    return {
        "message" : "Personnel ajouter avec success",
        "personnel" : personnelToAdd
    }

@router.put("/{id_}")
async def editPersonnel(id_ : int, item : Personnel_Create):
    personnelToEdit = await Personnel.get_or_none( id = id_)
    if not personnelToEdit:
        return {"message" : "Personnel introuvable"}
    
       
    
    personnelToEdit.nom = item.nom
    personnelToEdit.prenom = item.prenom
    personnelToEdit.telephone = item.telephone
    personnelToEdit.email = item.email
    personnelToEdit.salaire = item.salaire
    
    if item.mot_de_passe == "":
        personnelToEdit.mot_de_passe = item.mot_de_passe
    
 
    
    modifications = []

    if item.role != personnelToEdit.role:
        modifications.append(
            f"<li><strong>Rôle :</strong> <span style='color: red;'>{personnelToEdit.role.value}</span> → <span style='color: green;'>{item.role.value}</span></li>"
        )

    if item.poste != personnelToEdit.poste:
        modifications.append(
            f"<li><strong>Poste :</strong> <span style='color: red;'>{personnelToEdit.poste}</span> → <span style='color: green;'>{item.poste}</span></li>"
        )

    if item.statut_compte != personnelToEdit.statut_compte:
        modifications.append(
            f"<li><strong>Statut du compte :</strong> <span style='color: red;'>{personnelToEdit.statut_compte.value}</span> → <span style='color: green;'>{item.statut_compte.value}</span></li>"
        )

    print(len(modifications))
    
    personnelToEdit.role = item.role
    personnelToEdit.statut_compte = item.statut_compte
    personnelToEdit.poste = item.poste
    
    if modifications:
        etab_ = await Etablissement.get_or_none(id=item.etablissement_id)

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2c3e50;">Mise à jour de votre compte personnel</h2>
                <p>Bonjour,</p>
                <p>
                    Votre profil dans l'établissement <strong>{etab_.nom}</strong> a été mis à jour.
                </p>
                <p>Voici les champs qui ont été modifiés :</p>

                <ul style="font-size: 16px; color: #333;">
                    {''.join(modifications)}
                </ul>

                <p>
                    Si vous constatez une erreur, merci de contacter l'administration de votre établissement.
                </p>

                <hr style="margin-top: 40px;">
                <p style="font-size: 12px; color: #888;">
                    Ceci est un message automatique, veuillez ne pas y répondre.
                </p>
            </body>
        </html>
        """

        await send_email(
            subject="Mise à jour de votre compte personnel",
            to=item.email,
            body=html_content
        )


        
        
        
    
    await personnelToEdit.save()
    return {
        "message" : "Modifier Personnel",
        "personnel" : personnelToEdit
    }


@router.delete("/{id_}")
async def deletPersonnel(id_ : int):
    personnelToDelete = await Personnel.get_or_none( id = id_)
    if not personnelToDelete:
        return {
            "message" : "Introuvable personnel"
        }
    
    await personnelToDelete.delete()
    return {"message" : "Personnel supprimer"}