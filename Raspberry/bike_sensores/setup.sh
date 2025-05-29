#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "El entorno virtual no existe. Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    echo "Entorno virtual creado en .venv"
fi

source $VENV_DIR/bin/activate

echo "Actualizando pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo "Instalando dependencias..."
"$VENV_DIR/bin/pip" install -r "$DIR/requirements.txt"

echo "Ejecutando el script de envío de datos..."
"$VENV_DIR/bin/python" "$DIR/envioDatos.py"

