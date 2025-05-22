from flask import Blueprint, jsonify, request
from services import municipio_service

municipios_bp = Blueprint('municipios', __name__)


@municipios_bp.route('/municipios', methods=['GET'])
def listar_municipios():
    uf = request.args.get('uf')
    municipios = municipio_service.listar_municipios(uf)
    return jsonify([
        {"id": m.id, "nome": m.nome, "codigo_ibge": m.codigo_ibge, "uf": m.uf}
        for m in municipios
    ])


@municipios_bp.route('/municipios/<int:id>', methods=['GET'])
def lista_municipio(id):
    municipio = municipio_service.listar_municipio_por_id(id)
    if not municipio:
        return jsonify({"erro": "Município não encontrado"}), 404
    return jsonify({"id": municipio.id, "nome": municipio.nome})


@municipios_bp.route('/municipios', methods=['POST'])
def sincronizar_municipios():
    data = request.get_json()
    uf = data.get('uf', 'PR').upper() if data else 'PR'
    sucesso, mensagem = municipio_service.sincronizar_municipios(uf)
    if not sucesso:
        return jsonify({"erro": mensagem}), 500
    return jsonify({"mensagem": mensagem})


@municipios_bp.route("/municipios/proximos", methods=["GET"])
def municipios_proximos():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        raio_km = float(request.args.get("raio_km"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Parâmetros lat, lon e raio_km são obrigatórios e devem ser numéricos."}), 400

    resultado = municipio_service.buscar_municipios_proximos(lat, lon, raio_km)
    return jsonify({"municipios": resultado})