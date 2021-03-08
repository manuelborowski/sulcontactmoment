var _form = null;
$(document).ready(function () {
    socketio.start(null, null);
    socketio.subscribe_on_receive("settings", socketio_receive_settings);
    Formio.createForm(document.getElementById('configuration-settings'), data.template).then((form) => {
        _form = form
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        form.on('submit', function(submission) {
            socketio_transmit_setting('data', JSON.stringify((submission.data)))
        })
    });
});


function socketio_receive_settings(type, data) {
    _form.emit('submitDone')
    setTimeout(function() {$("#configuration-settings .alert").css("display", "none");}, 1000);
    if (!data.status) {
        bootbox.alert("Opgepast, er is volgende fout opgetreden:<br>" + data.message);
    }

}


function socketio_transmit_setting(setting, value) {
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}