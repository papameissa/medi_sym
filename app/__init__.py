from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import Config

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Connectez-vous pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    import json as _json

    @app.template_filter('from_json')
    def from_json_filter(s):
        try:
            return _json.loads(s)
        except Exception:
            return []

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app

def _seed_admin():
    from app.models import User
    if not User.query.filter_by(email='admin@medisym.com').first():
        admin = User(
            username='admin',
            email='admin@medisym.com',
            is_admin=True,
            plan='premium'
        )
        admin.set_password('Admin@1234')
        db.session.add(admin)
        db.session.commit()
        print("OK - Admin cree : admin@medisym.com / Admin@1234")
