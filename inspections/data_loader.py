# Imports from python.  # NOQA
from copy import deepcopy


# Imports from inspections.
from inspections.models import (  # NOQA
    Establishment,
    Inspection,
    Violation
)


def save_establishment(establishment_obj):
    '''TK.

    '''
    normalized_establishment = deepcopy(establishment_obj)

    inspections = normalized_establishment.pop('inspections')

    establishment_model = Establishment(**normalized_establishment)

    establishment_model.save()

    for inspection_obj in inspections:
        save_inspection(inspection_obj, establishment_model)


def save_inspection(inspection_obj, establishment_model):
    '''TK.

    '''
    normalized_inspection = deepcopy(inspection_obj)

    violations = normalized_inspection.pop('violations')

    inspection_model = Inspection(**normalized_inspection)

    inspection_model.establishment = establishment_model

    inspection_model.save()

    for violation_obj in violations:
        save_violation(violation_obj, inspection_model)


def save_violation(violation_obj, inspection_model):
    '''TK.

    '''
    normalized_violation = deepcopy(violation_obj)

    # violation_obj['infraction_category'] = violation_obj.pop(
    #     'rule_violated'
    # )
    # violation_obj['inspector_comment'] = violation_obj.pop(
    #     'corrective_action'
    # )
    # violation_obj['additional_information'] = violation_obj.pop(
    #     'extra_information'
    # )
    # violation_obj['corrected_during_inspection'] = None

    violation_model = Violation(**normalized_violation)
    violation_model.inspection = inspection_model

    # if violation_model.inspector_comment is None:
    #     violation_model.inspector_comment = ''

    violation_model.save()
