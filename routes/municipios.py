import requests
from flask import Blueprint, jsonify, request
from shapely.geometry import shape
from sqlalchemy import func
from geoalchemy2 import Geography
from model import db
from model.municipio import Municipio

municipios_bp = Blueprint('municipios', __name__)

def get_uf_code(sigla_uf):
    estados = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados").json()
    for estado in estados:
        if estado['sigla'].upper() == sigla_uf.upper():
            return estado['id']
    return None

@municipios_bp.route('/municipios', methods=['GET'])
def listar_municipios():
    uf = request.args.get('uf')
    query = Municipio.query
    if uf:
        query = query.filter(Municipio.uf.ilike(uf))
    municipios = query.all()
    return jsonify([
        {"id": m.id, "nome": m.nome, "codigo_ibge": m.codigo_ibge, "uf": m.uf}
        for m in municipios
    ])

@municipios_bp.route('/municipios/<int:id>', methods=['GET'])
def lista_municipio(id):
    municipio = Municipio.query.get(id)
    if not municipio:
        return jsonify({"erro": "Municipio não encontrado"}), 404
    return jsonify({"id": municipio.id, "nome": municipio.nome})

@municipios_bp.route('/municipios', methods=['POST'])
def sincronizar_municipios():
    data = request.get_json()    
    uf = data.get('uf', 'PR').upper() if data else 'PR'    
    uf_code = get_uf_code(uf)
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_code}/municipios"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"erro": "Não foi possível acessar os dados do IBGE"}), 500

    municipios = response.json()
    lista_municipios = [
        {"codigo_ibge": m["id"], "nome": m["nome"]}
        for m in municipios
    ]

    for cidade in lista_municipios:
        codigo_ibge = cidade["codigo_ibge"]
        nome = cidade["nome"]

        url = f"https://servicodados.ibge.gov.br/api/v2/malhas/{codigo_ibge}?formato=application/vnd.geo+json"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        
        geojson = response.json()
        geometry = shape(geojson["features"][0]["geometry"]).wkt
        geometria = f"SRID=4326;{geometry}"

        existente = Municipio.query.filter_by(codigo_ibge=codigo_ibge).first()
        if existente:
            existente.nome = nome
            existente.uf = uf
            existente.geometria = geometria
        else:
            novo = Municipio(nome=nome, codigo_ibge=codigo_ibge, uf=uf, geometria=geometria)
            db.session.add(novo)
        db.session.commit()

    return jsonify({"mensagem": "Dados sincronizados com sucesso!"})

@municipios_bp.route("/municipios/proximos", methods=["GET"])
def municipios_proximos():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        raio_km = float(request.args.get("raio_km"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Parâmetros lat, lon e raio_km são obrigatórios e devem ser numéricos."}), 400

    raio_m = raio_km * 1000

    municipios = (
        db.session.query(Municipio)
        .filter(
            func.ST_DWithin(
                Municipio.geometria.cast(Geography),
                func.ST_SetSRID(func.ST_Point(lon, lat), 4326).cast(Geography),
                raio_m
            )
        )
        .all()
    )

    resultado = []
    for m in municipios:
        resultado.append({
            "id": m.id,
            "nome": m.nome,
            "uf": m.uf,
            "geometria": db.session.scalar(func.ST_AsGeoJSON(m.geometria))
        })

    return jsonify({"municipios": resultado})