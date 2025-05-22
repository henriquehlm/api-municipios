from geoalchemy2 import Geometry
from model import db

class Municipio(db.Model):
    __tablename__ = 'municipios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    uf = db.Column(db.String(2), nullable=True)
    codigo_ibge = db.Column(db.Integer, nullable=True)    
    geometria = db.Column(Geometry("MULTIPOLYGON", srid=4326))