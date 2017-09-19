from data.models import OfficerHistory, Officer, PoliceUnit


def create_officer_history(officer, unit, start_date, end_date, import_db='default'):
    OfficerHistory.objects.using(import_db).create(
        officer=officer, unit=unit, effective_date=start_date, end_date=end_date
    )


def import_officer_history(row, import_db='default'):
    officer = Officer.objects.using(import_db).get(id=row['officer_id'])
    unit = PoliceUnit.objects.using(import_db).filter(unit_name=str(row['unit']).zfill(3)).first()
    start_date = row['start_date']
    end_date = row['end_date']

    history = OfficerHistory.objects.using(import_db).filter(officer=officer, unit=unit).last()
    if not history:
        create_officer_history(officer, unit, start_date, end_date, import_db)
    else:
        if end_date:
            if end_date != str(history.end_date):
                create_officer_history(officer, unit, start_date, end_date, import_db)
        elif start_date:
            if history.end_date and start_date > str(history.end_date):
                create_officer_history(officer, unit, start_date, end_date, import_db)
            elif history.effective_date and start_date < str(history.effective_date):
                create_officer_history(officer, unit, start_date, end_date, import_db)
            elif not history.effective_date:
                history.effective_date = start_date
                history.save()
