


from pathlib import Path

path = Path("greta_webappv2.py")
text = path.read_text()

# -------------------------------------------------
# 1) Agregar datos iniciales: catálogo, ventas, usuarios, settings
# -------------------------------------------------
marker = "\n\ninit_data()\n"
insert_data = r'''

    if "catalogo" not in st.session_state:
        st.session_state.catalogo = pd.DataFrame([
            {
                "Servicio": "Manicure gel",
                "Categoria": "Manos",
                "Duracion min": 60,
                "Precio": 55.0,
                "Activo": True,
                "Descripcion": "Aplicación de gel con limpieza básica."
            },
            {
                "Servicio": "Acrílico",
                "Categoria": "Manos",
                "Duracion min": 90,
                "Precio": 75.0,
                "Activo": True,
                "Descripcion": "Set acrílico completo."
            },
            {
                "Servicio": "Pedicure",
                "Categoria": "Pies",
                "Duracion min": 60,
                "Precio": 50.0,
                "Activo": True,
                "Descripcion": "Pedicure sencillo."
            }
        ])

    if "ventas" not in st.session_state:
        st.session_state.ventas = pd.DataFrame([
            {
                "Fecha": str(date.today()),
                "Cliente": "Maria Lopez",
                "Servicio": "Manicure gel",
                "Empleado": "Greta",
                "Metodo pago": "Tarjeta",
                "Subtotal": 55.0,
                "Descuento": 0.0,
                "Total": 55.0,
                "Notas": "Venta demo"
            }
        ])

    if "usuarios" not in st.session_state:
        st.session_state.usuarios = pd.DataFrame([
            {
                "Usuario": "admin",
                "Nombre": "Greta",
                "Rol": "Admin",
                "Activo": True
            },
            {
                "Usuario": "recepcion",
                "Nombre": "Recepción",
                "Rol": "Recepción",
                "Activo": True
            },
            {
                "Usuario": "eva",
                "Nombre": "Eva",
                "Rol": "Empleada",
                "Activo": True
            }
        ])

    if "app_settings" not in st.session_state:
        st.session_state.app_settings = {
            "nombre_negocio": "Greta Studio",
            "telefono_negocio": "",
            "direccion_negocio": "",
            "moneda": "USD",
            "online_booking_activo": True,
            "requiere_confirmacion_online": True
        }
'''

if insert_data.strip() not in text:
    text = text.replace(marker, insert_data + marker)

# -------------------------------------------------
# 2) Agregar helpers de roles después de import_excel
# -------------------------------------------------
marker_helpers = '''
def import_excel(file):
    xls = pd.ExcelFile(file)
    if "Clientes" in xls.sheet_names:
        st.session_state.clientes = pd.read_excel(file, sheet_name="Clientes")
    if "Empleados" in xls.sheet_names:
        st.session_state.empleados = pd.read_excel(file, sheet_name="Empleados")
    if "Citas" in xls.sheet_names:
        st.session_state.citas = pd.read_excel(file, sheet_name="Citas")
    if "Inventario" in xls.sheet_names:
        st.session_state.inventario = pd.read_excel(file, sheet_name="Inventario")
    if "Gastos" in xls.sheet_names:
        st.session_state.gastos = pd.read_excel(file, sheet_name="Gastos")
'''

role_helpers = marker_helpers + r'''

# =========================
# ROLES Y PERMISOS
# =========================

ROLE_MENUS = {
    "Admin": [
        "Inicio",
        "Agenda Fresha",
        "Calendario",
        "Nueva cita",
        "Ventas",
        "Lista de clientes",
        "Catálogo",
        "Online booking",
        "Reportes",
        "WhatsApp",
        "Empleados",
        "Nómina",
        "Inventario",
        "Finanzas",
        "Settings",
        "Excel / Backup"
    ],
    "Recepción": [
        "Inicio",
        "Agenda Fresha",
        "Calendario",
        "Nueva cita",
        "Ventas",
        "Lista de clientes",
        "Catálogo",
        "Online booking",
        "WhatsApp"
    ],
    "Empleada": [
        "Inicio",
        "Agenda Fresha",
        "Calendario",
        "Lista de clientes",
        "WhatsApp"
    ]
}


def get_allowed_menus(role):
    return ROLE_MENUS.get(role, ROLE_MENUS["Empleada"])


def require_admin():
    if st.session_state.get("current_role", "Admin") != "Admin":
        st.warning("Esta sección es solo para Admin.")
        st.stop()
'''

if "ROLE_MENUS = {" not in text:
    text = text.replace(marker_helpers, role_helpers)

# -------------------------------------------------
# 3) Reemplazar sidebar por menú con roles
# -------------------------------------------------
old_sidebar = '''menu = st.sidebar.radio(
    "Menú principal",
    [
        "Inicio",
        "Agenda Fresha",
        "Calendario",
        "Nueva cita",
        "Clientes",
        "WhatsApp",
        "Empleados",
        "Nómina",
        "Inventario",
        "Finanzas",
        "Excel / Backup"
    ]
)
'''

new_sidebar = '''st.sidebar.markdown("### Usuario / Rol")

roles_disponibles = ["Admin", "Recepción", "Empleada"]

current_role = st.sidebar.selectbox(
    "Entrar como",
    roles_disponibles,
    index=roles_disponibles.index(st.session_state.get("current_role", "Admin")),
    key="current_role_selector"
)

st.session_state.current_role = current_role

st.sidebar.caption(f"Rol activo: {current_role}")

menu = st.sidebar.radio(
    "Menú principal",
    get_allowed_menus(current_role)
)
'''

if old_sidebar in text:
    text = text.replace(old_sidebar, new_sidebar)

# -------------------------------------------------
# 4) Cambiar bloque Clientes a Lista de clientes
# -------------------------------------------------
text = text.replace('elif menu == "Clientes":\n    st.header("Clientes")', 'elif menu == "Lista de clientes":\n    st.header("Lista de clientes")')

# -------------------------------------------------
# 5) Insertar nuevos módulos antes de WHATSAPP
# -------------------------------------------------
whatsapp_marker = '''
# =========================
# WHATSAPP
# =========================
'''

new_modules = r'''

# =========================
# VENTAS
# =========================

elif menu == "Ventas":
    render_fresha_hero(
        "Ventas",
        "Registra pagos, revisa ventas del día y conecta cada venta con una cita o servicio."
    )

    ventas = st.session_state.ventas.copy()
    citas = st.session_state.citas.copy()
    catalogo = st.session_state.catalogo.copy()

    ventas["Total"] = pd.to_numeric(ventas["Total"], errors="coerce").fillna(0)
    ventas["Fecha_dt"] = pd.to_datetime(ventas["Fecha"], errors="coerce")

    hoy = date.today()
    ventas_hoy = ventas[ventas["Fecha_dt"].dt.date == hoy] if not ventas.empty else ventas

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Ventas hoy", money(ventas_hoy["Total"].sum() if not ventas_hoy.empty else 0), "Total cobrado hoy")
    with c2:
        render_stat_card("Tickets hoy", len(ventas_hoy), "Ventas registradas")
    with c3:
        render_stat_card("Venta promedio", money(ventas_hoy["Total"].mean() if not ventas_hoy.empty else 0), "Promedio por ticket")
    with c4:
        render_stat_card("Ventas totales", money(ventas["Total"].sum()), "Histórico")

    tab1, tab2 = st.tabs(["Nueva venta", "Historial de ventas"])

    with tab1:
        st.subheader("Registrar venta")

        clientes_lista = st.session_state.clientes["Nombre"].tolist()
        empleados_lista = st.session_state.empleados[
            st.session_state.empleados["Activo"] == True
        ]["Nombre"].tolist()
        servicios_lista = catalogo[catalogo["Activo"] == True]["Servicio"].tolist()

        with st.form("form_venta"):
            v1, v2, v3 = st.columns(3)

            with v1:
                fecha_venta = st.date_input("Fecha", value=date.today(), key="venta_fecha")
                cliente_venta = st.selectbox("Cliente", clientes_lista, key="venta_cliente")
                empleado_venta = st.selectbox("Empleado", empleados_lista, key="venta_empleado")

            with v2:
                servicio_venta = st.selectbox("Servicio", servicios_lista, key="venta_servicio")
                metodo_pago = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Zelle", "Cash App", "Otro"])
                descuento = st.number_input("Descuento", min_value=0.0, value=0.0)

            with v3:
                precio_sugerido = 0.0
                if servicio_venta:
                    match = catalogo[catalogo["Servicio"] == servicio_venta]
                    if not match.empty:
                        precio_sugerido = float(match.iloc[0]["Precio"])

                subtotal = st.number_input("Subtotal", min_value=0.0, value=precio_sugerido)
                total = max(subtotal - descuento, 0)
                st.metric("Total", money(total))

            notas_venta = st.text_area("Notas de venta")
            guardar_venta = st.form_submit_button("Guardar venta")

        if guardar_venta:
            nueva_venta = pd.DataFrame([{
                "Fecha": str(fecha_venta),
                "Cliente": cliente_venta,
                "Servicio": servicio_venta,
                "Empleado": empleado_venta,
                "Metodo pago": metodo_pago,
                "Subtotal": subtotal,
                "Descuento": descuento,
                "Total": total,
                "Notas": notas_venta
            }])

            st.session_state.ventas = pd.concat(
                [st.session_state.ventas, nueva_venta],
                ignore_index=True
            )

            st.success("Venta registrada correctamente.")

    with tab2:
        st.subheader("Historial")
        st.dataframe(st.session_state.ventas, use_container_width=True)


# =========================
# CATÁLOGO
# =========================

elif menu == "Catálogo":
    render_fresha_hero(
        "Catálogo",
        "Servicios, precios, duración y disponibilidad para citas y online booking."
    )

    tab1, tab2 = st.tabs(["Servicios", "Agregar servicio"])

    with tab1:
        catalogo_editado = st.data_editor(
            st.session_state.catalogo,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Guardar cambios del catálogo"):
            st.session_state.catalogo = catalogo_editado
            st.success("Catálogo actualizado.")

    with tab2:
        with st.form("form_servicio_catalogo"):
            c1, c2, c3 = st.columns(3)

            with c1:
                servicio = st.text_input("Nombre del servicio")
                categoria = st.text_input("Categoría", "Manos")

            with c2:
                duracion = st.number_input("Duración min", min_value=5, value=60, step=5)
                precio = st.number_input("Precio", min_value=0.0, value=50.0)

            with c3:
                activo = st.checkbox("Activo", value=True)

            descripcion = st.text_area("Descripción")
            guardar_servicio = st.form_submit_button("Guardar servicio")

        if guardar_servicio and servicio:
            nuevo_servicio = pd.DataFrame([{
                "Servicio": servicio,
                "Categoria": categoria,
                "Duracion min": duracion,
                "Precio": precio,
                "Activo": activo,
                "Descripcion": descripcion
            }])

            st.session_state.catalogo = pd.concat(
                [st.session_state.catalogo, nuevo_servicio],
                ignore_index=True
            )

            st.success("Servicio agregado al catálogo.")


# =========================
# ONLINE BOOKING
# =========================

elif menu == "Online booking":
    render_fresha_hero(
        "Online booking",
        "Simulación de reservas online para clientes. Las solicitudes entran como citas pendientes."
    )

    settings = st.session_state.app_settings

    if not settings.get("online_booking_activo", True):
        st.warning("Online booking está desactivado en Settings.")
    else:
        st.info("Esta vista funciona como una página sencilla para que el cliente solicite una cita. Después podemos separarla como página pública.")

    catalogo = st.session_state.catalogo.copy()
    servicios_activos = catalogo[catalogo["Activo"] == True]

    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    with st.form("form_online_booking"):
        b1, b2, b3 = st.columns(3)

        with b1:
            cliente_nombre = st.text_input("Nombre del cliente")
            cliente_telefono = st.text_input("Teléfono")
            cliente_email = st.text_input("Email")

        with b2:
            servicio_online = st.selectbox("Servicio", servicios_activos["Servicio"].tolist())
            empleado_online = st.selectbox("Profesional preferido", ["Sin preferencia"] + empleados_activos)

        with b3:
            fecha_online = st.date_input("Fecha deseada", value=date.today())
            hora_online = st.time_input("Hora deseada", value=time(10, 0))

        notas_online = st.text_area("Notas / diseño que desea")
        enviar_solicitud = st.form_submit_button("Solicitar cita")

    if enviar_solicitud and cliente_nombre:
        clientes_actuales = st.session_state.clientes.copy()

        if cliente_nombre not in clientes_actuales["Nombre"].tolist():
            nuevo_cliente = pd.DataFrame([{
                "Nombre": cliente_nombre,
                "Telefono": cliente_telefono,
                "Email": cliente_email,
                "Cumpleanos": "",
                "Notas": "Cliente agregado desde online booking"
            }])
            st.session_state.clientes = pd.concat(
                [st.session_state.clientes, nuevo_cliente],
                ignore_index=True
            )

        empleado_final = empleado_online
        if empleado_final == "Sin preferencia":
            empleado_final = empleados_activos[0] if empleados_activos else ""

        precio_servicio = 0.0
        match = servicios_activos[servicios_activos["Servicio"] == servicio_online]
        if not match.empty:
            precio_servicio = float(match.iloc[0]["Precio"])

        nueva_cita = pd.DataFrame([{
            "Fecha": str(fecha_online),
            "Hora": hora_online.strftime("%H:%M"),
            "Cliente": cliente_nombre,
            "Empleado": empleado_final,
            "Servicio": servicio_online,
            "Diseno": notas_online,
            "Materiales": "",
            "Costo materiales": 0.0,
            "Precio": precio_servicio,
            "Estado": "Pendiente",
            "Notas": "Solicitud creada desde online booking"
        }])

        st.session_state.citas = pd.concat(
            [st.session_state.citas, nueva_cita],
            ignore_index=True
        )

        st.success("Solicitud recibida. La cita quedó como Pendiente.")


# =========================
# REPORTES
# =========================

elif menu == "Reportes":
    render_fresha_hero(
        "Reportes",
        "Resumen de desempeño: ventas, citas, clientes, servicios y empleadas."
    )

    citas = st.session_state.citas.copy()
    ventas = st.session_state.ventas.copy()

    citas["Fecha_dt"] = pd.to_datetime(citas["Fecha"], errors="coerce")
    citas["Precio"] = pd.to_numeric(citas["Precio"], errors="coerce").fillna(0)
    ventas["Fecha_dt"] = pd.to_datetime(ventas["Fecha"], errors="coerce")
    ventas["Total"] = pd.to_numeric(ventas["Total"], errors="coerce").fillna(0)

    r1, r2 = st.columns(2)
    with r1:
        desde = st.date_input("Desde", value=date.today().replace(day=1), key="reportes_desde")
    with r2:
        hasta = st.date_input("Hasta", value=date.today(), key="reportes_hasta")

    citas_periodo = citas[
        (citas["Fecha_dt"].dt.date >= desde) &
        (citas["Fecha_dt"].dt.date <= hasta)
    ]

    ventas_periodo = ventas[
        (ventas["Fecha_dt"].dt.date >= desde) &
        (ventas["Fecha_dt"].dt.date <= hasta)
    ]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Ventas", money(ventas_periodo["Total"].sum()), "Periodo seleccionado")
    with c2:
        render_stat_card("Citas", len(citas_periodo), "Periodo seleccionado")
    with c3:
        render_stat_card("Clientes únicos", citas_periodo["Cliente"].nunique() if not citas_periodo.empty else 0, "En citas")
    with c4:
        completadas = len(citas_periodo[citas_periodo["Estado"] == "Completada"]) if not citas_periodo.empty else 0
        render_stat_card("Completadas", completadas, "Citas cerradas")

    tab1, tab2, tab3 = st.tabs(["Por empleada", "Por servicio", "Por estado"])

    with tab1:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep_emp = citas_periodo.groupby("Empleado").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()
            st.dataframe(rep_emp, use_container_width=True)

    with tab2:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep_serv = citas_periodo.groupby("Servicio").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()
            st.dataframe(rep_serv, use_container_width=True)

    with tab3:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep_estado = citas_periodo.groupby("Estado").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()
            st.dataframe(rep_estado, use_container_width=True)


# =========================
# SETTINGS
# =========================

elif menu == "Settings":
    require_admin()

    render_fresha_hero(
        "Settings",
        "Configuración del negocio, usuarios, roles y preferencias de online booking."
    )

    tab1, tab2, tab3 = st.tabs(["Negocio", "Usuarios y roles", "Permisos"])

    with tab1:
        settings = st.session_state.app_settings

        nombre_negocio = st.text_input("Nombre del negocio", value=settings.get("nombre_negocio", "Greta Studio"))
        telefono_negocio = st.text_input("Teléfono del negocio", value=settings.get("telefono_negocio", ""))
        direccion_negocio = st.text_area("Dirección", value=settings.get("direccion_negocio", ""))
        moneda = st.selectbox("Moneda", ["USD", "MXN"], index=0 if settings.get("moneda", "USD") == "USD" else 1)
        online_booking_activo = st.checkbox("Online booking activo", value=settings.get("online_booking_activo", True))
        requiere_confirmacion_online = st.checkbox("Solicitudes online requieren confirmación", value=settings.get("requiere_confirmacion_online", True))

        if st.button("Guardar settings del negocio"):
            st.session_state.app_settings = {
                "nombre_negocio": nombre_negocio,
                "telefono_negocio": telefono_negocio,
                "direccion_negocio": direccion_negocio,
                "moneda": moneda,
                "online_booking_activo": online_booking_activo,
                "requiere_confirmacion_online": requiere_confirmacion_online
            }
            st.success("Settings guardados.")

    with tab2:
        st.subheader("Usuarios")
        usuarios_editados = st.data_editor(
            st.session_state.usuarios,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Guardar usuarios y roles"):
            st.session_state.usuarios = usuarios_editados
            st.success("Usuarios actualizados.")

        st.caption("Por ahora esto simula roles dentro de la app. Después se puede conectar a login real con contraseñas.")

    with tab3:
        st.subheader("Permisos actuales por rol")
        permisos_rows = []
        for rol, menus in ROLE_MENUS.items():
            permisos_rows.append({
                "Rol": rol,
                "Secciones permitidas": ", ".join(menus)
            })
        st.dataframe(pd.DataFrame(permisos_rows), use_container_width=True)

'''

if new_modules.strip() not in text:
    text = text.replace(whatsapp_marker, new_modules + whatsapp_marker)

# -------------------------------------------------
# 6) Export Excel: agregar hojas nuevas si existen
# -------------------------------------------------
text = text.replace(
    'st.session_state.gastos.to_excel(writer, index=False, sheet_name="Gastos")',
    '''st.session_state.gastos.to_excel(writer, index=False, sheet_name="Gastos")
        if "catalogo" in st.session_state:
            st.session_state.catalogo.to_excel(writer, index=False, sheet_name="Catalogo")
        if "ventas" in st.session_state:
            st.session_state.ventas.to_excel(writer, index=False, sheet_name="Ventas")
        if "usuarios" in st.session_state:
            st.session_state.usuarios.to_excel(writer, index=False, sheet_name="Usuarios")'''
)

# -------------------------------------------------
# 7) Import Excel: leer nuevas hojas si existen
# -------------------------------------------------
text = text.replace(
    '''if "Gastos" in xls.sheet_names:
        st.session_state.gastos = pd.read_excel(file, sheet_name="Gastos")''',
    '''if "Gastos" in xls.sheet_names:
        st.session_state.gastos = pd.read_excel(file, sheet_name="Gastos")
    if "Catalogo" in xls.sheet_names:
        st.session_state.catalogo = pd.read_excel(file, sheet_name="Catalogo")
    if "Ventas" in xls.sheet_names:
        st.session_state.ventas = pd.read_excel(file, sheet_name="Ventas")
    if "Usuarios" in xls.sheet_names:
        st.session_state.usuarios = pd.read_excel(file, sheet_name="Usuarios")'''
)

path.write_text(text)
print("✅ Greta app actualizada con Ventas, Catálogo, Online booking, Reportes, Settings y Roles.")
PY