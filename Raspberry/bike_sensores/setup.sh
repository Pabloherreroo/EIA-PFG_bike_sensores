#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VENV_DIR="$DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "El entorno virtual no existe. Creando entorno virtual..."
    python3 -m venv $VENV_DIR
    echo "Entorno virtual creado en .venv"
else
    echo "El entorno virtual ya existe. Activando entorno virtual..."
fi

source $VENV_DIR/bin/activate

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Ejecutando el script de envío de datos..."
python envioDatos.py

