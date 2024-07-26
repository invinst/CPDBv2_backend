from .update_officer_manager import UpdateOfficerManager
from .update_officer_history_manager import UpdateOfficerHistoryManager

from .update_allegation_manager import UpdateAllegationManager
from .update_officer_allegation_manager import UpdateOfficerAllegationManager
from .update_investigator_manager import UpdateInvestigatorManager
from .update_complainant_manager import UpdateComplainantManager
from .update_victim_manager import UpdateVictimManager

from .update_trr_manager import UpdateTRRManager
from .update_trr_status_manager import UpdateTRRStatusManager
from .update_action_response_manager import UpdateActionResponseManager
from .update_weapon_discharge_manager import UpdateWeaponDischargeManager
from .update_subject_weapon_manager import UpdateSubjectWeaponManager

from .update_award_manager import UpdateAwardManager
from .update_salary_manager import UpdateSalaryManager

update_manager_dict = {
    'Officer': UpdateOfficerManager,
    'OfficerHistory': UpdateOfficerHistoryManager,
    'Allegation': UpdateAllegationManager,
    'OfficerAllegation': UpdateOfficerAllegationManager,
    'Investigator': UpdateInvestigatorManager,
    'Complainant': UpdateComplainantManager,
    'Victim': UpdateVictimManager,
    "Award": UpdateAwardManager,
    "TRR": UpdateTRRManager,
    "TRRStatus": UpdateTRRStatusManager,
    "ActionResponse": UpdateActionResponseManager,
    "SubjectWeapon": UpdateSubjectWeaponManager,
    "WeaponDischarge": UpdateWeaponDischargeManager,
    "Salary": UpdateSalaryManager
}


def get(manager_name):
    return update_manager_dict[manager_name]


def update_all(batch_size=10000, update_holding_table=True):
    for manager in update_manager_dict.values():
        manager(batch_size=batch_size).update_data(update_holding_table=update_holding_table)
