from app.data.models import Timeslot, Registration
from app.data import utils as mutils

def get_timeslots(id=None, first=False):
    try:
        timeslots = Timeslot.query
        if id:
            timeslots = timeslots.filter(Timeslot.id == id)
        if first:
            timeslot = timeslots.first()
            return timeslot
        timeslots = timeslots.all()
        return timeslots
    except Exception as e:
        mutils.raise_error('could not get timeslots', e)
    return None


def get_first_timeslot(id=None):
    return get_timeslots(id=id, first=True)


# return all timeslots where there is no Registration referring to it.
def get_free_timeslots():
    try:
        timeslots = Timeslot.query.join(Registration, isouter=True).filter(Registration.id==None)
        timeslots = timeslots.all()
        return timeslots
    except Exception as e:
        mutils.raise_error('could not get free timeslots', e)
    return None
