from flask import render_template
from flask_login import login_required

from app import admin_required
from app.application import socketio as msocketio, utils as mutils
from . import settings
from app.application import settings as msettings


@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    return render_template('/settings/settings.html',
                           settings_form=settings_formio, default_settings=default_settings)


def update_settings_cb(msg, client_sid=None):
    data = msg['data']
    msettings.set_configuration_setting(data['setting'], data['value'])


msocketio.subscribe_on_type('settings', update_settings_cb)

from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
    {
        "display": "form",
        "components": [
            {
                "title": "BEZOEKERS : Registratie en smartschoolbericht template",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate1",
                "type": "panel",
                "label": "BEZOEKERS : Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "contactmoment registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingsbericht: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-message-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingsbericht: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-message-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Tijdsloten",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate2",
                "type": "panel",
                "label": "BEZOEKERS : Registratie en smartschoolbericht template",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Tijdslot template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "registration-timeslot-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Smartschoolbericht server settings",
                "theme": "primary",
                "collapsible": true,
                "key": "eMailServerSettings",
                "type": "panel",
                "label": "E-mail server settings",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Aantal keer dat een bericht geprobeerd wordt te verzenden",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "message-send-max-retries",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Tijd (seconden) tussen het verzenden van berichten",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "message-task-interval",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Max aantal berichten per minuut",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "messages-per-minute",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Basis URL",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "key": "base-url",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Berichten mogen worden verzonden",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "enable-send-message",
                        "type": "checkbox",
                        "input": true
                    }
                ],
                "collapsed": true
            }
        ]
    }