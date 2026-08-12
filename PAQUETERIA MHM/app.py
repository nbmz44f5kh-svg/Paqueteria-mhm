import streamlit as st
import datetime
import pandas as pd
import os
from PIL import Image

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Paquetería MHM - Sistema de Control", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# CONTROL DE SESIÓN (INICIAR / TERMINAR JORNADA)
# ==========================================
if "jornada_iniciada" not in st.session_state:
    st.session_state["jornada_iniciada"] = False
if "usuario_activo" not in st.session_state:
    st.session_state["usuario_activo"] = ""

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def mostrar_logo(nombre_base, ancho=120):
    extensiones = [".png", ".jpg", ".jpeg", ".webp", ""]
    variaciones = [nombre_base.lower()]
    
    if "john" in nombre_base.lower():
        variaciones.append(nombre_base.lower().replace("john", "jhon"))
    elif "jhon" in nombre_base.lower():
        variaciones.append(nombre_base.lower().replace("jhon", "john"))

    for var in variaciones:
        for ext in extensiones:
            archivo_buscado = f"{var}{ext}"
            if os.path.exists(archivo_buscado):
                try:
                    img = Image.open(archivo_buscado)
                    st.image(img, width=ancho)
                    return
                except Exception:
                    pass
    st.caption(f"[{nombre_base}]")

def guardar_registro(datos_dict, nombre_modulo):
    archivo_csv = f"registros_{nombre_modulo.lower().replace(' ', '_')}.csv"
    df_nuevo = pd.DataFrame([datos_dict])
    
    if not os.path.exists(archivo_csv):
        df_nuevo.to_csv(archivo_csv, index=False)
    else:
        df_existente = pd.read_csv(archivo_csv)
        df_completo = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_completo.to_csv(archivo_csv, index=False)
        
    st.success("✅ Registro guardado exitosamente.")

def cargar_y_asegurar_estatus(archivo_csv):
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

LISTA_CHOFERES = ["Ninguno / No aplica", "Chofer 1", "Chofer 2", "Chofer 3", "Chofer 4", "Particular"]
LISTA_ESTATUS = ["En Almacén / Bodega", "En Tránsito", "Entregado", "Pendiente de Recolección"]

# ==========================================
# PANTALLA 1: INICIAR JORNADA (LOGIN LIMPIO)
# ==========================================
if not st.session_state["jornada_iniciada"]:
    st.write("")
    st.write("")
    col_izq, col_centro, col_der = st.columns([1, 1.2, 1])
    
    with col_centro:
        with st.container(border=True):
            c_logo_a, c_logo_b, c_logo_c = st.columns([1, 2, 1])
            with c_logo_b:
                mostrar_logo("logo_mhm", ancho=160)
                
            st.markdown("<h3 style='text-align: center;'>Control de Operaciones</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Ingresa tus credenciales para iniciar jornada</p>", unsafe_allow_html=True)
            
            correo_user = st.text_input("Correo / Usuario", placeholder="ejemplo@mhm.com")
            pass_user = st.text_input("Contraseña", type="password")
            
            st.write("")
            if st.button("🚀 Iniciar Jornada", use_container_width=True, type="primary"):
                if correo_user != "":
                    st.session_state["jornada_iniciada"] = True
                    st.session_state["usuario_activo"] = correo_user
                    st.rerun()
                else:
                    st.error("Por favor ingresa tu correo o usuario.")
    st.stop()

# ==========================================
# PANTALLA 2: APLICACIÓN PRINCIPAL
# ==========================================

# Menú Lateral
with st.sidebar:
    mostrar_logo("logo_mhm", ancho=130)
    st.markdown(f"👤 **Operador:** `{st.session_state['usuario_activo']}`")
    
    if st.button("🔴 Terminar Jornada", use_container_width=True):
        st.session_state["jornada_iniciada"] = False
        st.session_state["usuario_activo"] = ""
        st.rerun()
        
    st.divider()
    st.title("Navegación")
    modulo = st.radio(
        "Selecciona Módulo:",
        [
            "John Deere",
            "Club de Pollos",
            "Laboratorios",
            "Andrea",
            "Paquetería General",
            "Control de Estatus y Resumen"
        ]
    )

st.title("Registro de Paquetería y Traspasos")
st.caption(f"Módulo activo: {modulo}")

fecha_actual = datetime.date.today()

# 1. JOHN DEERE
if modulo == "John Deere":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_john_deere", ancho=100)
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
            chofer1_jd = st.selectbox("Chofer 1 (Trae de MTY / Recibe)", LISTA_CHOFERES)
            chofer2_jd = st.selectbox("Chofer 2 (Toma / Hace Ruta)", LISTA_CHOFERES)
            chofer3_jd = st.selectbox("Chofer 3 (Entrega)", LISTA_CHOFERES)

        notas_jd = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro John Deere"):
            if not guia_jd:
                st.error("⚠️ Falta ingresar el número de guía.")
            else:
                guardar_registro({
                    "Fecha": fecha_jd.strftime("%Y/%m/%d"),
                    "Guia": guia_jd,
                    "Origen": origen_jd,
                    "Destino": destino_jd,
                    "Estatus": estatus_jd,
                    "Chofer_Trae": chofer1_jd,
                    "Chofer_Ruta": chofer2_jd,
                    "Chofer_Entrega": chofer3_jd,
                    "Notas": notas_jd
                }, "John Deere")

# 2. CLUB DE POLLOS
elif modulo == "Club de Pollos":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_club_pollos", ancho=100)
    with col_titulo:
        st.subheader("Control de Insumos Club de Pollos")

    with st.form("form_cp", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_cp = st.date_input("Fecha", value=fecha_actual)
            folio_cp = st.text_input("Folio / Identificador de Envío")
            origen_cp = st.text_input("Origen / Sucursal", value="Monterrey")
            destino_cp = st.text_input("Destino Final / Sucursal")
            estatus_cp = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer1_cp = st.selectbox("Chofer 1 (Trae / Recibe)", LISTA_CHOFERES)
            chofer2_cp = st.selectbox("Chofer 2 (Entrega)", LISTA_CHOFERES)
            
        with c2:
            st.markdown("**Conteo de Cajas e Insumos**")
            cajas_g = st.number_input("Cajas Grandes", min_value=0, step=1, value=0)
            cajas_m = st.number_input("Cajas Medianas", min_value=0, step=1, value=0)
            cajas_ch = st.number_input("Cajas Chicas", min_value=0, step=1, value=0)
            insumos_texto = st.text_input("Insumos recibidos (Escribe los artículos)")

        notas_cp = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro Club de Pollos"):
            guardar_registro({
                "Fecha": fecha_cp.strftime("%Y/%m/%d"),
                "Guia": folio_cp if folio_cp else "S/N",
                "Origen": origen_cp,
                "Destino": destino_cp,
                "Estatus": estatus_cp,
                "Chofer_Trae": chofer1_cp,
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
        mostrar_logo("logo_laboratorios", ancho=100)
    with col_titulo:
        st.subheader("Registro de Operaciones Laboratorios")

    with st.form("form_lab", clear_on_submit=True):
        ca, cb = st.columns(2)
        with ca:
            fecha_lab = st.date_input("Fecha", value=fecha_actual)
            guia_lab = st.text_input("Número de Guía Laboratorio")
            origen_lab = st.text_input("Origen / Sucursal", value="Río Bravo")
            chofer1_lab = st.selectbox("Chofer Trae / Recibe", LISTA_CHOFERES)
        with cb:
            destino_lab = st.text_input("Destino Final / Sucursal")
            estatus_lab = st.selectbox("Estatus Inicial", LISTA_ESTATUS)
            chofer2_lab = st.selectbox("Chofer Entrega", LISTA_CHOFERES)
            
        notas_lab = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro Laboratorios"):
            guardar_registro({
                "Fecha": fecha_lab.strftime("%Y/%m/%d"),
                "Guia": guia_lab,
                "Origen": origen_lab,
                "Destino": destino_lab,
                "Estatus": estatus_lab,
                "Chofer_Trae": chofer1_lab,
                "Chofer_Entrega": chofer2_lab,
                "Notas": notas_lab
            }, "Laboratorios")

# 4. ANDREA
elif modulo == "Andrea":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_andrea", ancho=100)
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
            chofer_and = st.selectbox("Chofer Responsable", LISTA_CHOFERES)
            
        notas_and = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Traspaso Andrea"):
            guardar_registro({
                "Fecha": fecha_and.strftime("%Y/%m/%d"),
                "Guia": guia_and,
                "Origen": origen_and,
                "Destino": destino_and,
                "Estatus": estatus_and,
                "Chofer": chofer_and,
                "Notas": notas_and
            }, "Andrea")

# 5. PAQUETERÍA GENERAL
elif modulo == "Paquetería General":
    col_logo, col_titulo = st.columns([1, 5])
    with col_logo:
        mostrar_logo("logo_mhm", ancho=80)
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
            chofer_gen = st.selectbox("Chofer Encargado", LISTA_CHOFERES)
            
        notas_gen = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar Registro General"):
            guardar_registro({
                "Fecha": fecha_gen.strftime("%Y/%m/%d"),
                "Empresa": empresa_gen,
                "Guia": guia_gen,
                "Origen": origen_gen,
                "Destino": destino_gen,
                "Estatus": estatus_gen,
                "Chofer": chofer_gen,
                "Notas": notas_gen
            }, "Paqueteria_General")

# 6. CONTROL DE ESTATUS Y RESUMEN OPERATIVO
elif modulo == "Control de Estatus y Resumen":
    st.subheader("Control de Estatus y Resumen Operativo")
    
    tab_almacen, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 En Almacén", 
        "John Deere", 
        "Club de Pollos", 
        "Laboratorios",
        "Andrea", 
        "Paquetería General"
    ])
    
    with tab_almacen:
        st.markdown("### 🏬 Registro Consolidado: Paquetes e Insumos Actualmente en Almacén")
        archivos_modulos = {
            "John Deere": "registros_john_deere.csv",
            "Club de Pollos": "registros_club_de_pollos.csv",
            "Laboratorios": "registros_laboratorios.csv",
            "Andrea": "registros_andrea.csv",
            "Paquetería General": "registros_paqueteria_general.csv"
        }
        
        lista_almacen = []
        for modulo_nom, archivo in archivos_modulos.items():
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
            st.info("No hay registros actualmente marcados 'En Almacén / Bodega'.")

    modulos_tablas = [
        (tab1, "registros_john_deere.csv", "John Deere", "jd"),
        (tab2, "registros_club_de_pollos.csv", "Club de Pollos", "cp"),
        (tab3, "registros_laboratorios.csv", "Laboratorios", "lab"),
        (tab4, "registros_andrea.csv", "Andrea", "and"),
        (tab5, "registros_paqueteria_general.csv", "Paquetería General", "gen")
    ]

    for tab_obj, archivo_csv, nombre_mod, key_suffix in modulos_tablas:
        with tab_obj:
            if os.path.exists(archivo_csv):
                df = cargar_y_asegurar_estatus(archivo_csv)
                
                st.markdown(f"#### ⚙️ Gestionar Registros de {nombre_mod}")
                
                if "Guia" in df.columns:
                    opciones_guias = df["Guia"].astype(str).tolist()
                else:
                    opciones_guias = [f"Fila {i+1}" for i in range(len(df))]
                
                if len(opciones_guias) > 0:
                    c_sel, c_est, c_btn_upd, c_btn_del = st.columns([2.5, 2, 1.2, 1.2])
                    
                    with c_sel:
                        guia_seleccionada = st.selectbox(
                            "Selecciona Registro / Guía:", 
                            opciones_guias, 
                            key=f"sel_{key_suffix}"
                        )
                    with c_est:
                        nuevo_estatus = st.selectbox(
                            "Nuevo Estatus:", 
                            LISTA_ESTATUS, 
                            key=f"est_{key_suffix}"
                        )
                    with c_btn_upd:
                        st.write("")
                        st.write("")
                        if st.button("🔄 Actualizar", key=f"btn_upd_{key_suffix}", use_container_width=True):
                            if "Guia" in df.columns:
                                df.loc[df["Guia"].astype(str) == guia_seleccionada, "Estatus"] = nuevo_estatus
                            else:
                                idx = int(guia_seleccionada.replace("Fila ", "")) - 1
                                df.loc[idx, "Estatus"] = nuevo_estatus
                                
                            df.to_csv(archivo_csv, index=False)
                            st.success(f"Estatus actualizado a '{nuevo_estatus}'.")
                            st.rerun()

                    with c_btn_del:
                        st.write("")
                        st.write("")
                        if st.button("🗑️ Eliminar", key=f"btn_del_{key_suffix}", use_container_width=True):
                            if "Guia" in df.columns:
                                df = df[df["Guia"].astype(str) != guia_seleccionada]
                            else:
                                idx = int(guia_seleccionada.replace("Fila ", "")) - 1
                                df = df.drop(index=idx)
                                
                            df.to_csv(archivo_csv, index=False)
                            st.success("Registro eliminado correctamente.")
                            st.rerun()

                st.divider()
                st.markdown(f"**Tabla Histórica de {nombre_mod}:**")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"No hay registros guardados en {nombre_mod}.")