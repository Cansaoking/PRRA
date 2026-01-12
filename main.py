#!/usr/bin/env python3
"""
PRRA - Peer Review Automated Application
Punto de entrada principal de la aplicación
"""
import sys
import os

# Añadir directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui_main import main

if __name__ == "__main__":
    main()
