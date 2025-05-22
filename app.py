from flask import Flask
from model import db
from routes.municipios import municipios_bp

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@db:5432/geodb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensão SQLAlchemy
    db.init_app(app)

    # Registrar blueprints (rotas)
    app.register_blueprint(municipios_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)