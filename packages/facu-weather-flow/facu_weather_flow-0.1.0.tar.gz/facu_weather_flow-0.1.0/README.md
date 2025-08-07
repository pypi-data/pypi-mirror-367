# Track Flow

**Track Flow** es una librería de Python modular que implementa un pipeline ETL para procesar datos de charts de Spotify. Extrae información desde una API, la transforma en DTOs (Data Transfer Objects), la guarda en formato Parquet y la carga en un bucket de Amazon S3.

---

## 🚀 Características

- Extracción de datos desde una API externa (Spotify charts)
- Transformación a DTOs estructurados
- Almacenamiento como Parquet
- Carga directa en S3 (Amazon Web Services)
- Configuración flexible mediante variables de entorno
- Uso como librería o desde la línea de comandos (`trackflow`)

---

## 📦 Instalación

```bash
pip install track-flow
