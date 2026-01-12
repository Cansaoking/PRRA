#!/usr/bin/env python3
"""
PRRA - Peer Review Automated Application (Legacy entry point)

NOTA: Este archivo mantiene compatibilidad con versiones anteriores.
Para la nueva versión modular, usar: python main.py

La aplicación ha sido refactorizada con arquitectura modular.
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la nueva aplicación modular
from src.ui_main import main

if __name__ == "__main__":
    print("=" * 60)
    print("PRRA - Peer Review Automated Application")
    print("=" * 60)
    print("Starting modular version...")
    print("For new installations, use: python main.py")
    print("=" * 60)
    print()
    
    main()