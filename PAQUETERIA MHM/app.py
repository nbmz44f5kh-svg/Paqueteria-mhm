import streamlit as st
import datetime
import pandas as pd
import os
from PIL import Image

# ==========================================
# RUTA BASE Y CONFIGURACIÓN
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

st.set_page_config(
    page_title="Paquetería MHM",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS PREMIUM (DISEÑO MÓVIL Y FLUIDEZ)
# ==========================================
st.markdown("""
    <style>
    /* Estilos globales */
    .main { background-color: #f8f9fa; }
    
    /* Botones más amplios y táctiles */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        border: none;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.08);
    }
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Ocultar elementos nativos de Streamlit para apariencia app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tarjetas redondeadas */
    [data-testid="stForm"], div[data-testid="stContainer"] {
        border-radius: 12px !important;
        border: 1px solid #e9ecef !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONTROL DE SESIÓN
# ==========================================
if "jornada_iniciada" not in st.session_state:
    st.session_state["jornada_iniciada"] = False
if "usuario_activo" not in st.session_state:
    st.session_state["usuario_activo"] = ""

# ==========================================
# FUNCIONES CON CACHÉ (ALTA VELOCIDAD)
# ==========================================
LISTA_CHOFERES = ["Ninguno / No aplica", "Chofer 1", "Chofer 2", "Chofer 3", "Chofer 4", "Particular"]
LISTA_ESTATUS = ["En Almacén / Bodega", "En Tránsito", "Entregado", "Pendiente de Recolección"]

ARCHIVOS_MODULOS = {
    "John Deere": get_path("registros_john_deere.csv"),
    "Club de Pollos": get_path("registros_club_de_pollos.csv"),
    "Laboratorios": get_path("registros_laboratorios.csv"),
    "Andrea": get_path("registros_andrea.csv"),
    "Paquetería General": get_path("registros_paqueteria_general.csv")
}

@st.cache_resource(show_spinner=False)
def cargar_imagen_memoria(ruta_completa):
    """Carga y mantiene la imagen en RAM para evitar lectura de disco."""
    if os.path.exists(ruta_completa):
        try:
            return Image.open(ruta_completa)
        except Exception:
            return None
    return None

def mostrar_logo(nombre_base, ancho=120):
    extensiones = [".png", ".jpg", ".jpeg", ".webp", ""]
    variaciones = [nombre_base.lower()]
    
    if "john" in nombre_base.lower():
        variaciones.append(nombre_base.lower().replace("john", "jhon"))
    elif "jhon" in nombre_base.lower():
        variaciones.append(nombre_base.lower().replace("jhon", "john"))

    for var in variaciones:
        for ext in extensiones:
            archivo_buscado = get_path(f"{var}{ext}")
            img = cargar_imagen_memoria(archivo_buscado)
            if img:
                st.image(img, width=ancho)
                return
    st.caption(f"[{nombre_base}]")

@st.cache_data(show_spinner=False, ttl=300)
def cargar_y_asegurar_estatus(archivo_csv):
    """Carga veloz de datos en caché."""
    df = pd.read_csv(archivo_csv)
    if "Estatus" not in df.columns:
        df["Estatus"] = "En Tránsito"
    
    cols = list(df.columns)
    if "Estatus" in cols:
        cols.remove("Estatus")
        idx = cols.index("Destino") + 1 if "Destino" in cols else 1
        cols.insert(idx, "Estatus")
        df = df[cols]
    return df

def guardar_registro(datos_dict, nombre_modulo):
    nombre_archivo = f"registros_{nombre_modulo.lower().replace(' ', '_')}.csv"
    archivo_csv = get_path(nombre_archivo)
    df_nuevo = pd.DataFrame([datos_dict])
    
    if not os.path.exists(archivo_csv):
        df_nuevo.to_csv(archivo_csv, index=False)
    else:
        df_existente = pd.read_csv(archivo_csv)
        df_completo = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_completo.to_csv(archivo_csv, index=False)
        
    st.cache_data.clear()  # Limpia la caché para refrescar los datos al momento
    st.success("✅ Registro guardado exitosamente.")

# ==========================================
# PANTALLA 1: LOGIN LIMPIO
# ==========================================
if not st.session_state["jornada_iniciada"]:
    st.write("")
    col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
    
    with col_centro:
        with st.container(border=True):
            c_logo_a, c_logo_b, c_logo_c = st.columns([1, 2, 1])
            with c_logo_b:
                mostrar_logo("logo_mhm", ancho=150)
                
            st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>Control de Operaciones</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray; font-size: 0.9em;'>Ingresa tus credenciales</p>", unsafe_allow_html=True)
            
            correo_user = st.text_input("Usuario", placeholder="ejemplo@mhm.com")
            pass_user = st.text_input("Contraseña", type="password")
            
            st.write("")
            if st.button("🚀 Iniciar Jornada", use_container_width=True, type="primary"):
                if correo_user != "":
                    st.session_state["jornada_iniciada"] = True
                    st.session_state["usuario_activo"] = correo_user
                    st.rerun()
                else:
                    st.error("Ingresa tu usuario.")
    st.stop()

# ==========================================
# PANTALLA 2: APLICACIÓN PRINCIPAL
# ==========================================

with st.sidebar:
    mostrar_logo("logo_mhm", ancho=120)
    st.markdown(f"👤 **Operador:** `{st.session_state['usuario_activo']}`")
    
    if st.button("🔴 Terminar Jornada", use_container_width=True):
        st.session_state["jornada_iniciada"] = False
        st.session_state["usuario_activo"] = ""
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    modulo = st.radio(
        "Módulo Activo:",
        [
            "John Deere",
            "Club de Pollos",
            "Laboratorios",
            "Andrea",
            "Paquetería General",
            "Control de Estatus y Resumen"
        ]
    )

st.title("Sistema de Paquetería y Traspasos")

fecha_actual = datetime.date.today()

# 1. JOHN DEERE
if modulo == "John Deere":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_john_deere", ancho=90)
    with col_titulo:
        st.subheader("Operaciones John Deere")

    with st.form("form_jd", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_jd = st.date_input("Fecha", value=fecha_actual)
            guia_jd = st.text_input("Número de Guía / Paquete")
            origen_jd = st.text_input("Origen / Sucursal", value="Monterrey")
            destino_jd = st.text_input("Destino Final / Sucursal")
            estatus_jd = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            
        with c2:
            st.markdown("**Asignación de Choferes**")
            chofer1_jd = st.selectbox("Chofer que recolecta", LISTA_CHOFERES)
            chofer2_jd = st.selectbox("Chofer que traslada", LISTA_CHOFERES)
            chofer3_jd = st.selectbox("Chofer que entrega", LISTA_CHOFERES)

        notas_jd = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro John Deere", type="primary"):
            if not guia_jd:
                st.error("⚠️ Falta ingresar el número de guía.")
            else:
                guardar_registro({
                    "Fecha": fecha_jd.strftime("%Y/%m/%d"),
                    "Guia": guia_jd,
                    "Origen": origen_jd,
                    "Destino": destino_jd,
                    "Estatus": estatus_jd,
                    "Chofer_Recolecta": chofer1_jd,
                    "Chofer_Traslada": chofer2_jd,
                    "Chofer_Entrega": chofer3_jd,
                    "Notas": notas_jd
                }, "John Deere")

# 2. CLUB DE POLLOS
elif modulo == "Club de Pollos":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_club_pollos", ancho=90)
    with col_titulo:
        st.subheader("Control de Insumos Club de Pollos")

    with st.form("form_cp", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_cp = st.date_input("Fecha", value=fecha_actual)
            folio_cp = st.text_input("Folio / Identificador")
            origen_cp = st.text_input("Origen / Sucursal", value="Monterrey")
            destino_cp = st.text_input("Destino Final / Sucursal")
            estatus_cp = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer1_cp = st.selectbox("Chofer que recolecta", LISTA_CHOFERES)
            chofer2_cp = st.selectbox("Chofer que entrega", LISTA_CHOFERES)
            
        with c2:
            st.markdown("**Conteo de Cajas e Insumos**")
            cajas_g = st.number_input("Cajas Grandes", min_value=0, step=1, value=0)
            cajas_m = st.number_input("Cajas Medianas", min_value=0, step=1, value=0)
            cajas_ch = st.number_input("Cajas Chicas", min_value=0, step=1, value=0)
            insumos_texto = st.text_input("Insumos recibidos")

        notas_cp = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro Club de Pollos", type="primary"):
            guardar_registro({
                "Fecha": fecha_cp.strftime("%Y/%m/%d"),
                "Guia": folio_cp if folio_cp else "S/N",
                "Origen": origen_cp,
                "Destino": destino_cp,
                "Estatus": estatus_cp,
                "Chofer_Recolecta": chofer1_cp,
                "Chofer_Entrega": chofer2_cp,
                "Cajas_Grandes": cajas_g,
                "Cajas_Medianas": cajas_m,
                "Cajas_Chicas": cajas_ch,
                "Insumos": insumos_texto,
                "Notas": notas_cp
            }, "Club de Pollos")

# 3. LABORATORIOS
elif modulo == "Laboratorios":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_laboratorios", ancho=90)
    with col_titulo:
        st.subheader("Registro de Operaciones Laboratorios")

    with st.form("form_lab", clear_on_submit=True):
        ca, cb = st.columns(2)
        with ca:
            fecha_lab = st.date_input("Fecha", value=fecha_actual)
            guia_lab = st.text_input("Número de Guía Laboratorio")
            origen_lab = st.text_input("Origen / Sucursal", value="Río Bravo")
            chofer1_lab = st.selectbox("Chofer que recolecta", LISTA_CHOFERES)
        with cb:
            destino_lab = st.text_input("Destino Final / Sucursal")
            estatus_lab = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer2_lab = st.selectbox("Chofer que entrega", LISTA_CHOFERES)
            
        notas_lab = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro Laboratorios", type="primary"):
            guardar_registro({
                "Fecha": fecha_lab.strftime("%Y/%m/%d"),
                "Guia": guia_lab,
                "Origen": origen_lab,
                "Destino": destino_lab,
                "Estatus": estatus_lab,
                "Chofer_Recolecta": chofer1_lab,
                "Chofer_Entrega": chofer2_lab,
                "Notas": notas_lab
            }, "Laboratorios")

# 4. ANDREA
elif modulo == "Andrea":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_andrea", ancho=90)
    with col_titulo:
        st.subheader("Registro de Traspasos Andrea")

    with st.form("form_andrea", clear_on_submit=True):
        ca, cb = st.columns(2)
        with ca:
            fecha_and = st.date_input("Fecha", value=fecha_actual)
            guia_and = st.text_input("Número de Guía / Traspaso Andrea")
            origen_and = st.text_input("Sucursal Origen")
        with cb:
            destino_and = st.text_input("Sucursal Destino")
            estatus_and = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer_and = st.selectbox("Chofer que traslada / entrega", LISTA_CHOFERES)
            
        notas_and = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Traspaso Andrea", type="primary"):
            guardar_registro({
                "Fecha": fecha_and.strftime("%Y/%m/%d"),
                "Guia": guia_and,
                "Origen": origen_and,
                "Destino": destino_and,
                "Estatus": estatus_and,
                "Chofer_Entrega": chofer_and,
                "Notas": notas_and
            }, "Andrea")

# 5. PAQUETERÍA GENERAL
elif modulo == "Paquetería General":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_mhm", ancho=70)
    with col_titulo:
        st.subheader("Paquetería General MHM")
    
    with st.form("form_gen", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_gen = st.date_input("Fecha", value=fecha_actual)
            empresa_gen = st.selectbox("Empresa / Paquetería", ["DHL", "FedEx", "Estafeta", "Sendex", "99 Minutos", "Flecha Amarilla", "Local MHM"])
            guia_gen = st.text_input("Número de Guía")
            origen_gen = st.text_input("Origen / Sucursal", value="Río Bravo")
        with c2:
            destino_gen = st.text_input("Destino Final / Sucursal")
            estatus_gen = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer_gen = st.selectbox("Chofer que traslada / entrega", LISTA_CHOFERES)
            
        notas_gen = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro General", type="primary"):
            guardar_registro({
                "Fecha": fecha_gen.strftime("%Y/%m/%d"),
                "Empresa": empresa_gen,
                "Guia": guia_gen,
                "Origen": origen_gen,
                "Destino": destino_gen,
                "Estatus": estatus_gen,
                "Chofer_Entrega": chofer_gen,
                "Notas": notas_gen
            }, "Paqueteria_General")

# 6. CONTROL DE ESTATUS Y RESUMEN OPERATIVO
elif modulo == "Control de Estatus y Resumen":
    st.subheader("Control de Estatus y Resumen Operativo")
    
    tab_almacen, tab_choferes, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 En Almacén", 
        "🚚 Rutas por Chofer",
        "John Deere", 
        "Club de Pollos", 
        "Laboratorios",
        "Andrea", 
        "Paquetería General"
    ])
    
    with tab_almacen:
        st.markdown("### 🏬 Paquetes en Almacén / Bodega")
        lista_almacen = []
        for modulo_nom, archivo in ARCHIVOS_MODULOS.items():
            if os.path.exists(archivo):
                df = cargar_y_asegurar_estatus(archivo)
                df_filtrado = df[df["Estatus"] == "En Almacén / Bodega"].copy()
                if not df_filtrado.empty:
                    df_filtrado.insert(0, "Módulo", modulo_nom)
                    lista_almacen.append(df_filtrado)
                        
        if lista_almacen:
            df_almacen_total = pd.concat(lista_almacen, ignore_index=True)
            st.dataframe(df_almacen_total, use_container_width=True)
        else:
            st.info("No hay paquetes en almacén.")

    with tab_choferes:
        st.markdown("### 🚚 Resumen de Rutas por Chofer")
        lista_todas = []
        for modulo_nom, archivo in ARCHIVOS_MODULOS.items():
            if os.path.exists(archivo):
                df_temp = cargar_y_asegurar_estatus(archivo)
                df_temp.insert(0, "Módulo", modulo_nom)
                lista_todas.append(df_temp)
                
        if lista_todas:
            df_global = pd.concat(lista_todas, ignore_index=True)
            c_fec, c_chof = st.columns([1, 2])
            with c_fec:
                fechas_disponibles = sorted(df_global["Fecha"].dropna().unique(), reverse=True)
                fecha_sel = st.selectbox("Fecha:", ["Todas las Fechas"] + list(fechas_disponibles))
            
            with c_chof:
                choferes_activos = [ch for ch in LISTA_CHOFERES if ch != "Ninguno / No aplica"]
                chofer_sel = st.selectbox("Chofer:", choferes_activos)

            if fecha_sel != "Todas las Fechas":
                df_global = df_global[df_global["Fecha"] == fecha_sel]

            st.divider()

            col_recolecta = "Chofer_Recolecta" if "Chofer_Recolecta" in df_global.columns else ("Chofer_Trae" if "Chofer_Trae" in df_global.columns else None)
            col_traslada = "Chofer_Traslada" if "Chofer_Traslada" in df_global.columns else ("Chofer_Ruta" if "Chofer_Ruta" in df_global.columns else None)
            col_entrega = "Chofer_Entrega" if "Chofer_Entrega" in df_global.columns else ("Chofer" if "Chofer" in df_global.columns else None)

            mov_recolecta = df_global[df_global[col_recolecta] == chofer_sel] if col_recolecta and col_recolecta in df_global.columns else pd.DataFrame()
            mov_traslada = df_global[df_global[col_traslada] == chofer_sel] if col_traslada and col_traslada in df_global.columns else pd.DataFrame()
            mov_entrega = df_global[df_global[col_entrega] == chofer_sel] if col_entrega and col_entrega in df_global.columns else pd.DataFrame()

            t1, t2, t3 = st.tabs(["📥 Recolecta", "🚚 Traslada", "✅ Entrega"])
            with t1:
                st.dataframe(mov_recolecta, use_container_width=True) if not mov_recolecta.empty else st.info("Sin registros.")
            with t2:
                st.dataframe(mov_traslada, use_container_width=True) if not mov_traslada.empty else st.info("Sin registros.")
            with t3:
                st.dataframe(mov_entrega, use_container_width=True) if not mov_entrega.empty else st.info("Sin registros.")
        else:
            st.info("Sin datos acumulados.")

    modulos_tablas = [
        (tab1, get_path("registros_john_deere.csv"), "John Deere", "jd"),
        (tab2, get_path("registros_club_de_pollos.csv"), "Club de Pollos", "cp"),
        (tab3, get_path("registros_laboratorios.csv"), "Laboratorios", "lab"),
        (tab4, get_path("registros_andrea.csv"), "Andrea", "and"),
        (tab5, get_path("registros_paqueteria_general.csv"), "Paquetería General", "gen")
    ]

    for tab_obj, archivo_csv, nombre_mod, key_suffix in modulos_tablas:
        with tab_obj:
            if os.path.exists(archivo_csv):
                df = cargar_y_asegurar_estatus(archivo_csv)
                
                column_config = {
                    "Estatus": st.column_config.SelectboxColumn("Estatus", options=LISTA_ESTATUS, required=True),
                    "Chofer_Recolecta": st.column_config.SelectboxColumn("Chofer recolecta", options=LISTA_CHOFERES),
                    "Chofer_Traslada": st.column_config.SelectboxColumn("Chofer traslada", options=LISTA_CHOFERES),
                    "Chofer_Entrega": st.column_config.SelectboxColumn("Chofer entrega", options=LISTA_CHOFERES)
                }
                
                df_editado = st.data_editor(
                    df,
                    column_config=column_config,
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"editor_{key_suffix}"
                )
                
                if st.button(f"💾 Guardar Cambios ({nombre_mod})", key=f"btn_save_{key_suffix}", type="primary"):
                    df_editado.to_csv(archivo_csv, index=False)
                    st.cache_data.clear()
                    st.success("¡Cambios guardados!")
                    st.rerun()
            else:
                st.info(f"Sin registros en {nombre_mod}.")
