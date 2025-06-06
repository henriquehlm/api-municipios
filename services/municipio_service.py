import requests
from shapely.geometry import shape
from sqlalchemy import func
from geoalchemy2 import Geography
from model import db
from model.municipio import Municipio


def get_uf_code(sigla_uf):
    estados = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados").json()
    for estado in estados:
        if estado['sigla'].upper() == sigla_uf.upper():
            return estado['id']
    return None


def listar_municipios(uf=None):
    query = Municipio.query
    if uf:
        query = query.filter(Municipio.uf.ilike(uf))
    return query.all()


def listar_municipio_por_id(id):
    return Municipio.query.get(id)


def sincronizar_municipios(uf='PR'):
    uf = uf.upper()
    uf_code = get_uf_code(uf)
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_code}/municipios"
    response = requests.get(url)

    if response.status_code != 200:
        return False, "Não foi possível acessar os dados do IBGE"

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

    return True, "Dados sincronizados com sucesso!"


def buscar_municipios_proximos(lat, lon, raio_km):
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

    return resultado