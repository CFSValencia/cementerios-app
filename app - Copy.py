import streamlit as st
from pathlib import Path
import pandas as pd
from supabase import create_client
import base64
from io import BytesIO

BASE_DIR = Path(__file__).parent
LOGO = BASE_DIR / "logo.png"
CSS_FILE = BASE_DIR / "style.css"

st.set_page_config(
    page_title="Registro de cementerios",
    page_icon="📘",
    layout="wide"
)

if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_data
def convertir_a_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cementerios")
    output.seek(0)
    return output.getvalue()

def es_url_valida(url):
    if not str(url).strip():
        return True
    url = str(url).strip().lower()
    return url.startswith("http://") or url.startswith("https://")

def es_coordenada_valida(texto):
    if not str(texto).strip():
        return True
    partes = str(texto).split(",")
    if len(partes) != 2:
        return False
    try:
        lat = float(partes[0].strip())
        lon = float(partes[1].strip())
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except ValueError:
        return False

def obtener_cementerios():
    respuesta = (
        supabase
        .table("cementerios")
        .select("""
            codigo_cementerio,
            nombre_oficial,
            pais,
            departamento,
            municipio,
            distrito,
            estado,
            coordenadas,
            google_maps_url,
            enlace_principal,
            enlace_2,
            enlace_3,
            foto_url,
            observaciones
        """)
        .order("codigo_cementerio", desc=False)
        .execute()
    )
    return respuesta.data if respuesta.data else []

def actualizar_cementerio(codigo_original, datos_actualizados):
    return (
        supabase
        .table("cementerios")
        .update(datos_actualizados)
        .eq("codigo_cementerio", codigo_original)
        .execute()
    )

def eliminar_cementerio(codigo):
    return (
        supabase
        .table("cementerios")
        .delete()
        .eq("codigo_cementerio", codigo)
        .execute()
    )

supabase = get_supabase()

if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = ""

PAYS = ["El Salvador"]

DEPARTAMENTOS = {
    "Ahuachapán": {
        "Ahuachapán Norte": ["Atiquizaya", "El Refugio", "San Lorenzo", "Turín"],
        "Ahuachapán Centro": ["Ahuachapán", "Apaneca", "Concepción de Ataco", "Tacuba"],
        "Ahuachapán Sur": ["Guaymango", "Jujutla", "San Francisco Menendez", "San Pedro Puxtla"],
    },
    "San Salvador": {
        "San Salvador Norte": ["Aguilares", "El Paisnal", "Guazapa"],
        "San Salvador Oeste": ["Apopa", "Nejapa"],
        "San Salvador Este": ["Ilopango", "San Martín", "Soyapango", "Tonacatepeque"],
        "San Salvador Centro": ["Ayutuxtepeque", "Mejicanos", "San Salvador", "Cuscatancingo", "Ciudad Delgado"],
        "San Salvador Sur": ["Panchimalco", "Rosario de Mora", "San Marcos", "Santo Tomás", "Santiago Texacuangos"],
    },
    "La Libertad": {
        "La Libertad Norte": ["Quezaltepeque", "San Matías", "San Pablo Tacachico"],
        "La Libertad Centro": ["San Juan Opico", "Ciudad Arce"],
        "La Libertad Oeste": ["Colón", "Jayaque", "Sacacoyo", "Tepecoyo", "Talnique"],
        "La Libertad Este": ["Antiguo Cuscatlán", "Huizúcar", "Nuevo Cuscatlán", "San José Villanueva", "Zaragoza"],
        "La Libertad Costa": ["Chiltiupán", "Jicalapa", "La Libertad", "Tamanique", "Teotepeque"],
        "La Libertad Sur": ["Comasagua", "Santa Tecla"],
    },
    "Chalatenango": {
        "Chalatenango Norte": ["La Palma", "Citalá", "San Ignacio"],
        "Chalatenango Centro": ["Nueva Concepción", "Tejutla", "La Reina", "Agua Caliente", "Dulce Nombre de María", "El Paraíso", "San Francisco Morazán", "San Rafael", "Santa Rita", "San Fernando"],
        "Chalatenango Sur": ["Chalatenango", "Arcatao", "Azacualpa", "Comalapa", "Concepción Quezaltepeque", "El Carrizal", "La Laguna", "Las Vueltas", "Nombre de Jesús", "Nueva Trinidad", "Ojos de Agua", "Potonico", "San Antonio de La Cruz", "San Antonio Los Ranchos", "San Francisco Lempa", "San Isidro Labrador", "San José Cancasque", "San Miguel de Mercedes", "San José Las Flores", "San Luis del Carmen"],
    },
    "Cuscatlán": {
        "Cuscatlán Norte": ["Suchitoto", "San José Guayabal", "Oratorio de Concepción", "San Bartolomé Perulapán", "San Pedro Perulapán"],
        "Cuscatlán Sur": ["Cojutepeque", "San Rafael Cedros", "Candelaria", "Monte San Juan", "El Carmen", "San Cristóbal", "Santa Cruz Michapa", "San Ramón", "El Rosario", "Santa Cruz Analquito", "Tenancingo"],
    },
    "Cabañas": {
        "Cabañas Este": ["Sensuntepeque", "Victoria", "Dolores", "Guacotecti", "San Isidro"],
        "Cabañas Oeste": ["Ilobasco", "Tejutepeque", "Jutiapa", "Cinquera"],
    },
    "La Paz": {
        "La Paz Oeste": ["Cuyultitán", "Olocuilta", "San Juan Talpa", "San Luis Talpa", "San Pedro Masahuat", "Tapalhuaca", "San Francisco Chinameca"],
        "La Paz Centro": ["El Rosario", "Jerusalén", "Mercedes La Ceiba", "Paraíso de Osorio", "San Antonio Masahuat", "San Emigdio", "San Juan Tepezontes", "San Luis La Herradura", "San Miguel Tepezontes", "San Pedro Nonualco", "Santa María Ostuma", "Santiago Nonualco"],
        "La Paz Este": ["San Juan Nonualco", "San Rafael Obrajuelo", "Zacatecoluca"],
    },
    "La Unión": {
        "La Unión Norte": ["Anamorós", "Bolívar", "Concepción de Oriente", "El Sauce", "Lislique", "Nueva Esparta", "Pasaquina", "Polorós", "San José La Fuente", "Santa Rosa de Lima"],
        "La Unión Sur": ["Conchagua", "El Carmen", "Intipucá", "La Unión", "Meanguera del Golfo", "San Alejo", "Yayantique", "Yucuaiquín"],
    },
    "Usulután": {
        "Usulután Norte": ["Santiago de María", "Alegría", "Berlín", "Mercedes Umaña", "Jucuapa", "El Triunfo", "Estanzuelas", "San Buenaventura", "Nueva Granada"],
        "Usulután Este": ["Usulután", "Jucuarán", "San Dionisio", "Concepción Batres", "Santa María", "Ozatlán", "Tecapán", "Santa Elena", "California", "Ereguayquín"],
        "Usulután Oeste": ["Jiquilisco", "Puerto El Triunfo", "San Agustín", "San Francisco Javier"],
    },
    "Sonsonate": {
        "Sonsonate Norte": ["Juayúa", "Nahuizalco", "Salcoatitán", "Santa Catarina Masahuat"],
        "Sonsonate Centro": ["Sonsonate", "Sonzacate", "Nahulingo", "San Antonio del Monte", "Santo Domingo de Guzmán"],
        "Sonsonate Este": ["Izalco", "Armenia", "Caluco", "San Julián", "Cuisnahuat", "Santa Isabel Ishuatán"],
        "Sonsonate Oeste": ["Acajutla"],
    },
    "Santa Ana": {
        "Santa Ana Norte": ["Masahuat", "Metapán", "Santa Rosa Guachipilín", "Texistepeque"],
        "Santa Ana Centro": ["Santa Ana"],
        "Santa Ana Este": ["Coatepeque", "El Congo"],
        "Santa Ana Oeste": ["Candelaria de la Frontera", "Chalchuapa", "El Porvenir", "San Antonio Pajonal", "San Sebastián Salitrillo", "Santiago de La Frontera"],
    },
    "San Vicente": {
        "San Vicente Norte": ["Apastepeque", "Santa Clara", "San Ildefonso", "San Esteban Catarina", "San Sebastián", "San Lorenzo", "Santo Domingo"],
        "San Vicente Sur": ["San Vicente", "Guadalupe", "Verapaz", "Tepetitán", "Tecoluca", "San Cayetano Istepeque"],
    },
    "San Miguel": {
        "San Miguel Norte": ["Ciudad Barrios", "Sesori", "Nuevo Edén de San Juan", "San Gerardo", "San Luis de La Reina", "Carolina", "San Antonio del Mosco", "Chapeltique"],
        "San Miguel Centro": ["San Miguel", "Comacarán", "Uluazapa", "Moncagua", "Quelepa", "Chirilagua"],
        "San Miguel Oeste": ["Chinameca", "Nueva Guadalupe", "Lolotique", "San Jorge", "San Rafael Oriente", "El Tránsito"],
    },
    "Morazán": {
        "Morazán Norte": ["Arambala", "Cacaopera", "Corinto", "El Rosario", "Joateca", "Jocoaitique", "Meanguera", "Perquín", "San Fernando", "San Isidro", "Torola"],
        "Morazán Sur": ["Chilanga", "Delicias de Concepción", "El Divisadero", "Gualococti", "Guatajiagua", "Jocoro", "Lolotiquillo", "Osicala", "San Carlos", "San Francisco Gotera", "San Simón", "Sensembra", "Sociedad", "Yamabal", "Yoloaiquín"],
    },
}

if LOGO.exists():
    logo_base64 = base64.b64encode(LOGO.read_bytes()).decode()
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:1rem; margin-bottom:0.5rem;">
            <img src="data:image/png;base64,{logo_base64}" width="280">
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="titulo-app">Registro de cementerios</div>', unsafe_allow_html=True)

if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = ""

tab1, tab2 = st.tabs(["Registrar cementerio", "Ver datos capturados"])

with tab1:
    st.subheader("Ubicación")

    col1, col2, col3 = st.columns(3)

    with col1:
        pais = st.selectbox("País", PAYS, index=0)

    with col2:
        departamento = st.selectbox("Departamento", list(DEPARTAMENTOS.keys()))

    municipios_disponibles = list(DEPARTAMENTOS[departamento].keys())

    with col3:
        municipio = st.selectbox("Municipio", municipios_disponibles)

    distritos_disponibles = DEPARTAMENTOS[departamento][municipio]
    distrito = st.selectbox("Distrito", distritos_disponibles)

    st.subheader("Datos del cementerio")

    with st.form("form_cementerio", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            id_cementerio = st.text_input("ID del cementerio")
            nombre = st.text_input("Nombre del cementerio")
            coordenadas = st.text_input("Coordenadas", placeholder="13.6929,-89.2182")
            google_maps_url = st.text_input("Enlace Google Maps")
            observaciones = st.text_area("Observaciones")

        with c2:
            estado = st.selectbox("Estado", ["Provisional", "Aceptado", "Certificado"])
            enlace_principal = st.text_input("Enlace principal")
            enlace_2 = st.text_input("Enlace 2")
            enlace_3 = st.text_input("Enlace 3")
            foto_url = st.text_input("Enlace de la foto")

        enviado = st.form_submit_button("Guardar registro")

    if enviado:
        errores = []
        id_limpio = str(id_cementerio).strip()
        nombre_limpio = str(nombre).strip()
        coordenadas_limpio = str(coordenadas).strip()
        google_maps_url_limpio = str(google_maps_url).strip()
        enlace_principal_limpio = str(enlace_principal).strip()
        enlace_2_limpio = str(enlace_2).strip()
        enlace_3_limpio = str(enlace_3).strip()
        foto_url_limpio = str(foto_url).strip()
        observaciones_limpio = str(observaciones).strip()

        if not id_limpio:
            errores.append("El campo ID del cementerio es obligatorio.")

        if not nombre_limpio:
            errores.append("El nombre del cementerio es obligatorio.")

        if not es_coordenada_valida(coordenadas_limpio):
            errores.append("Las coordenadas no son válidas. Usa el formato: 13.6929,-89.2182")

        if not es_url_valida(google_maps_url_limpio):
            errores.append("El enlace de Google Maps debe iniciar con http:// o https://")

        if not es_url_valida(enlace_principal_limpio):
            errores.append("El enlace principal debe iniciar con http:// o https://")

        if not es_url_valida(enlace_2_limpio):
            errores.append("El enlace 2 debe iniciar con http:// o https://")

        if not es_url_valida(enlace_3_limpio):
            errores.append("El enlace 3 debe iniciar con http:// o https://")

        if not es_url_valida(foto_url_limpio):
            errores.append("El enlace de la foto debe iniciar con http:// o https://")

        if errores:
            for error in errores:
                st.error(error)
        else:
            estado_final = "Aceptado" if enlace_principal_limpio else estado

            registro = {
                "codigo_cementerio": id_limpio,
                "nombre_oficial": nombre_limpio,
                "pais": pais,
                "departamento": departamento,
                "municipio": municipio,
                "distrito": distrito,
                "estado": estado_final,
                "coordenadas": coordenadas_limpio,
                "enlace_principal": enlace_principal_limpio,
                "enlace_2": enlace_2_limpio,
                "enlace_3": enlace_3_limpio,
                "google_maps_url": google_maps_url_limpio,
                "foto_url": foto_url_limpio,
                "observaciones": observaciones_limpio,
            }

            try:
                supabase.table("cementerios").insert(registro).execute()
                st.session_state.mensaje_exito = "Registro guardado correctamente en Supabase."
                st.rerun()
            except Exception as e:
                error_texto = str(e)

                if "duplicate key value violates unique constraint" in error_texto or "23505" in error_texto:
                    st.error(f"Ya existe un cementerio con el ID '{id_limpio}'. Usa un ID diferente.")
                else:
                    st.error(f"No se pudo guardar en Supabase: {e}")

with tab2:
    st.subheader("Datos capturados")

    try:
        datos = obtener_cementerios()

        if datos:
            df = pd.DataFrame(datos)

            c1, c2 = st.columns(2)
            with c1:
                busqueda = st.text_input("Buscar por ID o nombre")
            with c2:
                estado_filtro = st.selectbox(
                    "Filtrar por estado",
                    ["Todos"] + sorted(df["estado"].dropna().unique().tolist())
                )

            c3, c4, c5 = st.columns(3)
            with c3:
                departamento_filtro = st.selectbox(
                    "Filtrar por departamento",
                    ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
                )

            if departamento_filtro != "Todos":
                municipios_disponibles_filtro = sorted(
                    df[df["departamento"] == departamento_filtro]["municipio"].dropna().unique().tolist()
                )
            else:
                municipios_disponibles_filtro = sorted(df["municipio"].dropna().unique().tolist())

            with c4:
                municipio_filtro = st.selectbox(
                    "Filtrar por municipio",
                    ["Todos"] + municipios_disponibles_filtro
                )

            if municipio_filtro != "Todos":
                distritos_disponibles_filtro = sorted(
                    df[df["municipio"] == municipio_filtro]["distrito"].dropna().unique().tolist()
                )
            elif departamento_filtro != "Todos":
                distritos_disponibles_filtro = sorted(
                    df[df["departamento"] == departamento_filtro]["distrito"].dropna().unique().tolist()
                )
            else:
                distritos_disponibles_filtro = sorted(df["distrito"].dropna().unique().tolist())

            with c5:
                distrito_filtro = st.selectbox(
                    "Filtrar por distrito",
                    ["Todos"] + distritos_disponibles_filtro
                )

            df_filtrado = df.copy()

            if busqueda.strip():
                termino = busqueda.strip().lower()
                df_filtrado = df_filtrado[
                    df_filtrado["codigo_cementerio"].astype(str).str.lower().str.contains(termino, na=False) |
                    df_filtrado["nombre_oficial"].astype(str).str.lower().str.contains(termino, na=False)
                ]

            if estado_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["estado"] == estado_filtro]

            if departamento_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["departamento"] == departamento_filtro]

            if municipio_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["municipio"] == municipio_filtro]

            if distrito_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["distrito"] == distrito_filtro]

            df_tabla = df_filtrado.rename(columns={
                "codigo_cementerio": "ID",
                "nombre_oficial": "Nombre",
                "pais": "País",
                "departamento": "Departamento",
                "municipio": "Municipio",
                "distrito": "Distrito",
                "estado": "Estado",
                "coordenadas": "Coordenadas",
                "google_maps_url": "Google Maps",
                "enlace_principal": "Enlace principal",
                "enlace_2": "Enlace 2",
                "enlace_3": "Enlace 3",
                "foto_url": "Foto",
                "observaciones": "Observaciones",
            })

            columnas_visibles = [
                "ID",
                "Nombre",
                "Departamento",
                "Municipio",
                "Distrito",
                "Estado",
                "Coordenadas",
                "Google Maps",
                "Enlace principal",
                "Foto",
                "Observaciones",
            ]

            df_tabla = df_tabla[[col for col in columnas_visibles if col in df_tabla.columns]]

            st.caption(f"Registros encontrados: {len(df_tabla)} de {len(df)}")

            csv_data = convertir_a_csv(df_tabla)

            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    label="Exportar registros filtrados a CSV",
                    data=csv_data,
                    file_name="cementerios_filtrados.csv",
                    mime="text/csv",
                    width="stretch"
                )

            with d2:
                try:
                    excel_data = convertir_a_excel(df_tabla)
                    st.download_button(
                        label="Exportar registros filtrados a Excel",
                        data=excel_data,
                        file_name="cementerios_filtrados.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch"
                    )
                except Exception as e:
                    st.warning(f"No se pudo preparar la exportación a Excel: {e}")

            st.dataframe(
                df_tabla,
                width="stretch",
                hide_index=True,
                column_config={
                    "ID": st.column_config.Column("ID", width="small"),
                    "Nombre": st.column_config.Column("Nombre", width="large"),
                    "Departamento": st.column_config.Column("Departamento", width="medium"),
                    "Municipio": st.column_config.Column("Municipio", width="medium"),
                    "Distrito": st.column_config.Column("Distrito", width="medium"),
                    "Estado": st.column_config.Column("Estado", width="small"),
                    "Coordenadas": st.column_config.Column("Coordenadas", width="medium"),
                    "Google Maps": st.column_config.LinkColumn("Google Maps", width="medium", display_text="Abrir mapa"),
                    "Enlace principal": st.column_config.LinkColumn("Enlace principal", width="medium", display_text="Abrir enlace"),
                    "Foto": st.column_config.LinkColumn("Foto", width="small", display_text="Ver foto"),
                    "Observaciones": st.column_config.Column("Observaciones", width="large"),
                }
            )

            st.divider()
            st.subheader("Editar o eliminar registro")

            opciones = [
                f"{row['codigo_cementerio']} - {row['nombre_oficial']}"
                for row in datos
            ]

            seleccion = st.selectbox("Selecciona un cementerio", options=opciones)

            codigo_seleccionado = seleccion.split(" - ")[0]
            registro_actual = next(
                (row for row in datos if str(row["codigo_cementerio"]) == str(codigo_seleccionado)),
                None
            )

            if registro_actual:
                st.markdown("### Editar registro")

                departamento_edit = registro_actual["departamento"]
                municipio_edit = registro_actual["municipio"]
                distrito_edit = registro_actual["distrito"]

                with st.form("form_editar_cementerio"):
                    e1, e2 = st.columns(2)

                    with e1:
                        nuevo_nombre = st.text_input("Nombre", value=registro_actual.get("nombre_oficial", ""))
                        nuevas_coordenadas = st.text_input("Coordenadas", value=registro_actual.get("coordenadas", ""))
                        nuevo_google_maps = st.text_input("Enlace Google Maps", value=registro_actual.get("google_maps_url", ""))
                        nuevas_observaciones = st.text_area("Observaciones", value=registro_actual.get("observaciones", ""))

                    with e2:
                        estados = ["Provisional", "Aceptado", "Certificado"]
                        estado_actual = registro_actual.get("estado", "Provisional")
                        indice_estado = estados.index(estado_actual) if estado_actual in estados else 0
                        nuevo_estado = st.selectbox("Estado", estados, index=indice_estado)

                        departamentos_lista = list(DEPARTAMENTOS.keys())
                        indice_departamento = departamentos_lista.index(departamento_edit) if departamento_edit in departamentos_lista else 0
                        nuevo_departamento = st.selectbox("Departamento", departamentos_lista, index=indice_departamento)

                        municipios_nuevos = list(DEPARTAMENTOS[nuevo_departamento].keys())
                        indice_municipio = municipios_nuevos.index(municipio_edit) if municipio_edit in municipios_nuevos else 0
                        nuevo_municipio = st.selectbox("Municipio", municipios_nuevos, index=indice_municipio)

                        distritos_nuevos = DEPARTAMENTOS[nuevo_departamento][nuevo_municipio]
                        indice_distrito = distritos_nuevos.index(distrito_edit) if distrito_edit in distritos_nuevos else 0
                        nuevo_distrito = st.selectbox("Distrito", distritos_nuevos, index=indice_distrito)

                        nuevo_enlace_principal = st.text_input("Enlace principal", value=registro_actual.get("enlace_principal", ""))
                        nuevo_enlace_2 = st.text_input("Enlace 2", value=registro_actual.get("enlace_2", ""))
                        nuevo_enlace_3 = st.text_input("Enlace 3", value=registro_actual.get("enlace_3", ""))
                        nueva_foto = st.text_input("Enlace de la foto", value=registro_actual.get("foto_url", ""))

                    guardar_cambios = st.form_submit_button("Guardar cambios")

                if guardar_cambios:
                    errores_edicion = []

                    if not str(nuevo_nombre).strip():
                        errores_edicion.append("El nombre del cementerio es obligatorio.")

                    if not es_coordenada_valida(nuevas_coordenadas):
                        errores_edicion.append("Las coordenadas no son válidas. Usa el formato: 13.6929,-89.2182")

                    if not es_url_valida(nuevo_google_maps):
                        errores_edicion.append("El enlace de Google Maps debe iniciar con http:// o https://")

                    if not es_url_valida(nuevo_enlace_principal):
                        errores_edicion.append("El enlace principal debe iniciar con http:// o https://")

                    if not es_url_valida(nuevo_enlace_2):
                        errores_edicion.append("El enlace 2 debe iniciar con http:// o https://")

                    if not es_url_valida(nuevo_enlace_3):
                        errores_edicion.append("El enlace 3 debe iniciar con http:// o https://")

                    if not es_url_valida(nueva_foto):
                        errores_edicion.append("El enlace de la foto debe iniciar con http:// o https://")

                    if errores_edicion:
                        for error in errores_edicion:
                            st.error(error)
                    else:
                        datos_actualizados = {
                            "nombre_oficial": str(nuevo_nombre).strip(),
                            "pais": "El Salvador",
                            "departamento": nuevo_departamento,
                            "municipio": nuevo_municipio,
                            "distrito": nuevo_distrito,
                            "estado": "Aceptado" if str(nuevo_enlace_principal).strip() else nuevo_estado,
                            "coordenadas": str(nuevas_coordenadas).strip(),
                            "google_maps_url": str(nuevo_google_maps).strip(),
                            "enlace_principal": str(nuevo_enlace_principal).strip(),
                            "enlace_2": str(nuevo_enlace_2).strip(),
                            "enlace_3": str(nuevo_enlace_3).strip(),
                            "foto_url": str(nueva_foto).strip(),
                            "observaciones": str(nuevas_observaciones).strip(),
                        }

                        try:
                            actualizar_cementerio(codigo_seleccionado, datos_actualizados)
                            st.session_state.mensaje_exito = "Registro actualizado correctamente."
                            st.rerun()
                        except Exception as e:
                            st.error(f"No se pudo actualizar el registro: {e}")

                st.markdown("### Eliminar registro")
                confirmar_eliminacion = st.checkbox(
                    f"Confirmo que deseo eliminar el cementerio con ID {codigo_seleccionado}"
                )

                if st.button("Eliminar registro", type="secondary"):
                    if not confirmar_eliminacion:
                        st.warning("Debes confirmar la eliminación antes de continuar.")
                    else:
                        try:
                            eliminar_cementerio(codigo_seleccionado)
                            st.session_state.mensaje_exito = "Registro eliminado correctamente."
                            st.rerun()
                        except Exception as e:
                            st.error(f"No se pudo eliminar el registro: {e}")

        else:
            st.info("Aún no hay registros guardados en Supabase.")

    except Exception as e:
        st.error(f"No se pudieron cargar los datos desde Supabase: {e}")