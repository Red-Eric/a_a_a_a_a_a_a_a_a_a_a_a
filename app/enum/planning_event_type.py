from enum import Enum

class PlanningEventType(str, Enum):
    ABSENCE = "Absence"
    FORMATION = "Formation"
    MISSION = "Mission"
    TACHE = "Tâche"
    REUNION = "Réunion"
    
    