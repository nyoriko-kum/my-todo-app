from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from flask_todo.models import User, Task
from datetime import datetime, date
from flask_todo import db, login_manager
import re

#bpモジュールのインスタンス化
#Blueprintとは機能ごとにファイルを分割し管理しやすくするために利用する機能です
#bluePrintをつかえば、機能ごとにファイルをわけられちゃうんですね！！gakupuruです！
#引数では、todo_appと言う名前で纏めるようにしています。url_prefixには纏めたファイルをurlで纏める事が出来ますが今回は引数無し
#url_prefixを指定すると例；url_prefix="/admin"とかすると/admin/home.htmlや/admin/user.htmlって感じでurlが指定できます。
bp = Blueprint('todo_app', __name__, url_prefix='')

#初期画面はhome.htmlを表示させます
@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("todo_app.home"))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    #formからemailとpasswordを取得
    email = request.form.get('email')
    password = request.form.get('password')
    #取得したemailとデータベースのemailが一致するもののパスワードを取得
    if request.method == 'POST':
        #これはオブジェクトになっています。Userテーブルにあるemailが同じやつをクエリしてくれています。
        #なんで、この関数が使えるかというと、select～は、一番最初のimportでＵｓｅｒデータベースとともにmodelsをインポートしています。
        user = User.select_by_email(email)

#取得したパスワードとデータベースのパスワードが等しければログインセッション完了し、ホームを表示
#これは、modelsの中にあるvalidate_passwordを呼び出して自分自身のpasswordにpasswordを代入。
        if user and user.validate_password(password):
            #ユーザーをログイン状態にするための関数:login_user
            #指定されたユーザーオブジェクトをログインセッションに登録し、ログイン状態を保持し、保護されたエンドポイントへのアクセスができるようになる。
            login_user(user)
            #@login_requiredでログイン未完了でもともとリクエストしたページにlogin()できずに遷移してきた場合は、urlは/next=user.htmlとして元々実行したかったURLが格納されちるので、そこに遷移させます。
            next = request.args.get('next')
            if not next:
                #nextがなかった場合のデフォルトの遷移先を指定しています。
                next = url_for('todo_app.user')
            return redirect(next)

#一致しなかった場合には、ログイン画面にもどる。
    return render_template('login.html', last_access=datetime.now())



#ユーザー登録
@bp.route('/register',methods=['GET', 'POST'])
def register():
    #書き込まれた項目を取得する
    #get()の引数は、それぞれinputタグのnameオプションになります
    username = request.form.get('name')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    #メールアドレスの形式を正規表現で想定している
    #任意の文字が一つ以上＋　.は任意の文字
    #^は先頭を指定^は行の先頭を表し、[a-zA-Z0-9_.+-]は、アルファベット（大文字・小文字）、数字、アンダースコア、ピリオド、プラス、ハイフンのいずれか1文字にマッチすることを意味します
    #$は最後を指定
    pattern = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    #POSTリクエストの場合
    if request.method == 'POST':
        #どこかに空欄がある場合
        if username == '' or email == '' or password1 == '' or password2 == '':
            flash('空のフォームがあります')
        #パスワードが一致しない場合
        elif password1 != password2:
            flash('パスワードが一致しません')
        #メールアドレスの形式になっていない場合
        elif re.match(pattern, email) is None:
            flash('メールアドレスの形式になっていません')
        #すべて正しく入力された場合
        else:
            #書き込まれた項目を取得する
            #全ての項目で正しく入力された場合は、フォームから取得した文字列をインスタンス化した引数に割り当てます
            user = User(
                    email = email,
                    username = username,
                    password = password1
                    )
            #databaseにあるメールアドレスを取得する
            #データベースにメールアドレスが登録されていなければＮｏｎｅになる
            DBuser = User.select_by_email(email)

            #メールアドレスが取得された場合
            if DBuser != None:
                flash('登録済みです')
            #メールアドレスが取得されなかった場合
            else:
                #データベースへの書き込みを行う
                #try-except文は、errorが出る場合を想定して記載する場合に使います。
                #今回の場合は、トランザクションの保証です。データベースに書き込みがうまくいかなかったら、動作を巻き戻す処理が入っています。
                #finally節は、エラーが起ころうが起こらなかろうが、最後に必ず処理する内容を書き込みます。今回はセッションを切るということです。
                try:
                    #データベースとの接続を開始する
                    #with文とは、ファイル操作や通信などの開始時の前処理と終了時の後処理など必須となる処理を自動で実行してくれるものでこれを使わないとファイルオープン、ファイルクローズを書かないといけなくなる。
                    with db.session.begin(subtransactions=True):
                        #データベースに書き込むデータを用意する
                        db.session.add(user)
                        #データベーへの書き込みを実行する
                    db.session.commit()
                    #書き込みがうまくいかない場合
                except:
                    #データベースへの書き込みを行わずにロールバックする
                    db.session.rollback()
                    #raiseでraise eとするとスタックトレース（エラーをトレースする機能）でraise eで再度エラーを送出してしまうので、エラー箇所をトレースしにくい。raiseとするとエラーがそのまま送出されてトレースがそのままになる。
                    raise
                #データベースとの接続を終了する
                finally:
                    db.session.close()
                #成功すればlogin.htmlに遷移する
                return redirect(url_for('todo_app.login'))
    return render_template('register.html')

#タスク一覧
@bp.route('/user' ,methods=['GET', 'POST'])
#ログインできているときに処理を実行できる
@login_required
def user():
    if request.method == 'GET':
#現在ログインしている人のタスクをタスク終了日が早い順にすべて取得
        tasks = Task.query.filter(Task.user_id == current_user.get_id()).order_by(Task.end_time).all()
    return render_template('user.html',tasks=tasks, today=date.today())    

#新規タスク作成
@bp.route('/create_task',methods=['GET', 'POST'])
#ログインできているときに処理を実行できる
@login_required
def create_task():
#POSTリクエストの場合
    if request.method == 'POST':
#書き込まれた項目を取得する
        title = request.form.get('title')
        detail = request.form.get('detail')
#request.form.get('end_time')で取得した文字列を「年-月-日」に変換しています。
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%d')

#どこかに空欄がある場合
        if title == '' or detail == '' or end_time == '':
            flash('空のフォームがあります')
            return render_template('create_task.html')
#すべて正しく入力された場合
        else:
#取得した項目をデータベースのカラム名に紐づける
            create_task = Task(
                    title = title,
                    end_time = end_time,
                    detail = detail,
                    user_id = current_user.get_id()
                    )
#データベースへの書き込み（create処理）
            try:
                with db.session.begin(subtransactions=True):
                    db.session.add(create_task)
                db.session.commit()
                return redirect(url_for('todo_app.user'))
            except:
                db.session.rollback()
                return render_template('create_task.html')
            finally:
                db.session.close()

            return redirect(url_for('todo_app.user'))
    return render_template('create_task.html')

#　タスク詳細
@bp.route('/detail/<int:id>')
# ログインできているときに処理を実行できる
@login_required
def detail_task(id):
    #選択したタスクの情報を取得（read処理）
    #自分はこう書いた⇒Task.query.filter_by(id = id).first()これでもいいけど、主キーの場合はget()のほうが高速で簡潔でよい。
    task = Task.query.get(id)

    return render_template('detail.html', task=task, today=date.today())

#　タスク削除
@bp.route('/delete/<int:id>')
@login_required
def delete_task(id):
    #選択したタスクの情報を取得
    task = Task.query.get(id)
    #データベースへの書き込み（Delete処理）
    #try節を使用した方がtryが失敗したときにexcept節が実行される。さらにfinally節で必ずセッションがクローズされるので
    #トランザクションの保証ができる。
    try:
        #サブトランザクション管理にすることで、そのサブトラだけをクローズできるので、親トラは無事。
        with db.session.begin(subtransactions=True):
            db.session.delete(task)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    finally:
        db.session.close()

    return redirect(url_for('todo_app.user'))


# タスク更新機能
@bp.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update_task(id):
    #選択したタスクの情報を取得
    task = Task.query.get(id)
    #ＧＥＴリクエストの場合
    if request.method == 'GET':
        return render_template('update.html', task=task, today=date.today())
    else:
        task.title = request.form.get('title')
        task.detail = request.form.get('detail')
        task.end_time = datetime.strptime(request.form.get("end_time"), '%Y-%m-%d')
        update_task = Task(
                title = task.title,
                end_time = task.end_time,
                detail = task.detail
                )
        try:
            # Update処理のデータベースへの書き込みは、既にデータベースから情報を取得しているので、接続を開始するbeginやデータのaddは必要ありません。commit()だけになります。
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()

        return redirect(url_for('todo_app.user'))
