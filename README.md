
# API de Municípios - Documentação

Esta API oferece funcionalidades para listar, sincronizar e consultar municípios brasileiros com dados geoespaciais, utilizando Flask, SQLAlchemy e PostGIS.

# Guia para Construção e Execução da API com Docker

## Pré-requisitos

- Docker instalado ([link para instalação](https://docs.docker.com/get-docker/))
- Docker Compose instalado ([link para instalação](https://docs.docker.com/compose/install/))

## Clone o repositorio 
```bash
git clone https://github.com/henriquehlm/api-municipios.git
cd api-municipios
```

## Passo 1: Construir a imagem Docker da aplicação

No diretório raiz do projeto (onde está o `Dockerfile`), execute o comando:

```bash
docker build -t api-municipios .
```

## Passo 2: Efetuar o build
```bash
docker-compose up --build
```
## Passo 3: Disponivel a API na url abaixo
```bash
[local](http://localhost:5000/)
```

---

## Endpoints

### 1. Listar municípios

- **URL:** `/municipios`
- **Método:** `GET`
- **Parâmetros Query:**
  - `uf` (opcional) — filtro por sigla da Unidade Federativa (ex: `SP`, `RJ`, `PR`)

- **Resposta:**
  - Status 200
  - JSON com lista de municípios

```json
[
  {
    "id": 1,
    "nome": "Curitiba",
    "codigo_ibge": 4106902,
    "uf": "PR"
  }
]
```

---

### 2. Buscar município por ID

- **URL:** `/municipios/<id>`
- **Método:** `GET`
- **Parâmetros:**
  - `id` — ID do município no banco de dados

- **Resposta:**
  - Status 200
  - JSON com dados do município

```json
{
  "id": 1,
  "nome": "Curitiba"
}
```

- **Erros:**
  - Status 404 se município não for encontrado

```json
{
  "erro": "Municipio não encontrado"
}
```

---

### 3. Sincronizar municípios por UF

- **URL:** `/municipios`
- **Método:** `POST`
- **Body (JSON):**
  - `uf` (opcional) — sigla da Unidade Federativa para sincronizar (ex: `"PR"`)
  - Se não informado, sincroniza por padrão a UF `PR`

- **Funcionamento:**
  - Busca municípios da UF no serviço do IBGE
  - Baixa geometria geojson de cada município
  - Atualiza os municípios existentes ou cria novos no banco

- **Resposta:**
  - Status 200
  - JSON com mensagem de sucesso

```json
{
  "mensagem": "Dados sincronizados com sucesso!"
}
```

---

### 4. Buscar municípios próximos a uma coordenada

- **URL:** `/municipios/proximos`
- **Método:** `GET`
- **Parâmetros Query:**
  - `lat` — latitude (obrigatório)
  - `lon` — longitude (obrigatório)
  - `raio_km` — raio de busca em quilômetros (obrigatório)

- **Resposta:**
  - Status 200
  - JSON com lista de municípios dentro do raio

```json
{
  "municipios": [
    {
      "id": 1,
      "nome": "Curitiba",
      "uf": "PR",
      "geometria": "{...GeoJSON string...}"
    }
  ]
}
```

- **Erros:**
  - Status 400 se parâmetros estiverem faltando ou inválidos

```json
{
  "erro": "Parâmetros lat, lon e raio_km são obrigatórios e devem ser numéricos."
}
```

---


