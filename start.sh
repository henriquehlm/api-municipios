#!/usr/bin/env bash
#   wait-for-it.sh
#   Use este script para esperar um serviço TCP ficar disponível antes de iniciar outro

echo "Esperando 10 segundos antes de iniciar..."
sleep 10

echo "Iniciando aplicação..."
python app.py