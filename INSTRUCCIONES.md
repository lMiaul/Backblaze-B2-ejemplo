# Instrucciones de Configuración de Entorno

Para que la aplicación funcione, es necesario conectar los tres servicios en la nube. Siga estos pasos para obtener las credenciales y configurar su entorno.

1. **Copiar la plantilla de entorno**:
   Copie el archivo `.env.example` y renómbrelo a `.env`.

---

## 1. Supabase (Datos Estructurados)

1. Vaya a [Supabase](https://supabase.com/) y cree un nuevo proyecto.
2. Una vez creado el proyecto, vaya a **Project Settings** (el ícono de la rueda dentada) > **API**.
3. Copie la URL del proyecto y péguela en `.env` como `SUPABASE_URL`.
4. Copie la clave `anon` `public` y péguela en `.env` como `SUPABASE_KEY`.
5. En Supabase, vaya al **SQL Editor** y ejecute el siguiente comando para crear la tabla de usuarios:
   ```sql
   CREATE TABLE usuarios (
     id SERIAL PRIMARY KEY,
     nombre VARCHAR(255) NOT NULL,
     email VARCHAR(255) UNIQUE NOT NULL,
     fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```

---

## 2. MongoDB Atlas (Datos Semiestructurados)

1. Vaya a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) y cree un clúster gratuito.
2. En la sección **Database Access**, cree un usuario para la base de datos con contraseña.
3. En **Network Access**, asegúrese de permitir el acceso desde cualquier lugar (`0.0.0.0/0`) para que Codespaces pueda conectarse.
4. Vaya a **Database** y haga clic en **Connect** > **Drivers** (Python).
5. Copie la cadena de conexión (`mongodb+srv://...`) y reemplace `<password>` por la contraseña de su usuario. Péguelo en `.env` como `MONGODB_URI`.

---

## 3. Backblaze B2 (Almacenamiento No Estructurado)

1. Vaya a [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) y cree una cuenta.
2. Vaya a **Buckets** y haga clic en **Create a Bucket**. Dele un nombre único y asegúrese de que la privacidad sea **Private**. Note que se usa un bucket privado por seguridad.
3. Coloque el nombre de este bucket en `.env` como `B2_BUCKET_NAME`.
4. En el bucket, tome nota del **Endpoint** S3 (por ejemplo, `s3.us-east-005.backblazeb2.com`).
5. Agregue el protocolo `https://` al inicio del endpoint y péguelo en `.env` como `B2_ENDPOINT_URL` (ejemplo: `https://s3.us-east-005.backblazeb2.com`).
6. Vaya a **Application Keys** y haga clic en **Add a New Application Key**. Dele acceso al bucket que acaba de crear o a todos.
7. Copie el `keyID` y péguelo como `B2_KEY_ID`.
8. Copie el `applicationKey` (solo se muestra una vez) y péguelo como `B2_APPLICATION_KEY`.

---

Una vez tenga el archivo `.env` configurado con todas estas claves, la aplicación Streamlit estará lista para funcionar.
