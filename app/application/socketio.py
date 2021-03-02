from flask import request
from flask_socketio import emit, join_room, leave_room, close_room
from app import socketio

socketio_cbs = {}


@socketio.event
def subscribe_to_room(message):
    join_room(message['room'])


@socketio.event
def leave_room(message):
    leave_room(message['room'])


@socketio.on
def close_room(message):
    close_room(message['room'])


@socketio.event
def send_to_server(msg):
    if msg['type'] in socketio_cbs:
        socketio_cbs[msg['type']](msg, request.sid)


@socketio.on('disconnect')
def disconnect_socket():
    print(f'{request.sid} is leaving')
    if 'disconnect' in socketio_cbs:
        socketio_cbs['disconnect'](None, request.sid)


@socketio.event
def connect():
    pass


def subscribe_on_type(type, cb):
    socketio_cbs[type] = cb


def send_to_room(msg, room):
    emit('send_to_client', msg, room=room)


def broadcast_message(msg):
    emit('send_to_client', msg, broadcast=True, namespace='/')


def send_to_client(client_sid, type, msg):
    emit(type, msg, room=client_sid)