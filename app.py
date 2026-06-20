import os
import streamlit as st
from supabase import create_client, Client
from pymongo import MongoClient
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# --- Configurations ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
MONGODB_URI = os.environ.get("MONGODB_URI", "")
B2_ENDPOINT_URL = os.environ.get("B2_ENDPOINT_URL", "")
B2_KEY_ID = os.environ.get("B2_KEY_ID", "")
B2_APPLICATION_KEY = os.environ.get("B2_APPLICATION_KEY", "")
B2_BUCKET_NAME = os.environ.get("B2_BUCKET_NAME", "")

# --- Initialize Clients ---
@st.cache_resource
def init_supabase() -> Client:
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error inicializando Supabase: {e}")
    return None

@st.cache_resource
def init_mongodb():
    try:
        if MONGODB_URI:
            client = MongoClient(MONGODB_URI)
            db = client.get_database("app_db") # Base de datos por defecto
            return db.perfiles_extra # Coleccion
    except Exception as e:
        st.error(f"Error inicializando MongoDB: {e}")
    return None

@st.cache_resource
def init_b2():
    try:
        if B2_ENDPOINT_URL and B2_KEY_ID and B2_APPLICATION_KEY:
            b2 = boto3.client(
                service_name='s3',
                endpoint_url=B2_ENDPOINT_URL,
                aws_access_key_id=B2_KEY_ID,
                aws_secret_access_key=B2_APPLICATION_KEY,
                config=Config(signature_version='s3v4')
            )
            return b2
    except Exception as e:
        st.error(f"Error inicializando B2: {e}")
    return None

supabase = init_supabase()
mongo_collection = init_mongodb()
b2_client = init_b2()


# --- UI: Setup ---
st.set_page_config(page_title="Registro Universal en la Nube", page_icon="☁️", layout="centered")

st.title("☁️ Registro Universal en la Nube")
st.markdown("""
Esta aplicación demuestra la integración de una arquitectura tripartita:
1. **Supabase (PostgreSQL)**: Para datos estructurados (perfil de usuario).
2. **MongoDB Atlas**: Para datos semiestructurados (configuración en JSON flexible).
3. **Backblaze B2**: Para almacenamiento de datos no estructurados (archivos adjuntos).
""")

st.divider()

if not supabase or not mongo_collection or not b2_client:
    st.warning("⚠️ Faltan configurar las variables de entorno. Por favor revise el archivo INSTRUCCIONES.md y .env")

# --- UI: Form ---
with st.form("registro_form"):
    st.subheader("1. Datos Personales (Datos Estructurados - Supabase)")
    nombre = st.text_input("Nombre completo")
    email = st.text_input("Correo electrónico")
    
    st.subheader("2. Preferencias (Datos Semiestructurados - MongoDB)")
    st.caption("Estos datos se guardarán como un documento JSON flexible.")
    tema = st.selectbox("Tema de la Interfaz", ["Claro", "Oscuro", "Sistema"])
    notificaciones = st.checkbox("Recibir notificaciones", value=True)
    biografia = st.text_area("Biografía corta (Opcional)")
    
    st.subheader("3. Archivo Adjunto (Datos No Estructurados - Backblaze B2)")
    st.caption("Suba un avatar o documento (se guardará en un bucket privado).")
    archivo_subido = st.file_uploader("Seleccione un archivo", type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])

    submit_button = st.form_submit_button("Registrar Usuario")

# --- Lógica de Procesamiento ---
if submit_button:
    if not nombre or not email:
        st.error("Por favor, complete el nombre y el correo electrónico.")
    elif not supabase or not mongo_collection or not b2_client:
        st.error("Los servicios de backend no están configurados correctamente.")
    else:
        with st.spinner("Procesando datos en la nube..."):
            try:
                # 1. Supabase (Insertar datos estructurados)
                user_data = {"nombre": nombre, "email": email}
                res_supabase = supabase.table("usuarios").insert(user_data).execute()
                
                # Asumimos que se creó bien y obtenemos el ID (si la tabla tiene serial)
                # Opcional: usar el correo como identificador si no retorna ID
                user_ref = res_supabase.data[0]['id'] if hasattr(res_supabase, 'data') and len(res_supabase.data)>0 and 'id' in res_supabase.data[0] else email
                
                st.success(f"✅ Datos en Supabase guardados con éxito para {email}.")

                # 2. MongoDB (Insertar datos semiestructurados vinculados al usuario)
                perfil_extendido = {
                    "usuario_ref": user_ref,
                    "email": email,
                    "preferencias": {
                        "tema": tema,
                        "notificaciones": notificaciones
                    },
                    "biografia": biografia
                }
                mongo_collection.insert_one(perfil_extendido)
                st.success("✅ Documento JSON guardado en MongoDB Atlas con éxito.")

                # 3. Backblaze B2 (Subir archivo si existe)
                if archivo_subido is not None:
                    # Generar un nombre único para el archivo
                    file_extension = archivo_subido.name.split('.')[-1]
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    
                    # Leer bytes
                    file_bytes = archivo_subido.getvalue()
                    
                    # Subir al bucket
                    b2_client.put_object(
                        Bucket=B2_BUCKET_NAME,
                        Key=unique_filename,
                        Body=file_bytes,
                        ContentType=archivo_subido.type
                    )
                    st.success(f"✅ Archivo guardado en Backblaze B2 como: `{unique_filename}`")
                
                st.balloons()
                st.info("El registro completo en la nube ha finalizado correctamente.")
                
            except Exception as e:
                st.error(f"Ocurrió un error durante el procesamiento: {e}")
