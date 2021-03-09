from flask_login import login_required, current_user
from app.data.registration import format_data, pre_filter
from app import db, log, admin_required, data
from . import registration
from app.presentation.view import base_multiple_items
from app.data.models import Registration, Timeslot

@registration.route('/registration', methods=['GET', 'POST'])
@login_required
def show():
    return base_multiple_items.show(configuration)


@registration.route('/registration/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    return base_multiple_items.ajax(configuration)


@registration.route('/registration/table_action', methods=['GET', 'POST'])
@login_required
def table_action():
    pass


@registration.route('/registration/item_action/<string:action>', methods=['GET', 'POST'])
@login_required
def item_action(action=None):
    pass


configuration = {
    'view': 'registration',
    'title': 'Registraties',
    'buttons': [],
    'delete_message': u'',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'Tijdslot', 'data': 'timeslot-date', 'order_by': Timeslot.date, 'orderable': True, 'width': '15%'},
        {'name': 'Leerling', 'data': 'student_name', 'width': '15%'},
        {'name': 'Ouder', 'data': 'parent_name', 'width': '15%'},
        {'name': 'Meeting', 'data': 'timeslot-meeting-url'},
        ],
    'filter': [],
    'item': {},
    'href': [],
    'pre_filter': pre_filter,
    'format_data': format_data,
    'default_order': (1, 'asc'),
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
