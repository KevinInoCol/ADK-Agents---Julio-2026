# ============= Instalación en MAC ==============
## Instalamos la CLI de Google:
brew install --cask google-cloud-sdk
# Buscamos actualizaciones si las hay:
brew upgrade --cask google-cloud-sdk


# =========== Instalación en Windows =============
## Descargar e instalar el ejecutable oficial:
- https://cloud.google.com/sdk/docs/install → botón "Google Cloud CLI installer" (GoogleCloudSDKInstaller.exe)


# ============= Empezamos a trabajar ============
# Primer paso: Para el SDK de Google
- gcloud init

# Segundo paso: Permisos para utilizar los diferentes servicios de Google.
- gcloud auth login

# Tercer paso: Obtengo una clave JSON de una cuenta de servicio temporal con el Google Auth Library
- gcloud auth application-default login


# ================ Lanza tu Entorno Virtual ==================
Ejemplo: conda activate ADK-Agents

# ================= Instalamos Google ADK ====================
pip install google-adk

# ========= Laboratorio de ADK ========
adk web




"google-adk==2.4.0"
# =========== Despliegue sobre GCR ========
adk deploy cloud_run \
--project=datapath-kevin-inofuentecolque \
--region=us-central1 \
--service_name=project-conexion-big-query-adk-service \
--app_name=project_conexion_big_query_adk_app \
--with_ui \
project_conexion_big_query_adk






# Tercer paso
- Verificamos si tenemos activa la API de Vertex AI
- Verificamos si tenemos activa la API de Gemini

# Cuarto paso: Especificamente para este proyecto
- Verificamos si tenemos activa la API de BigQuery

# Quinto paso: Instalamos las librerias o dependencias para este proyecto
- pip install -r requirements.txt

# Sexto paso: Modificamos lo necesario en el módulo "run_sql_query"
- La línea 10 tiene el ID del proyecto de Google.

# Septimo paso: Modificamos el .env
- Cambiar el ID del proyecto de Google.

# Octavo paso: Ejecutamos adk web
- Lanzamos en la terminal: "adk web --host 0.0.0.0"





# Comandos opcionales.
## Si no te activa la API de VertexAI
- gcloud services enable aiplatform.googleapis.com --project=project-mlops-10-streamlit

## Cuando quiero hacer la parte de Frontend o Desplegar (Deployar) la aplicación
adk api_server --host 0.0.0.0 --port 8000



Dev Container: Reopen in Container





## Hacer Deploy con Google Cloud Run






adk deploy agent_engine \
--project=datapath-kevin-inofuente \
--region=us-central1 \
--service_name=project-conexion-big-query-adk-service \
--app_name=project-conexion-big-query-adk-app \
--with_ui \
project_conexion_big_query_adk