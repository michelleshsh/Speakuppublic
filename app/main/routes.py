from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db, oa
from flask_babel import get_locale
from app.main import bp
from app.main.forms import EditProfileForm,EmptyForm, PostForm, DateForm
from app.models import User, Post, Hansard, MajorHeading, Speech, Rep
import json
import requests
import pandas
from guess_language import guess_language
from app.translate import translate


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, 3, False)
    return render_template('index.html', title='Home',
                           posts=posts.items)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, 3, False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('usertest.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.postcode = form.postcode.data
        current_user.set_representativeandconst()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.postcode.data = current_user.postcode
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('explore.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/hansard',methods=['GET', 'POST'])
@login_required
def main_hansard():
    obj = Hansard.query.order_by(Hansard.date.desc()).first().date
    return redirect(url_for('main.hansard',date=obj))


@bp.route('/hansard/<date>',methods=['GET', 'POST'])
@login_required
def hansard(date):
    hansard = Hansard.query.filter_by(date=date).first()
    hansards = Hansard.query.all()
    dates = []
    for date in hansards:
        dates.append(str(date.date).replace("-","/"))
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('main.index'))
    form1 = PostForm(identifier="FORM1")
    form2 = DateForm(identifier="FORM2")
    if form1.identifier.data == 'FORM1' and form1.validate_on_submit():
        speech = Speech.query.filter_by(exact_id=form1.hidden.data).first()
        language = guess_language(form1.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form1.post.data, author=current_user, speech= speech,
                    language=language)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    if form2.identifier.data == 'FORM2' and form2.validate_on_submit():
        date = form2.date.data.strftime("%Y-%m-%d")
        return redirect(url_for('main.hansard',date=date))
    return render_template('hansard.html',data = hansard, dates = dates, form1 = form1, form2=form2)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate([request.form['text']],
                                      request.form['dest_language'])})
