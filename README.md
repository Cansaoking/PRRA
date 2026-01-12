# PRRA - Peer Review Automated Application

Sistema automatizado de revisión por pares para manuscritos científicos utilizando IA local y búsqueda en PubMed.

## Características

- 📄 **Múltiples formatos de entrada**: PDF, DOCX, DOC, RTF, TXT
- 🤖 **Análisis con IA local**: Utiliza modelos de HuggingFace (Qwen, DeepSeek, Phi-3, Llama)
- 🔬 **Búsqueda en PubMed**: Búsqueda automática de artículos de referencia
- 📊 **Evaluación completa**: Calidad del inglés, estructura, metodología, actualización de contenidos
- 📝 **Doble informe**: Informe para el autor y informe detallado para auditoría
- 💬 **Prompts personalizables**: Sistema de prompts editables y guardables en JSON
- 🎨 **Interfaz profesional**: PyQt5 con diseño modular y progreso en tiempo real
- 🚀 **Soporte GPU**: Detección automática de CUDA para aceleración

## Arquitectura Modular

El proyecto está organizado en módulos especializados:

```
PRRA/
├── main.py                      # Punto de entrada
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuración y constantes
│   ├── document_processor.py    # Extracción de texto
│   ├── ai_analyzer.py           # Análisis con IA
│   ├── pubmed_searcher.py       # Búsqueda en PubMed
│   ├── report_generator.py      # Generación de informes
│   ├── worker.py                # Thread de procesamiento
│   └── ui_main.py               # Interfaz de usuario
└── requirements.txt             # Dependencias
```

## Instalación

### Requisitos

- Python 3.8 o superior
- GPU con CUDA (opcional, pero recomendado)

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/Cansaoking/PRRA.git
cd PRRA
```

2. Crear entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Inicio rápido

```bash
python main.py
```

### Flujo de trabajo

1. **Cargar manuscrito**: Abrir archivo PDF, DOCX, DOC, RTF o TXT
2. **Configurar parámetros**:
   - Número de frases clave (3-10)
   - Artículos a buscar en PubMed (5-50)
   - Modelo de IA a utilizar
   - Formato de salida (PDF o DOCX)
3. **Personalizar prompts** (opcional): Editar plantillas de prompts en la pestaña "Prompts"
4. **Iniciar revisión**: El proceso es automático
5. **Revisar resultados**: Se generan dos informes:
   - `*_Author_Report.pdf/docx`: Para el autor del manuscrito
   - `*_Auditor_Report.pdf/docx`: Para auditoría interna

### Modo manual

Activar la opción "Manual mode" para revisar y confirmar pasos intermedios.

### Prompts personalizados

Los prompts se pueden editar, guardar y cargar en formato JSON. Plantillas incluyen:

- `keyphrases`: Extracción de frases clave
- `analysis`: Análisis y evaluación del manuscrito

## Evaluación

La aplicación evalúa los siguientes aspectos:

1. **Calidad del inglés**: Gramática, claridad, estilo académico
2. **Estructura**: Organización lógica, flujo narrativo
3. **Actualización**: Métodos y referencias actuales
4. **Metodología**: Adecuación y descripción clara
5. **Originalidad**: Contribución y novedad
6. **Presentación**: Visualización y interpretación de datos
7. **Conclusiones**: Fundamentación en resultados

### Estructura de evaluación

- **Major Points**: Problemas críticos que deben abordarse
- **Minor Points**: Problemas menores a mejorar
- **Other Points**: Observaciones opcionales
- **Suggestions**: Sugerencias específicas de mejora

## Búsqueda en PubMed

La aplicación implementa búsqueda progresiva:

1. Búsqueda individual por frase clave
2. Si hay demasiados resultados: combina términos con AND
3. Si hay pocos resultados: amplía rango de fechas
4. Prioriza artículos recientes (últimos 5 años)

## Modelos de IA soportados

- Qwen/Qwen2.5-7B-Instruct
- deepseek-ai/deepseek-coder-7b-instruct-v1.5
- microsoft/Phi-3-mini-4k-instruct
- meta-llama/Llama-2-7b-chat-hf

**Nota**: La primera vez que se usa un modelo, se descarga automáticamente (puede tardar varios minutos).

## Configuración

Editar `src/config.py` para personalizar:

- Email de Entrez para PubMed
- Modelos disponibles
- Parámetros por defecto
- Prompts predeterminados
- Umbrales de búsqueda

## Requisitos de sistema

### Mínimos
- CPU: 4 núcleos
- RAM: 8 GB
- Disco: 20 GB libres

### Recomendados
- CPU: 8+ núcleos
- RAM: 16+ GB
- GPU: NVIDIA con 8+ GB VRAM (CUDA compatible)
- Disco: 50 GB libres

## Solución de problemas

### Error de memoria

Si el modelo es demasiado grande para tu GPU/RAM:
- Usar modelos más pequeños (Phi-3 mini)
- Ejecutar en modo CPU
- Cerrar otras aplicaciones

### Error de PubMed

- Verificar conexión a internet
- Cambiar email en `src/config.py`
- Reducir número de artículos a buscar

### Error de formato de archivo

- Verificar que el archivo no esté corrupto
- Probar con otro formato (convertir PDF a DOCX)
- Verificar que el archivo tenga texto extraíble

## Privacidad y seguridad

- **Procesamiento 100% local**: Los manuscritos NUNCA se envían a servidores externos
- **Sin API keys**: No requiere claves de API de servicios externos
- **Modelos locales**: Todos los modelos de IA se ejecutan localmente
- **Búsqueda pública**: Solo se consulta PubMed (base de datos pública)

## Licencia

[Especificar licencia]

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Contacto

[Información de contacto]

## Agradecimientos

- HuggingFace por los modelos de IA
- NCBI por PubMed/Entrez
- Comunidad open source

## Roadmap

- [ ] Soporte para más idiomas de interfaz
- [ ] Integración con gestores de referencias (Zotero, Mendeley)
- [ ] Exportación a más formatos (LaTeX, Markdown)
- [ ] Sistema de plugins para evaluaciones personalizadas
- [ ] Comparación entre múltiples modelos de IA
- [ ] Base de datos local de evaluaciones anteriores
- [ ] API REST para integración con otros sistemas
