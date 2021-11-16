from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from models.db import Users, Rooms, add_fbid, uri, add_user, add_room, del_room, check_user, check_fb_user, list_of_rooms, add_fbid
from pysrc.search import ope
from worker import conn
from datetime import timedelta
import datetime, re, os, logging
import traceback

app = Flask(__name__)
app.logger.debug('DEBUG')
app.logger.info('INFO')
app.logger.warning('WARNING')
app.logger.error('ERROR')
app.logger.critical('CRITICAL')
logging.basicConfig(level=logging.INFO)

# zip利用
app.jinja_env.filters['zip'] = zip

# セッションスコープ 暗号化とセッションの自動破棄時間
app.secret_key = 'abcdefghijklmn'
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
    return False
def login_user(user):
    session['id'] = user.id
    session['name'] = user.name
    session['flag'] = True
    session['last_action'] = datetime.datetime.now()
    if user.fbid:
        session['fb'] = True

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
                login_user(user)
                return render_template('login_confirm.html', name = session['name'], id = session['id'])
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
        if session['flag']:
            if session['fbid']:
                return redirect('/')
            else:
                add_fbid(session['id'], fbid)
                return redirect('/')
        else:
            print('6')
            user = check_fb_user(fbid)
            if user:
                print('7')
                login_user(user)
                print('8')
                return render_template('login_confirm.html', name = session['name'], id = session['id'])
            else:
                print('9')
                new_user = Users(name, fbid, 'fb')
                add_user(new_user)
                print('10')
                return redirect('/')
    except Exception as e:
        print(f'{e}')

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

# 物件検索
@app.route('/search', methods=['GET','POST'])
def search():
    if session_time_check():return redirect('/')

    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        station = request.form['station']
        min = request.form['min']
        times = request.form['times']
        rent = request.form['rent']
        walktime = request.form['walktime']
        # Flaskは同名formは最初のvalueを送るので、配列化し最後の一つを取り出す。
        sites = [request.form.getlist('suumo')[-1], request.form.getlist('athome')[-1], request.form.getlist('homes')[-1]]
        sites = [True if i == 'True' else False for i in sites]
        q = Queue(connection=conn)
        results = q.enqueue(ope, station, min, times, rent, walktime, sites, job_timeout=6000)
        return render_template('result.html', results = results,station=station,min=min,times=times,rent=rent,walktime=walktime,l=len(results))
    else:
        redirect('/')

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)