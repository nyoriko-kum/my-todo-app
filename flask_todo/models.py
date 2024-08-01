#models.py

#flask_todoからdbとlogin_managerをインポート
#じゃあ、さっき書いたflask_todoはモジュールだったってことですね？？
from flask_todo import db, login_manager

#flask_bcryptからハッシュ系のモジュールをインポート
from flask_bcrypt import generate_password_hash, check_password_hash

#userの認証のためflask_loginからUserMixinをインポート
from flask_login import UserMixin

#sqlalchemy sqlからfuncをインポート
#データベース関数を使用する際に利用される
from sqlalchemy.sql import func

#load_user関数の登録。引数はuser_idで定義
#load_user関数は指定されたユーザーＩＤに対応するユーザーオブジェクトを返す役割をもつ
#user_loaderは、Flask-loginライブラリで使用されるデコレータ。
#@~はデコレータで、login_managerインスタンスにload_user関数を登録し、該当するユーザーオブジェクトをかえす
# user_loaderは、ユーザーオブジェクトを特定するためのコールバック関数を登録するために使用されるインスタンス内の機能
#基本的にデコレータの処理は先にデコレータの前にdefの関数を処理して、それを引数としてわたしてデコレータが処理する形
#この場合、load_user関数user_idを引数としてquery.get処理して、それをデコレータに渡して処理してねって感じ。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#userテーブルの定義
class User(UserMixin, db.Model):
    #テーブル名
    __tablename__ = 'users'
#Column定義
    id = db.Column(db.Integer, primary_key=True)
    #uniquiは一意のemailしか許さんぞ！ってこと
    #index=trueは、目次を作ってくれるってことかと検索が早くなります。
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    password = db.Column(db.String(128))
    #created_atの引数にある`server_default=func.now()`はユーザー作成時のサーバーの時刻を取得する設定です。
    #`nullable=False`は、Null値を許容しない設定になります。
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

#taskに紐づける
#usersテーブルのカラムをTaskで外部キーとして使用できるように設定
    tasks = db.relationship("Task", backref="users")

#カラムを外から使用できる設定
#Userクラスをインスタンス化したときに各カラムを引数として扱えるように設定
#各カラムをviews.pyで使えるようにしている
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        #パスワードをハッシュ化しています。
        self.password = generate_password_hash(password)

#こちらは、ハッシュ化したself.passwordとpasswordとして入力されたものをハッシュ化してチェック、返してくるようにしています。
    def validate_password(self,password):
        return check_password_hash(self.password, password)
#emailで検索した時に一番最初にあるemailを取得します
#select_by_emailでclsとemailを引数として処理し、classmethodデコレータで処理してくださいね。ということ
    @classmethod
    def select_by_email(cls, email):
        #clsをemailに引数のemailをいれてクエリフィルター処理をして、一番最初にあったやつを返してね
        return cls.query.filter_by(email=email).first()

#Taskテーブルの定義
#SQLAlchemyのModelを継承してテーブルを定義
class Task(db.Model):
    #テーブル名
    __tabelename__ = 'tasks'

#カラム定義：idは自動で増加主キー
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), index=True, nullable=False)
    detail = db.Column(db.String(128), index=True)
#タスクの期限（終了日時）
    end_time = db.Column(db.DateTime, nullable=False)
#タスクの作成日時
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
#タスクの更新日時
    update_at = db.Column(db.DateTime, onupdate=func.utc_timestamp(), nullable=True)
#usersテーブルのidを外部キーとして設定
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
