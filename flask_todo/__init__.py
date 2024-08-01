
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#loginマネージャーをインスタンス化
login_manager = LoginManager()
#login_viewメソッドにtodo_app.loginを定義.
#この記述の意味は、未ログインのユーザーがログイン成功時しか見れないページを表示しようとしたときに、ログインを促すようにtodo_app.login( /login )へ遷移させます。
login_manager.login_view = 'todo_app.login'
#login_viewメソッドが実行されたときに表示されるメッセージをlogin_messageメソッドに定義します。
login_manager.login_message = 'ログイン未完了です'

#dbとしてSQLAlchemy（ORM）をインスタンス化。
#これで、データベースの記述指向との差分を考えずに記述させてくれる（クエリを作成してくれる）翻訳家が誕生
db = SQLAlchemy()
#migrateとして,マイグレート関数でインスタンス化
#migrateとは、python内のORMで操作する際のスキーマの変更を行ってくれるやつでクエリは作れない。
migrate = Migrate()

#ここでflaskクラスをインスタンス化する関数を定義
def create_app():
    app = Flask(__name__)

#Secret_keyはセッションの管理に必要な暗号化を管理する大事なキーです。
#そのキーを設定している項目です。
    app.config['SECRET_KEY'] = 'mysite'
#データベースとの接続の設定を定義しています。
#接続方法は使用するドライバなどによって若干違いますが、今回は**mysqlclient**を使用しますので、このようなコードになります。
    app.config['SQLALCHEMY_DATABASE_URI'] = \
            'mysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
                'user':"todo_user",
                'password':"MySQL_DB_Pass",
                'host':"localhost",
                'db_name':"ToDo_DB"
                })
#これは、もとのデータベースの変更を追跡して、仮想データベースを更新するかというもの。Falseは、更新しない。
    app.config['SQLALCHEMY_TRACE_MODIFICATIONS'] = False

#flask_todoの中のviews.pyファイルからblue printをインポート
#後述するviews.pyに記述するBlueprintという機能を使用できるように設定しています。
    from flask_todo.views import bp

#blue printをFlaskアプリで使用できるように設定しています。
    app.register_blueprint(bp)
#dbをFlaskアプリで使用できるように設定しています。
    db.init_app(app)
#migrateはMigrateのインスタンスflaskとSQLAlchemyを引数にしているので
#Flaskアプリで使用できるようになったMySQLのテーブルの作成や更新ができるように設定しています。
    migrate.init_app(app,db)
#login_managerはlogin_managerのインスタンスでflaskでlogin_managerを使えるようにしている。
    login_manager.init_app(app)
    return app

