from types import MappingProxyType
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models.db import Users, Rooms, add_fbid, uri, add_user, add_room, del_room, check_user, check_fb_user, list_of_rooms, add_fbid
from pysrc.test import searching, fav_list, add_fav_room, list_of_fav, del_fav
from pysrc.db_refresh import exe
from datetime import timedelta
from pysrc import env
import datetime, re, os
import traceback

app = Flask(__name__)

# zip利用
app.jinja_env.filters['zip'] = zip

# セッションスコープ 暗号化とセッションの自動破棄時間
app.secret_key = env.APP_secret_key
app.permanent_session_lifetime = timedelta(minutes=60)
# sessionリスト id, name, flag, last_action

# db.pyのuriをデータベースURIに
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

JST = datetime.timezone(timedelta(hours=+9), 'JST')
def str_to_list(str):
    return re.sub('(\[|\'|\]|\s)', '', str).split(',')
# 20分経過で自動ログアウト
def session_time_check():
    if 'flag' in session:
        if session['flag']:
            now = datetime.datetime.now(JST)
            delta = now - session['last_action']
            if delta.total_seconds() >= 1200:
                session.pop('flag', False)
                session.pop('id', None)
                session.pop('name', None)
                session.pop('action_time', None)

                return True
            else:
                session['last_action'] = now
        else:
            return False
    return False
def login_user(user):
    session['id'] = user.id
    session['name'] = user.name
    session['flag'] = True
    session['last_action'] = datetime.datetime.now()
    if user.fbid:
        session['fb'] = True
    else:
        session['fb'] = False
    return 'ログインに成功しました'

# トップ画面へ
@app.route('/')
def index():
    if session_time_check():return redirect('/')

    return render_template('index.html')

# ログイン
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        try:
            name = request.form['name']
            password = request.form['password']
            user = check_user(name,password)
            if user:
                message = login_user(user)
                return render_template('login_confirm.html', name = session['name'], id = session['id'], m = message)
            else:
                return render_template('login.html')
        except:
            return redirect('/')
    else:
        return redirect('/')

# ログアウト
@app.route('/logout')
def logout():
    session.pop('flag', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('action_time', None)
    return redirect('/')

# ユーザー登録
@app.route('/reg', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form["name"]
        password = request.form["password"]
        new_user = Users(name, password, 'normal')
        add_user(new_user)
        return redirect('/')
    else:
        return redirect('/')

# FBログイン、登録
@app.route('/fbin', methods=['POST'])
def fbin():
    try:
        name = request.form['name']
        fbid = request.form['fbid']
        if 'flag' in session and session['flag']:
            print('session[flag] = True')
            if 'fb' in session and session['fb']:
                print(f'session[fb] = exist = {session["fb"]}')
                return redirect('/')
            else:
                print('session[fbid] = Flase')
                print(f'session[id] = {session["id"]}')
                message = add_fbid(session['id'], fbid)
                return render_template('login_confirm.html', name = session['name'], id = session['id'], m = message)
        else:               # ログアウト時
            print('session[flag] = False ')
            user = check_fb_user(fbid)
            if user:        # FBIDで検索、存在する
                print('user = True')
                message = login_user(user)
                return render_template('login_confirm.html', name = session['name'], id = session['id'], m = message)
            else:           # FBIDで検索、存在しない
                print('user = False')
                new_user = Users(name, fbid, 'fb')
                message = add_user(new_user)
                return render_template('login_confirm.html', name = session['name'], id = session['id'], m = message)
    except Exception as e:
        print(f'except:{e}')
        return redirect('/')

# ログインユーザーの登録した物件メモ一覧
@app.route('/lists/<user_id>')
def lists(user_id):
    if session_time_check():return redirect('/')

    rooms = list_of_rooms(user_id)
    
    for room in rooms:
        room.near = str_to_list(room.near)
        room.cost = str_to_list(room.cost)
        room.link = str_to_list(room.link)
        room.transfer = str_to_list(room.transfer)

    return render_template('lists.html', rooms=rooms)

# 登録メモ一覧テスト
@app.route('/fav/<user_id>')
def favlist(user_id):
    if session_time_check():return redirect('/')

    rooms = list_of_fav(user_id)
    rooms.reverse()
    return render_template('fav.html', rooms=rooms)

# 物件メモ登録確認画面
@app.route('/update', methods=['post'])
def update():
    if session_time_check():return redirect('/')

    try:
        title = request.form.get('title')
        nears = str_to_list(request.form.get('nears'))
        costs = str_to_list(request.form.get('costs'))
        links = str_to_list(request.form.get('links'))
        transfers = str_to_list(request.form.get('transfers'))
        return render_template('update.html', title=title,nears=nears,costs=costs,links=links,transfers=transfers)
    except:
        return redirect('/')

# 物件メモ登録
@app.route('/done', methods=['post'])
def done():
    if session_time_check():return redirect('/')

    if not session['flag']:
        return redirect('/')
    # 配列を文字列として格納
    title = request.form.get('title')
    nears_l = request.form.get('nears_l')
    costs_l = request.form.get('costs_l')
    links_l = request.form.get('links_l')
    transfers_l = request.form.get('transfers_l')

    try:
        new_room = Rooms(session['id'],title,nears_l,costs_l,links_l,transfers_l)
        add_room(new_room)
    except Exception as e:
        print(traceback.format_exc())

    return redirect('/')

# 物件メモ削除
@app.route('/delete', methods=['post'])
def delete():
    if session_time_check():return redirect('/')

    if session['flag']:
        ids = request.form.getlist('id')
        id = session['id']
        del_room(ids)

        return redirect(f'/lists/{id}')
    else:
        return redirect('/')

# 検索
@app.route('/search', methods=['get', 'post'])
def test():
    if session_time_check():return redirect('/')

    if request.method == 'GET':
        return render_template('search_db.html')
    elif request.method == 'POST':
        station = request.form['station']
        if len(station)==0:
            station = "駅名空白"
        mins = float(request.form['mins']) * 10000
        minp = float(request.form['minp']) * 10000
        maxp = float(request.form['maxp']) * 10000
        shikirei = float(request.form['shikirei']) * 10000
        room_size_min = float(request.form['room_size_min'])
        room_size_max = float(request.form['room_size_max'])
        ekis = searching(station, mins, minp, maxp, shikirei, room_size_min, room_size_max)
        return render_template('test.html', ekis = ekis)
    else:
        return redirect('/')

# 登録テスト
@app.route('/fav_room', methods=['post'])
def add():
    if session_time_check():return redirect('/')

    f = fav_list(session['id'], request.form['title'], request.form['address'], request.form['line1'], request.form['station1'], request.form['time1'], request.form['line2'], request.form['station2'], request.form['time2'], request.form['line3'], request.form['station3'], request.form['time3'], request.form['rent'], request.form['fee'], request.form['deposit'], request.form['key'], request.form['room_type'], request.form['room_size'], request.form['url'])
    add_fav_room(f)
    return render_template('done.html')

# 物件メモ削除テスト
@app.route('/delete_fav', methods=['post'])
def delete_fav():
    if session_time_check():return redirect('/')

    if session['flag']:
        ids = request.form.getlist('id')
        id = session['id']
        del_fav(ids,id)

        return redirect(f'/fav/{id}')
    else:
        return redirect('/')

@app.route('/alldelete')
def alldel():
    exe()
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)