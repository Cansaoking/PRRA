# PRRA - Peer Review Automated Application

Sistema automatizado de revisión por pares para manuscritos científicos utilizando IA local y búsqueda en PubMed.

## Características

- 📄 **Múltiples formatos de entrada**: PDF, DOCX, DOC, RTF, TXT
- 🤖 **Análisis con IA local**: Utiliza modelos de HuggingFace (Qwen, DeepSeek, Phi-3, Llama)
- 🔬 **Búsqueda en PubMed**: Búsqueda automática de artículos de referencia
- 📥 **Importar artículos**: Carga artículos pre-seleccionados desde archivo de texto
- 🔑 **Extracción inteligente de keywords**: Usa keywords del autor + IA con enfoque médico/científico
- 📊 **Evaluación completa**: Calidad del inglés, estructura, metodología, actualización de contenidos
- 📝 **Doble informe**: Informe para el autor y informe detallado para auditoría
- ✏️ **Edición de informes**: Revisión y edición manual opcional antes de generar archivos finales
- 📁 **Directorio de salida personalizable**: Elige dónde guardar los informes generados
- 🗑️ **Limpieza automática de cache**: Elimina modelos y archivos temporales al cerrar
- 💬 **Prompts personalizables**: Sistema de prompts editables y guardables en JSON
- 🎨 **Interfaz profesional**: PyQt5 con diseño modular y progreso en tiempo real
- 🚀 **Soporte GPU**: Detección automática de CUDA para aceleración
- ⚡ **Inicio instantáneo**: Lazy imports para carga rápida de la aplicación

## Arquitectura Modular

El proyecto está organizado en módulos especializados:

```
PRRA/
├── main.py                      # Punto de entrada
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuración y constantes
│   ├── document_processor.py    # Extracción de texto y keywords
│   ├── ai_analyzer.py           # Análisis con IA
│   ├── pubmed_searcher.py       # Búsqueda en PubMed
│   ├── report_generator.py      # Generación de informes
│   ├── report_editor_dialog.py  # Editor de informes
│   ├── worker.py                # Thread de procesamiento
│   └── ui_main.py               # Interfaz de usuario
└── requirements.txt             # Dependencias
```

## Instalación

### Requisitos

- Python 3.8 o superior
- GPU con CUDA (opcional, pero recomendado)
- 20 GB de espacio libre (para modelos de IA)

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

**Nota**: La primera ejecución descargará el modelo de IA seleccionado (~4-14 GB según el modelo), lo cual puede tardar varios minutos.

### Instalación rápida (para pruebas)

Si solo quieres probar los módulos core sin la interfaz gráfica:

```bash
pip install python-docx PyPDF2 striprtf reportlab biopython
python test_modules.py
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
   - Artículos a buscar en PubMed (5-50) O importar artículos pre-seleccionados
   - Modelo de IA a utilizar
   - Formato de salida (PDF o DOCX)
   - Directorio de salida personalizado (opcional)
   - Edición manual de informes (opcional)
3. **Personalizar prompts** (opcional): Editar plantillas de prompts en la pestaña "Prompts"
4. **Iniciar revisión**: El proceso detecta automáticamente keywords del autor y las complementa con IA
5. **Revisar y editar** (si está habilitado): Editar contenido de informes antes de guardar
6. **Revisar resultados**: Se generan dos informes:
   - `*_Author_Report.pdf/docx`: Para el autor del manuscrito
   - `*_Auditor_Report.pdf/docx`: Para auditoría interna

### Importar artículos pre-seleccionados

Si ya tienes artículos relevantes de PubMed u otras fuentes, puedes importarlos directamente:

1. **Preparar archivo**: Crea un archivo de texto con tus artículos en el siguiente formato:
   ```
   Autor, X. et al. (Año). "Título del artículo." Revista Volumen(Número).
       Abstract del artículo...
   
   Autor2, Y. et al. (Año). "Otro título." Otra Revista Vol(Num).
       Otro abstract...
   ```

2. **Importar en la aplicación**:
   - En la pestaña "Configuration", marca "Import pre-selected articles (skip PubMed search)"
   - Click en "Load Articles File..." y selecciona tu archivo
   - La aplicación parseará y usará estos artículos para el análisis

3. **Ventajas**:
   - Salta la búsqueda en PubMed si ya tienes los artículos
   - Usa exactamente los artículos que consideras relevantes
   - Más rápido cuando ya has hecho la investigación

Ver `example_articles.txt` para un ejemplo completo del formato.

### Mejoras en extracción de keywords

La aplicación ahora utiliza un enfoque híbrido inteligente:

1. **Extracción de keywords del autor**: Busca y extrae las keywords que los autores incluyen en el manuscrito
   - Soporta múltiples formatos: "Keywords:", "Key words:", "Index terms:", "Palabras clave:"
   - Reconoce diferentes separadores: comas, punto y coma, bullets
2. **Complemento con IA**: Si faltan keywords o no se encuentran, la IA extrae frases clave adicionales
3. **Enfoque médico/científico mejorado**: El prompt de IA está optimizado para identificar conceptos médicos/científicos específicos
   - Se enfoca en temas principales, enfermedades, procesos biológicos, receptores, proteínas
   - Evita términos metodológicos generales que pueden causar búsquedas irrelevantes

Esto soluciona el problema reportado donde el tema era "receptores CGRP" pero se encontraban artículos de diabetes.

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

## Gestión de Cache

La aplicación descarga modelos de IA que pueden ocupar varios GB de espacio. Para gestionar este cache:

### Limpieza Automática al Cerrar
1. En la pestaña "Configuration", marca "Clean cache on exit"
2. Al cerrar la aplicación, se te preguntará si deseas limpiar el cache
3. Se eliminarán:
   - Modelos de IA descargados (HuggingFace, Torch)
   - Archivos temporales de Python (`__pycache__`)
   - Otros archivos de cache

### Limpieza Manual
Puedes limpiar el cache en cualquier momento sin cerrar la aplicación:

1. En la pestaña "Configuration", click en "🗑️ Clean Cache Now..."
2. Revisa el tamaño actual del cache
3. Confirma la limpieza
4. Los modelos se re-descargarán cuando se necesiten

### Ver Información del Cache
- Botón "📊 View Cache Info" muestra:
  - Tamaño total del cache
  - Cache de modelos de IA (HuggingFace, Torch)
  - Archivos temporales de Python (__pycache__)

**Importante**: Limpiar el cache eliminará los modelos descargados. La próxima vez que uses un modelo, se descargará nuevamente.

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
