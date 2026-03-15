#!/bin/bash

# Inicia o servidor com Gunicorn se estivermos em produção e no Linux
# Caso contrário, usa o run.py padrão
if [ "$FLASK_ENV" = "production" ]; then
    echo "Iniciando MagaBip em modo Produção (Gunicorn)..."
    exec gunicorn --bind 0.0.0.0:80 "app:create_app()"
else
    echo "Iniciando MagaBip em modo Desenvolvimento..."
    exec python run.py
fi
