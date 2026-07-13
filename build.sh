#!/bin/bash
# Script de build para o Render

echo "🚀 Iniciando build do AssistIA..."

echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🔄 Executando migrações..."
python manage.py migrate --noinput

echo "✅ Build concluído com sucesso!"
