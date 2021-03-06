var _form
$(document).ready(function () {
    // socketio.subscribe_on_receive("settings", socketio_receive_settings);
    Formio.createForm(document.getElementById('timeslot-settings'), data.template).then((form) => {
        _form = form;
        var timeslot_component = form.getComponent("timeslot-list");
        $.each(data.timeslots, function (i, v) {
            timeslot_component.addRow();
            timeslot_component.setRowComponentsData(i, v);
        });
        // timeslot_component.setRowComponentsData(0, data.timeslots[0]);
        // setTimeout(function () {
        //     console.log('after 1 sec');
        // $.each(data.timeslots, function (i, v) {
        //     timeslot_component.setRowComponentsData(i, v);
        // });}, 1000);
        // // form.on('change', function (changed) {
        // //     socketio_transmit_setting(changed.changed.component.key ,changed.changed.value)
        // // });
        // form.on('initialized', function() {
        //     console.log("done rendering");
        // })
        timeslot_component.redraw();
        timeslot_component.restoreComponentsContext();
        form.on('submit', function(submission) {
            console.log(submission);
        })
    });
    _form.submit();
});


// function socketio_receive_settings(type, data) {
// }
//
//
// function socketio_transmit_setting(setting, value) {
//     socketio.send_to_server('settings', {setting: setting, value: value});
//     return false;
// }