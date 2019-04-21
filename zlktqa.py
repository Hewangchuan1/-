#encoding: utf-8

from flask import Flask,render_template,request,redirect,url_for,session,g,Response,send_file,jsonify
import config
from models import User,Question,Answer,Photo
from exts import db
from decorators import login_required
from sqlalchemy import or_
from scipy import misc
import numpy as np
from PIL import Image
import simplejson

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
import pymysql
pymysql.install_as_MySQLdb()
import os

@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }

    return render_template('index.html',**context)


@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 如果想在31天内都不需要登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号码或者密码错误，请确认后再登录！'

@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 手机号码验证，如果被注册了，就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号码已被注册，请更换手机号码！'
        else:
            # password1要和password2相等才可以
            if password1 != password2:
                return u'两次密码不相等，请核对后再填写！'
            else:
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登录的页面
                return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    # session.pop('user_id')
    # del session['user_id']
    session.clear()
    return redirect(url_for('login'))


@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question=question_model)


@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content)
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))


@app.route('/search/')
def search():
    q = request.args.get('q')
    # title,content
    # 或
    # condition = or_(Question.title.contains(q),Question.content.contains(q))
    # questions = Question.query.filter(condition).order_by('-create_time')
    # 与
    questions = Question.query.filter(Question.title.contains(q),Question.content.contains(q))
    return render_template('index.html',questions=questions)


 
@app.route('/up_photo/', methods=['GET','POST'])
@login_required
def up_photo():
    if request.method == 'POST':
        print('True')
        img = request.files.get('fileList')
        print(img.filename)
        im = misc.imread(img)
        path = os.path.dirname(__file__)
        print('g.user is ', g.user.username)
        if not os.path.exists(path):
            os.makedirs(path)
        basepath = os.path.dirname(__file__)+'/static/photo'+'/'+g.user.username
        print(basepath)
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        #########产生JK序列#########
        JK = generate_JK(im)
        #########加密算法#########
        miwen = jiami(im, np.array(JK))
        miwen = Image.fromarray(miwen.astype(np.uint8))
        filepath = os.path.join(basepath, img.filename)
        miwen.save(filepath)
        photo_exit = Photo.query.filter(Photo.photoname == img.filename).all()
        usernames = []
        for k in photo_exit:
            usernames.append(k.username)
        print(usernames)
        print(g.user.username)
        if photo_exit is None:
            photo_new = Photo(username=g.user.username, photoname=img.filename, photopath='http://127.0.0.1:4241/static/photo/'+g.user.username+'/'+img.filename)
            db.session.add(photo_new)
            db.session.commit()
        elif g.user.username not in usernames:
            photo_new = Photo(username=g.user.username, photoname=img.filename,
                              photopath='http://127.0.0.1:4241/static/photo/' + g.user.username + '/' + img.filename)
            db.session.add(photo_new)
            db.session.commit()
        return jsonify(g.user.username, img.filename)
        # for file in request.files.getlist('file'): # 这里改动以存储多份文件
        #     if file and allowed_file(file.filename):
        #         filename = secure_filename(file.filename)
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    else:
        return render_template('up_photo.html')

@app.route('/download/', methods=['GET', 'POST'])
@login_required
def download():
    if request.method == 'GET':
        photo_exit = Photo.query.filter(Photo.username==g.user.username).all()
        context = {
            'photos':photo_exit
        }
        print(photo_exit[0].photopath)
        return render_template('download.html', **context)
    elif request.method == 'POST' :
        print('True')
        img = request.files.get('fileList')
        print(img.filename)
        im = misc.imread(img)
        path = os.path.dirname(__file__)
        print('g.user is ', g.user.username)
        if not os.path.exists(path):
            os.makedirs(path)
        basepath = os.path.dirname(__file__)+'/static/photo'+'/'+g.user.username
        print(basepath)
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        #########产生JK序列#########
        JK = generate_JK(im)
        ########解密算法#########
        miwen = jiemi(im, np.array(JK))
        miwen = Image.fromarray(miwen.astype(np.uint8))
        savepath = 'D:/yunjiami/'
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        savepath = os.path.join(savepath, img.filename)
        miwen.save(savepath)
        return jsonify(savepath)
@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user

@app.context_processor
def my_context_processor():
    if hasattr(g,'user'):
        return {'user':g.user}
    return {}

# before_request -> 视图函数 -> context_processor

def generate_JK(ima):
    length = ima.shape[0]*ima.shape[1]
    fbconnection = [0,1,0,1,0,1,0,0,1,1,0,1]   #12级本原多项式系数
    n = len(fbconnection)
    N = 2**n-1
    register = [1] + [0 for i in range(0,n-2)] + [0]
    mseq = []
    mseq.append(register[n-1])
    for i in range(1, N):
        newregister = []
        newregister.append(np.sum(np.multiply(np.array(fbconnection), np.array(register)))%2)
        newregister += register[0:n-1]
        register = newregister
        mseq.append(register[n-1])
    x1 = []
    for ii in range((length*8)//N+1):
        x1[ii*N:(ii+1)*N] = mseq

    fbconnection1 = [0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1]  # 13级本原多项式系数
    n1 = len(fbconnection1)
    N1 = 2 ** n1 - 1
    register1 = [1] + [0 for i in range(0, n1 - 2)] + [1]
    mseq1 = []
    mseq1.append(register1[n1 - 1])
    for i in range(1, N1):
        newregister1 = []
        newregister1.append(np.sum(np.multiply(np.array(fbconnection1), np.array(register1))) % 2)
        newregister1 += register1[0:n1 - 1]
        register1 = newregister1
        mseq1.append(register1[n1 - 1])
    x2 = []
    for ii in range((length*8)//N1+1):
        x2[ii * N1:(ii+1) * N1] = mseq1

    print(len(x1))
    print(len(x2))
    JK_pre = []
    JK_pre.append(x1[0])
    for k in range(1,length*8):
        JK_pre.append(((x1[k]+x2[k]+1)*JK_pre[k-1]+x1[k])%2)
    JK = JK_pre
    return JK

def jiami(ima, JK):
    JK = JK[:ima.shape[0]*ima.shape[1]*8]

    print(JK[-50:])
    print('ima的最后十个数', ima[:,:,0].flatten()[-10:])
    JK = JK.reshape(ima.shape[0]*ima.shape[1], 8)
    ima_str = [bin(i)[2:].rjust(8, '0') for i in ima[:, :, 0].flatten()]
    print('ima_str的最后一个数',ima_str[-1])
    miwen = ['' for i in range(ima.shape[0]*ima.shape[1])]
    for i in range(0, 8//2):
        JK_C = JK[:, 2*i:2*(i+1)]
        ima_01_str = [ima_str[j][2*i:2*(i+1)] for j in range(len(ima_str))]
        ima_01_int = np.array([int(i,2) for i in ima_01_str])
        ima_0_str = [ima_01_str[j][0] for j in range(len(ima_01_str))]
        ima_0_int = np.array([int(j,2) for j in ima_0_str])
        ima_1_str = [ima_01_str[j][1] for j in range(len(ima_01_str))]
        ima_1_int = np.array([int(j,2) for j in ima_1_str])
        JK_C_0 = list(map(str, JK_C[:, 0]))
        JK_C_1 = list(map(str, JK_C[:, 1]))
        JK_C_str = [JK_C_0[j]+JK_C_1[j] for j in range(len(JK_C_0))]
        JK_C_int = np.array([int(j,2) for j in JK_C_str])
        result = (np.multiply(ima_1_int, ima_01_int) - ima_1_int - np.multiply(ima_0_int, np.array([i^1 for i in ima_1_int])) + JK_C_int)%4
        result_str = [bin(i)[2:].rjust(2, '0') for i in result]
        miwen = [miwen[j]+result_str[j] for j in range(len(result_str))]
    # print('最后出来的值是',ima_1_int[-1], ima_01_int[-1], ima_0_int[-1], JK_C_int[-1], result[-1],
    #       (np.multiply(ima_1_int, ima_01_int) - ima_1_int - np.multiply(ima_0_int, np.array([i^1 for i in ima_1_int])) + JK_C_int)[-1])
    miwen = np.array([int(i,2) for i in miwen])
    miwen = miwen.reshape(ima.shape[0], ima.shape[1])
    print('加密之后的密文的最后十个数字：', miwen.flatten()[-10:])
    return  miwen

def jiemi(ima, JK):
     JK = JK[:ima.shape[0] * ima.shape[1] * 8]
     JK = JK.reshape(ima.shape[0] * ima.shape[1], 8)
     ima_str = [bin(i)[2:].rjust(8, '0') for i in ima.flatten()]
     print('ima_str的值是', ima_str)
     miwen = ['' for i in range(ima.shape[0] * ima.shape[1])]
     for i in range(0, 8 // 2):
         JK_C = JK[:, 2 * i:2 * (i + 1)]
         JK_C_0 = list(map(str, JK_C[:, 0]))
         JK_C_1 = list(map(str, JK_C[:, 1]))
         JK_C_str = [JK_C_0[j] + JK_C_1[j] for j in range(len(JK_C_0))]
         JK_C_int = np.array([int(j,2) for j in JK_C_str])
         ima_01_str = [ima_str[j][2*i:2*(i+1)] for j in range(len(ima_str))]
         ima_01_int = np.array([int(i,2) for i in ima_01_str])
         result_2 = (JK_C_int-ima_01_int)%4
         print('result_2的值是,', result_2)

         b = np.zeros([len(result_2),], dtype=np.int8)
         b[result_2==3]=1
         result_dec_3 = b

         b = np.zeros([len(result_2),], dtype=np.int8)
         b[result_2==2]=3
         result_dec_2 = b

         b = np.zeros([len(result_2),], dtype=np.int8)
         b[result_2==1]=2
         result_dec_1 = b

         result_2_dec = result_dec_3+result_dec_2+result_dec_1

         result_2_base = [bin(i)[2:].rjust(2, '0') for i in result_2_dec.flatten()]
         miwen = [miwen[j] + result_2_base[j] for j in range(len(result_2_base))]

     miwen = np.array([int(j,2) for j in miwen])
     miwen = miwen.reshape(ima.shape[0], ima.shape[1])

     return miwen

# if __name__ == '__main__':
#     app.run(port=4241, debug=True)

#痛苦总是走在勇气前面，然后哀嚎，然后忍耐，然后改变
