FROM apache/airflow:2.7.1-python3.9

# Copiar requirements.txt primero para aprovechar el cache de capas de Docker
COPY requirements.txt /opt/airflow/

USER root

# Instalar dependencias del sistema y crear directorios necesarios
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/airflow/logs/scheduler \
    && mkdir -p /opt/airflow/logs/dag_processor_manager \
    && mkdir -p /opt/airflow/logs/webserver \
    && mkdir -p /opt/airflow/config \
    && mkdir -p /opt/airflow/dags \
    && mkdir -p /opt/airflow/data \
    && mkdir -p /opt/airflow/etls \
    && mkdir -p /opt/airflow/pipelines \
    && mkdir -p /opt/airflow/utils \
    && chown -R airflow:root /opt/airflow \
    && chmod -R 777 /opt/airflow/logs

USER airflow

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Verificar que los directorios existen y tienen los permisos correctos
RUN ls -la /opt/airflow/logs
