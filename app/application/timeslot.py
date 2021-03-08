from app.data import settings as msettings, timeslot as mtimeslot, utils as mutils
import json



def get_default_values():
    try:
        timeslot_template = json.loads(msettings.get_configuration_setting('registration-timeslot-template'))
        timeslots = mtimeslot.get_timeslots()
        timeslots_data = []
        for timeslot in timeslots:
            formio = timeslot.ret_formio()
            formio['timeslot-date'] = mutils.datetime_to_formiodate(formio['timeslot-date'])
            timeslots_data.append(formio)
        ret = {
            'template': timeslot_template,
            'timeslots': timeslots_data
        }
        return ret
    except Exception as e:
        mutils.raise_error(f'could not get default timeslot values', e)
    return None


