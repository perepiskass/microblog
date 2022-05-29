# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from appPackage import appFlask, db
from flask_login import current_user, login_user, logout_user, login_required
from appPackage.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from appPackage.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, EmptyForm
from appPackage.email import send_password_reset_email
from flask_babel import _, get_locale
# from guess_language import guess_language
from appPackage.translate import translate, guess_language

@appFlask.route('/', methods=['GET', 'POST'])
@appFlask.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, appFlask.config['POSTS_PER_PAGE'], False)  #формирует список сообщений для пользователя по группам их ко-во по POST_PER_PAGE 
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

#страница с сообщениями от всех пользователей, без возможности добаить свое сообщение.
@appFlask.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, appFlask.config['POSTS_PER_PAGE'], False) #формирует список всех сообщений по группам их ко-во по POST_PER_PAGE 
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

    
@appFlask.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:                                       #если текущий пользователь уже зарегестрирован то возвращается стартовая страница
        return redirect(url_for('index'))
    form = LoginForm()                                                      #создаем объект формы ввода
    if form.validate_on_submit():                                           #если данные введены
        user = User.query.filter_by(username=form.username.data).first()    #получаем из БД объект пользователя по имени, первое совпадение
        if user is None or not user.check_password(form.password.data):     #если объект = None или пароль не совпадает выдаем ошибку
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)                    #иначе запоминаем пользователя, переменная current_user-установлена, и св-во remember_me для сессии
        next_page = request.args.get('next')                                #смотрим в URL на значение атрибута next
        if not next_page or url_parse(next_page).netloc != '':              #если next не установлен или установлен полный путь с именем домена
            next_page = url_for('index')                                    #то переходим на страницу index
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)        #генерим страницу при входе впервые


@appFlask.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@appFlask.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@appFlask.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, appFlask.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

#запись последнего времени посещения пользователя, выполняется перед любой функцией просмотра
@appFlask.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())    #перед каждым запросом заносим локаль в переменную, для использования во временных метках


@appFlask.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),form=form)


@appFlask.route('/follow/<username>')
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@appFlask.route('/unfollow/<username>')
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@appFlask.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


@appFlask.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@appFlask.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})