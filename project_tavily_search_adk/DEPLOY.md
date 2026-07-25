# Despliegue en Cloud Run con Secret Manager

Proyecto: `datapath-kevin-inofuentecolque` · Región: `us-central1`
Servicio: `project-tavily-search-adk-service`

Las API keys (`GOOGLE_API_KEY`, `TAVILY_API_KEY`) **nunca** viajan dentro de la imagen:
el `.gcloudignore` excluye el `.env` y Cloud Run las inyecta desde Secret Manager.

---

## 1. Habilitar las APIs necesarias

```bash
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project=datapath-kevin-inofuentecolque
```

## 2. Los secretos

Ya están creados en Secret Manager con estos IDs, que son los que referencia el
`manifest.yml`:

| Secreto | Variable de entorno en el contenedor |
|---|---|
| `GOOGLE_API_KEY` | `GOOGLE_API_KEY` |
| `TAVILY_API_KEY` | `TAVILY_API_KEY` |

Comprobar que existen y que tienen al menos una versión activa:

```bash
gcloud secrets list --project=datapath-kevin-inofuentecolque
gcloud secrets versions list TAVILY_API_KEY --project=datapath-kevin-inofuentecolque
```

Si hiciera falta crear uno desde cero, se lee del `.env` local para que la clave no
quede en el historial del shell:

```bash
cd project_tavily_search_adk
grep '^TAVILY_API_KEY=' .env | cut -d= -f2- | tr -d '\n' | \
  gcloud secrets create TAVILY_API_KEY --data-file=- \
    --replication-policy=automatic --project=datapath-kevin-inofuentecolque
```

**Rotar una clave** más adelante (el manifest apunta a `latest`, así que basta con
añadir una versión nueva y redesplegar la revisión):

```bash
printf '%s' 'NUEVA_CLAVE' | \
  gcloud secrets versions add TAVILY_API_KEY --data-file=- \
    --project=datapath-kevin-inofuentecolque
```

## 3. Dar permiso de lectura a la service account de Cloud Run

```bash
PROJECT_ID=datapath-kevin-inofuentecolque
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
RUNNER="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

for SECRET in GOOGLE_API_KEY TAVILY_API_KEY; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$RUNNER" \
    --role=roles/secretmanager.secretAccessor \
    --project=$PROJECT_ID
done
```

> Sin este paso el contenedor arranca y muere con `PERMISSION_DENIED` al leer el secreto.

## 4. Primer despliegue (construye la imagen)

Desde la raíz `Proyectos-ADK/`:

```bash
adk deploy cloud_run \
  --project=datapath-kevin-inofuentecolque \
  --region=us-central1 \
  --service_name=project-tavily-search-adk-service \
  --app_name=project_tavily_search_adk_app \
  --with_ui \
  project_tavily_search_adk
```

Esto deja la imagen en
`us-central1-docker.pkg.dev/datapath-kevin-inofuentecolque/cloud-run-source-deploy/project-tavily-search-adk-service:latest`,
que es justo la que referencia el `manifest.yml`.

> Requiere `google-adk==2.4.0`. La 2.5.0 pasa un flag `--sandbox-launcher` a gcloud
> que todavía no existe en la CLI y el deploy falla.

## 5. Aplicar el manifest (inyecta los secretos)

```bash
gcloud run services replace project_tavily_search_adk/manifest.yml \
  --region=us-central1 \
  --project=datapath-kevin-inofuentecolque
```

## 6. Abrir el acceso

`services replace` no gestiona IAM, así que el acceso público se da aparte:

```bash
gcloud run services add-iam-policy-binding project-tavily-search-adk-service \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=datapath-kevin-inofuentecolque
```

---

## Redespliegues posteriores

Repite el paso 4 y luego el 5. El paso 4 sube código nuevo pero **borra la
configuración de secretos** (reconstruye el servicio desde cero), por eso el
`replace` va siempre después.

## Alternativa en un solo comando (sin manifest)

Si no necesitas la configuración declarativa, `adk deploy` acepta argumentos
que se pasan tal cual a gcloud después de `--`:

```bash
adk deploy cloud_run \
  --project=datapath-kevin-inofuentecolque \
  --region=us-central1 \
  --service_name=project-tavily-search-adk-service \
  --app_name=project_tavily_search_adk_app \
  --with_ui \
  project_tavily_search_adk \
  -- \
  --set-secrets=GOOGLE_API_KEY=GOOGLE_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest \
  --set-env-vars=GOOGLE_GENAI_USE_ENTERPRISE=FALSE,GOOGLE_GENAI_USE_VERTEXAI=FALSE \
  --allow-unauthenticated
```

Ventaja: un solo paso, sin desincronización entre deploy y manifest.
Desventaja: la configuración vive en el comando y no en el repo.

## Verificar

```bash
# Variables y secretos efectivos del servicio
gcloud run services describe project-tavily-search-adk-service \
  --region=us-central1 --project=datapath-kevin-inofuentecolque \
  --format='yaml(spec.template.spec.containers[0].env)'

# Logs si algo falla al arrancar
gcloud run services logs read project-tavily-search-adk-service \
  --region=us-central1 --project=datapath-kevin-inofuentecolque --limit=50
```
