# -*- coding: utf-8 -*-

from flask import redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user
from sqlalchemy import func

from app import log, db, flask_app
from . import auth
from .forms import LoginForm
from app.data.models import User
from app.presentation.layout import utils
import datetime, json

@auth.route('/', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if form.validate() and request.method == 'POST':
        user = User.query.filter_by(username=func.binary(form.username.data)).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            log.info(u'user {} logged in'.format(user.username))
            user.last_login = datetime.datetime.now()
            try:
                db.session.commit()
            except Exception as e:
                log.error(u'Could not save timestamp: {}'.format(e))
                utils.flash_plus(u'Fout in database', e)
                return redirect(url_for('auth.login'))
            # Ok, continue
            return redirect(url_for('user.show'))
        else:
            utils.flash_plus(u'Ongeldige gebruikersnaam of paswoord')
            log.error(u'Invalid username/password')
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    log.info(u'User logged out')
    logout_user()
    return redirect(url_for('auth.login'))


SMARTSCHOOL_ALLOWED_BASE_ROLES = [
    'Andere',
    'Leerkracht',
    'Directie'
]


@auth.route('/dashboard', methods=['POST', 'GET'])
def login_dashboard():
    if 'version' in request.args:
        profile = json.loads(request.args['profile'])

        if not 'username' in profile:  # not good
            log.error(u'Smartschool geeft een foutcode terug: {}'.format(profile['error']))
            return redirect(url_for('auth.login'))

        if profile['basisrol'] in SMARTSCHOOL_ALLOWED_BASE_ROLES:
            # Students are NOT allowed to log in
            user = User.query.filter_by(username=func.binary(profile['username']),
                                        user_type=User.USER_TYPE.OAUTH).first()
            if user:
                user.first_name = profile['name']
                user.last_name = profile['surname']
                user.email = profile['email']
            else:
                user = User(username=profile['username'], first_name=profile['name'], last_name=profile['surname'],
                            email=profile['email'], user_type=User.USER_TYPE.OAUTH, level=User.LEVEL.USER)
                db.session.add(user)
                db.session.flush()  # user.id is filled in
            user.last_login = datetime.datetime.now()
            login_user(user)
            log.info(u'OAUTH user {} logged in'.format(user.username))
            try:
                db.session.commit()
            except Exception as e:
                log.error(u'Could not save user : {}'.format(e))
                return redirect(url_for('auth.login'))
            # Ok, continue
            return redirect(url_for('registration.show'))
    else:
        redirect_uri = f'{flask_app.config["SMARTSCHOOL_OUATH_REDIRECT_URI"]}/dashboard'
        return redirect(f'{flask_app.config["SMARTSCHOOL_OAUTH_SERVER"]}?app_uri={redirect_uri}')
