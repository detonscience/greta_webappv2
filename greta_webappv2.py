import streamlit as st
import pandas as pd
from datetime import date, time, timedelta
import calendar
from io import BytesIO
from urllib.parse import quote

st.set_page_config(page_title="Greta Studio App", page_icon="💅", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.3rem; }
.app-title { font-size: 34px; font-weight: 850; color: #7a1f4d; }
.small-muted { color: #777; font-size: 14px; }
.fresha-hero {
    background: linear-gradient(135deg, #ffffff 0%, #fff0f7 100%);
    border: 1px solid #f4c9dd;
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0px 8px 24px rgba(122,31,77,0.08);
}
.fresha-title { font-size: 30px; font-weight: 850; color: #41122a; margin-bottom: 4px; }
.fresha-subtitle { color: #7b6170; font-size: 15px; }
.fresha-stat-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 16px;
    border: 1px solid #f1d6e3;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}
.fresha-stat-label { color: #8b6b7b; font-size: 13px; font-weight: 650; }
.fresha-stat-value { color: #351020; font-size: 25px; font-weight: 850; }
.appointment-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #f1d6e3;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
}
.appointment-time { font-size: 18px; font-weight: 850; color: #341020; }
.appointment-client { font-size: 15px; font-weight: 750; color: #4a2032; }
.appointment-meta { color: #77606b; font-size: 13px; line-height: 1.35; }
.fresha-pill { display: inline-block; padding: 5px 10px; border-radius: 999px; font-size: 12px; font-weight: 750; margin-top: 6px; }
.pill-confirmada { background: #e7f8ee; color: #14783d; }
.pill-pendiente { background: #fff4d6; color: #8a6100; }
.pill-cancelada { background: #ffe3e3; color: #a32626; }
.pill-completada { background: #e7f1ff; color: #2458a8; }
.day-box {
    background: white;
    border-radius: 16px;
    padding: 12px;
    min-height: 230px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.07);
    margin-bottom: 12px;
}
.quick-action-box {
    background: #fffafc;
    border: 1px dashed #e9accb;
    border-radius: 18px;
    padding: 14px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "$0.00"


def render_fresha_hero(title, subtitle):
    st.markdown(f"""
    <div class="fresha-hero">
        <div class="fresha-title">{title}</div>
        <div class="fresha-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label, value, note=""):
    st.markdown(f"""
    <div class="fresha-stat-card">
        <div class="fresha-stat-label">{label}</div>
        <div class="fresha-stat-value">{value}</div>
        <div class="small-muted">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def status_class(status):
    status_clean = str(status).strip().lower()
    if status_clean == "confirmada":
        return "pill-confirmada"
    if status_clean == "cancelada":
        return "pill-cancelada"
    if status_clean == "completada":
        return "pill-completada"
    return "pill-pendiente"


def render_appointment_card(row, compact=False):
    pill_class = status_class(row.get("Estado", "Pendiente"))
    extra = "" if compact else f"<br>Diseño: {row.get('Diseno', '')}<br>Materiales: {row.get('Materiales', '')}"

    st.markdown(f"""
    <div class="appointment-card">
        <div class="appointment-time">{row.get('Hora', '')}</div>
        <div class="appointment-client">{row.get('Cliente', '')}</div>
        <div class="appointment-meta">
            {row.get('Servicio', '')} · {row.get('Empleado', '')}<br>
            Precio: <b>{money(row.get('Precio', 0))}</b>{extra}
        </div>
        <span class="fresha-pill {pill_class}">{row.get('Estado', 'Pendiente')}</span>
    </div>
    """, unsafe_allow_html=True)


def init_data():
    if "clientes" not in st.session_state:
        st.session_state.clientes = pd.DataFrame([
            {
                "Nombre": "Maria Lopez",
                "Telefono": "2105551111",
                "Email": "maria@example.com",
                "Cumpleanos": "1990-05-15",
                "Notas": "Prefiere tonos nude y citas por la mañana."
            },
            {
                "Nombre": "Ana Rivera",
                "Telefono": "2105552222",
                "Email": "ana@example.com",
                "Cumpleanos": "1988-10-02",
                "Notas": "Cliente frecuente, le gusta diseño minimalista."
            },
            {
                "Nombre": "Sofia Garcia",
                "Telefono": "2105553333",
                "Email": "sofia@example.com",
                "Cumpleanos": "1995-02-20",
                "Notas": "Prefiere pedicure los sábados."
            },
        ])

    if "empleados" not in st.session_state:
        st.session_state.empleados = pd.DataFrame([
            {
                "Nombre": "Greta",
                "Puesto": "Admin",
                "Activo": True,
                "Sueldo base": 900.0,
                "Comision %": 20.0
            },
            {
                "Nombre": "Eva",
                "Puesto": "Técnica",
                "Activo": True,
                "Sueldo base": 700.0,
                "Comision %": 25.0
            },
            {
                "Nombre": "Luna",
                "Puesto": "Técnica",
                "Activo": True,
                "Sueldo base": 650.0,
                "Comision %": 25.0
            },
        ])

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
            },
            {
                "Servicio": "Retoque",
                "Categoria": "Manos",
                "Duracion min": 75,
                "Precio": 60.0,
                "Activo": True,
                "Descripcion": "Retoque de acrílico o gel."
            },
        ])

    if "citas" not in st.session_state:
        st.session_state.citas = pd.DataFrame([
            {
                "Fecha": str(date.today()),
                "Hora": "10:00",
                "Cliente": "Maria Lopez",
                "Empleado": "Greta",
                "Servicio": "Manicure gel",
                "Diseno": "French natural",
                "Materiales": "Gel nude, top coat",
                "Costo materiales": 8.0,
                "Precio": 55.0,
                "Estado": "Confirmada",
                "Notas": "Llega 10 min antes."
            },
            {
                "Fecha": str(date.today()),
                "Hora": "13:00",
                "Cliente": "Ana Rivera",
                "Empleado": "Eva",
                "Servicio": "Acrílico",
                "Diseno": "Coffin corto",
                "Materiales": "Acrílico clear, gel rosa",
                "Costo materiales": 12.0,
                "Precio": 75.0,
                "Estado": "Pendiente",
                "Notas": "Confirmar por WhatsApp."
            },
            {
                "Fecha": str(date.today() + timedelta(days=1)),
                "Hora": "11:30",
                "Cliente": "Sofia Garcia",
                "Empleado": "Luna",
                "Servicio": "Pedicure",
                "Diseno": "Rojo clásico",
                "Materiales": "Esmalte rojo",
                "Costo materiales": 6.0,
                "Precio": 50.0,
                "Estado": "Confirmada",
                "Notas": "Cliente regular."
            },
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
            },
        ])

    if "inventario" not in st.session_state:
        st.session_state.inventario = pd.DataFrame([
            {
                "Producto": "Gel nude",
                "Categoria": "Gel",
                "Cantidad": 5,
                "Minimo": 2,
                "Costo unitario": 9.5
            },
            {
                "Producto": "Top coat",
                "Categoria": "Gel",
                "Cantidad": 2,
                "Minimo": 2,
                "Costo unitario": 8.0
            },
            {
                "Producto": "Acrílico clear",
                "Categoria": "Acrílico",
                "Cantidad": 1,
                "Minimo": 2,
                "Costo unitario": 15.0
            },
        ])

    if "gastos" not in st.session_state:
        st.session_state.gastos = pd.DataFrame([
            {
                "Fecha": str(date.today()),
                "Concepto": "Renta",
                "Categoria": "Fijo",
                "Monto": 1200.0,
                "Notas": "Demo"
            },
            {
                "Fecha": str(date.today()),
                "Concepto": "Materiales",
                "Categoria": "Inventario",
                "Monto": 180.0,
                "Notas": "Compra demo"
            },
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
            },
        ])

    if "app_settings" not in st.session_state:
        st.session_state.app_settings = {
            "nombre_negocio": "Greta Studio",
            "telefono_negocio": "",
            "direccion_negocio": "",
            "moneda": "USD",
            "online_booking_activo": True,
            "requiere_confirmacion_online": True,
        }


init_data()

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
    ],
}


def get_allowed_menus(role):
    return ROLE_MENUS.get(role, ROLE_MENUS["Empleada"])


def require_admin():
    if st.session_state.get("current_role", "Admin") != "Admin":
        st.warning("Esta sección es solo para Admin.")
        st.stop()


def get_client_info(nombre):
    clientes = st.session_state.clientes
    match = clientes[clientes["Nombre"] == nombre]
    if match.empty:
        return None
    return match.iloc[0]


def render_whatsapp_buttons(row):
    cliente = get_client_info(row.get("Cliente", ""))
    telefono = "" if cliente is None else str(cliente.get("Telefono", ""))
    telefono_limpio = "".join(ch for ch in telefono if ch.isdigit())

    if not telefono_limpio:
        st.caption("Cliente sin teléfono para WhatsApp.")
        return

    mensajes = {
        "Confirmar": f"Hola {row.get('Cliente', '')}, te confirmamos tu cita el {row.get('Fecha', '')} a las {row.get('Hora', '')} para {row.get('Servicio', '')}. Gracias.",
        "Recordatorio": f"Hola {row.get('Cliente', '')}, te recordamos tu cita el {row.get('Fecha', '')} a las {row.get('Hora', '')}. Te esperamos.",
        "Gracias": f"Hola {row.get('Cliente', '')}, muchas gracias por visitarnos en Greta Studio. Esperamos verte pronto.",
        "Promo": f"Hola {row.get('Cliente', '')}, tenemos una promoción especial para ti en Greta Studio. Escríbenos para más detalles.",
    }

    cols = st.columns(4)
    for i, (label, msg) in enumerate(mensajes.items()):
        cols[i].link_button(
            label,
            f"https://wa.me/{telefono_limpio}?text={quote(msg)}"
        )


def export_excel():
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.clientes.to_excel(writer, index=False, sheet_name="Clientes")
        st.session_state.empleados.to_excel(writer, index=False, sheet_name="Empleados")
        st.session_state.citas.to_excel(writer, index=False, sheet_name="Citas")
        st.session_state.inventario.to_excel(writer, index=False, sheet_name="Inventario")
        st.session_state.gastos.to_excel(writer, index=False, sheet_name="Gastos")
        st.session_state.catalogo.to_excel(writer, index=False, sheet_name="Catalogo")
        st.session_state.ventas.to_excel(writer, index=False, sheet_name="Ventas")
        st.session_state.usuarios.to_excel(writer, index=False, sheet_name="Usuarios")

    return output.getvalue()


def import_excel(file):
    xls = pd.ExcelFile(file)

    sheet_map = {
        "Clientes": "clientes",
        "Empleados": "empleados",
        "Citas": "citas",
        "Inventario": "inventario",
        "Gastos": "gastos",
        "Catalogo": "catalogo",
        "Ventas": "ventas",
        "Usuarios": "usuarios",
    }

    for sheet, key in sheet_map.items():
        if sheet in xls.sheet_names:
            st.session_state[key] = pd.read_excel(file, sheet_name=sheet)


st.markdown(
    '<div class="app-title">💅 Greta Studio App</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="small-muted">Agenda, clientes, WhatsApp, ventas, catálogo, online booking, reportes, nómina y finanzas</div>',
    unsafe_allow_html=True
)
st.divider()

st.sidebar.markdown("### Usuario / Rol")

roles_disponibles = ["Admin", "Recepción", "Empleada"]

current_role = st.sidebar.selectbox(
    "Entrar como",
    roles_disponibles,
    index=0,
    key="current_role_selector"
)

st.session_state.current_role = current_role

st.sidebar.caption(f"Rol activo: {current_role}")

menu = st.sidebar.radio(
    "Menú principal",
    get_allowed_menus(current_role)
)


if menu == "Inicio":
    render_fresha_hero(
        "Inicio del estudio",
        "Vista rápida tipo Fresha: ventas, próximas citas, clientes y accesos rápidos."
    )

    citas = st.session_state.citas.copy()
    ventas = st.session_state.ventas.copy()
    gastos = st.session_state.gastos.copy()
    inventario = st.session_state.inventario.copy()

    ventas["Total"] = pd.to_numeric(ventas["Total"], errors="coerce").fillna(0)
    gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)
    citas["Costo materiales"] = pd.to_numeric(
        citas["Costo materiales"],
        errors="coerce"
    ).fillna(0)
    inventario["Cantidad"] = pd.to_numeric(
        inventario["Cantidad"],
        errors="coerce"
    ).fillna(0)
    inventario["Minimo"] = pd.to_numeric(
        inventario["Minimo"],
        errors="coerce"
    ).fillna(0)

    citas_hoy = citas[citas["Fecha"].astype(str) == str(date.today())]

    ingresos = ventas["Total"].sum()
    gastos_total = gastos["Monto"].sum()
    materiales = citas["Costo materiales"].sum()
    ganancia = ingresos - gastos_total - materiales

    bajos = inventario[inventario["Cantidad"] <= inventario["Minimo"]]

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        render_stat_card("Ventas", money(ingresos), "Total registrado")
    with s2:
        render_stat_card("Citas de hoy", len(citas_hoy), "Servicios agendados")
    with s3:
        render_stat_card("Clientes", len(st.session_state.clientes), "Base de datos")
    with s4:
        render_stat_card("Ganancia estimada", money(ganancia), "Ventas - gastos - materiales")

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown("### Agenda de hoy")

        if citas_hoy.empty:
            st.info("No hay citas para hoy.")
        else:
            for _, row in citas_hoy.sort_values("Hora").iterrows():
                render_appointment_card(row)
                render_whatsapp_buttons(row)

    with right:
        st.markdown("### Acciones rápidas")

        st.markdown("""
        <div class="quick-action-box">
        <b>Flujo recomendado</b><br>
        1. Agrega cliente<br>
        2. Agenda cita<br>
        3. Confirma por WhatsApp<br>
        4. Cobra en Ventas<br>
        5. Revisa Reportes
        </div>
        """, unsafe_allow_html=True)

        if not bajos.empty:
            st.warning("Productos bajos en inventario")
            st.dataframe(bajos, use_container_width=True)
        else:
            st.success("Inventario sin alertas críticas.")


elif menu == "Agenda Fresha":
    render_fresha_hero(
        "Agenda Fresha",
        "Vista diaria con filtros, detalles del cliente y acciones rápidas."
    )

    citas = st.session_state.citas.copy()

    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    top1, top2, top3 = st.columns(3)

    with top1:
        fecha_agenda = st.date_input(
            "Fecha de agenda",
            value=date.today(),
            key="agenda_fecha"
        )
    with top2:
        filtro_empleado = st.selectbox(
            "Profesional",
            ["Todas"] + empleados_activos,
            key="agenda_empleado"
        )
    with top3:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todos", "Confirmada", "Pendiente", "Cancelada", "Completada"],
            key="agenda_estado"
        )

    busqueda = st.text_input("Buscar cliente, servicio o notas", key="agenda_busqueda")

    citas_dia = citas[citas["Fecha"].astype(str) == str(fecha_agenda)]

    if filtro_empleado != "Todas":
        citas_dia = citas_dia[citas_dia["Empleado"] == filtro_empleado]

    if filtro_estado != "Todos":
        citas_dia = citas_dia[citas_dia["Estado"] == filtro_estado]

    if busqueda:
        citas_dia = citas_dia[
            citas_dia.apply(
                lambda r: busqueda.lower() in " ".join([str(v) for v in r.values]).lower(),
                axis=1
            )
        ]

    k1, k2, k3 = st.columns(3)

    with k1:
        render_stat_card("Citas", len(citas_dia), "Resultado actual")
    with k2:
        total_est = pd.to_numeric(
            citas_dia.get("Precio", 0),
            errors="coerce"
        ).fillna(0).sum()
        render_stat_card("Ventas estimadas", money(total_est), "Según filtros")
    with k3:
        clientes_unicos = citas_dia["Cliente"].nunique() if not citas_dia.empty else 0
        render_stat_card("Clientes únicos", clientes_unicos, "En vista")

    agenda_col, detalle_col = st.columns([1.4, 1])

    with agenda_col:
        st.markdown("### Timeline del día")

        if citas_dia.empty:
            st.info("No hay citas con esos filtros.")
        else:
            for _, row in citas_dia.sort_values("Hora").iterrows():
                render_appointment_card(row)

                with st.expander(f"Abrir cita: {row['Cliente']} · {row['Hora']}"):
                    cliente_info = get_client_info(row["Cliente"])

                    if cliente_info is not None:
                        st.write(f"**Teléfono:** {cliente_info.get('Telefono', '')}")
                        st.write(f"**Email:** {cliente_info.get('Email', '')}")
                        st.write(f"**Perfil:** {cliente_info.get('Notas', '')}")

                    st.write(f"**Servicio:** {row['Servicio']}")
                    st.write(f"**Diseño:** {row['Diseno']}")
                    st.write(f"**Materiales:** {row['Materiales']}")
                    st.write(f"**Precio:** {money(row['Precio'])}")
                    st.write(f"**Estado:** {row['Estado']}")
                    st.write(f"**Notas:** {row['Notas']}")

                    render_whatsapp_buttons(row)

    with detalle_col:
        st.markdown("### Vista por profesional")

        for emp in empleados_activos:
            emp_citas = citas_dia[citas_dia["Empleado"] == emp]

            with st.expander(f"{emp} · {len(emp_citas)} citas", expanded=True):
                if emp_citas.empty:
                    st.caption("Sin citas")
                else:
                    for _, row in emp_citas.sort_values("Hora").iterrows():
                        render_appointment_card(row, compact=True)


elif menu == "Calendario":
    render_fresha_hero(
        "Calendario",
        "Vista flexible de citas por año, mes, semana o día."
    )

    citas = st.session_state.citas.copy()
    citas["Fecha_dt"] = pd.to_datetime(citas["Fecha"], errors="coerce")
    citas = citas.dropna(subset=["Fecha_dt"])

    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    vista = st.radio(
        "Vista del calendario",
        ["Día", "Semana", "Mes", "Año"],
        horizontal=True,
        key="calendario_tipo_vista"
    )

    filtro_empleado = st.selectbox(
        "Filtrar por empleada",
        ["Todas"] + empleados_activos,
        key="calendario_filtro_empleado"
    )

    if filtro_empleado != "Todas":
        citas = citas[citas["Empleado"] == filtro_empleado]

    if vista == "Día":
        fecha_dia = st.date_input(
            "Selecciona día",
            value=date.today(),
            key="cal_dia"
        )

        citas_dia = citas[citas["Fecha_dt"].dt.date == fecha_dia]

        render_stat_card(
            "Citas del día",
            len(citas_dia),
            fecha_dia.strftime("%d/%m/%Y")
        )

        if citas_dia.empty:
            st.info("No hay citas para este día.")
        else:
            for _, row in citas_dia.sort_values("Hora").iterrows():
                render_appointment_card(row)

    elif vista == "Semana":
        fecha_base = st.date_input(
            "Semana de",
            value=date.today(),
            key="cal_semana"
        )

        inicio_semana = fecha_base - timedelta(days=fecha_base.weekday())
        dias = [inicio_semana + timedelta(days=i) for i in range(7)]
        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        cols = st.columns(7)

        for i, dia in enumerate(dias):
            with cols[i]:
                st.markdown(
                    f'<div class="day-box"><b>{dias_es[i]}</b><br>{dia.strftime("%d/%m/%Y")}<hr>',
                    unsafe_allow_html=True
                )

                citas_dia = citas[citas["Fecha_dt"].dt.date == dia]

                if citas_dia.empty:
                    st.caption("Sin citas")
                else:
                    for _, row in citas_dia.sort_values("Hora").iterrows():
                        render_appointment_card(row, compact=True)

                st.markdown("</div>", unsafe_allow_html=True)

    elif vista == "Mes":
        hoy = date.today()

        meses_nombre = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        col_mes, col_anio = st.columns(2)

        with col_mes:
            mes = st.selectbox(
                "Mes",
                list(range(1, 13)),
                index=hoy.month - 1,
                format_func=lambda x: meses_nombre[x - 1],
                key="cal_mes"
            )

        with col_anio:
            anio = st.number_input(
                "Año",
                min_value=2020,
                max_value=2035,
                value=hoy.year,
                step=1,
                key="cal_anio_mes"
            )

        citas_mes = citas[
            (citas["Fecha_dt"].dt.month == mes) &
            (citas["Fecha_dt"].dt.year == int(anio))
        ]

        render_stat_card("Citas del mes", len(citas_mes), "Total mensual")

        cal = calendar.Calendar(firstweekday=0)
        semanas = cal.monthdatescalendar(int(anio), int(mes))

        for semana in semanas:
            cols = st.columns(7)

            for _, dia in enumerate(semana):
                with cols[_]:
                    opacity = "0.35" if dia.month != mes else "1"
                    citas_dia = citas_mes[citas_mes["Fecha_dt"].dt.date == dia]

                    st.markdown(
                        f'<div class="day-box" style="opacity:{opacity};"><b>{dia.day}</b><br><span class="small-muted">{len(citas_dia)} citas</span><hr>',
                        unsafe_allow_html=True
                    )

                    for _, row in citas_dia.sort_values("Hora").head(3).iterrows():
                        render_appointment_card(row, compact=True)

                    st.markdown("</div>", unsafe_allow_html=True)

    else:
        anio = st.number_input(
            "Selecciona año",
            min_value=2020,
            max_value=2035,
            value=date.today().year,
            step=1,
            key="cal_anio"
        )

        citas_anio = citas[citas["Fecha_dt"].dt.year == int(anio)]

        meses_nombre = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        rows = []

        for m in range(1, 13):
            citas_m = citas_anio[citas_anio["Fecha_dt"].dt.month == m]

            rows.append({
                "Mes": meses_nombre[m - 1],
                "Citas": len(citas_m),
                "Clientes únicos": citas_m["Cliente"].nunique() if not citas_m.empty else 0,
                "Ventas estimadas": pd.to_numeric(
                    citas_m.get("Precio", 0),
                    errors="coerce"
                ).fillna(0).sum()
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)


elif menu == "Nueva cita":
    render_fresha_hero(
        "Nueva cita",
        "Agenda una cita nueva y déjala lista para confirmar por WhatsApp."
    )

    clientes_lista = st.session_state.clientes["Nombre"].tolist()

    empleados_lista = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    catalogo = st.session_state.catalogo.copy()
    servicios_lista = catalogo[catalogo["Activo"] == True]["Servicio"].tolist()

    with st.form("form_nueva_cita"):
        c1, c2, c3 = st.columns(3)

        with c1:
            fecha_cita = st.date_input("Fecha", value=date.today())
            hora_cita = st.time_input("Hora", value=time(10, 0))
            cliente_cita = st.selectbox("Cliente", clientes_lista)

        with c2:
            empleado_cita = st.selectbox("Empleado", empleados_lista)
            servicio_cita = st.selectbox("Servicio", servicios_lista)
            estado_cita = st.selectbox(
                "Estado",
                ["Pendiente", "Confirmada", "Completada", "Cancelada"]
            )

        with c3:
            match = catalogo[catalogo["Servicio"] == servicio_cita]
            precio_sugerido = float(match.iloc[0]["Precio"]) if not match.empty else 0.0
            precio = st.number_input("Precio", min_value=0.0, value=precio_sugerido)
            costo_materiales = st.number_input("Costo materiales", min_value=0.0, value=0.0)

        diseno = st.text_input("Diseño / tipo de trabajo")
        materiales = st.text_input("Materiales a usar")
        notas = st.text_area("Notas")

        guardar = st.form_submit_button("Guardar cita")

    if guardar:
        nueva = pd.DataFrame([{
            "Fecha": str(fecha_cita),
            "Hora": hora_cita.strftime("%H:%M"),
            "Cliente": cliente_cita,
            "Empleado": empleado_cita,
            "Servicio": servicio_cita,
            "Diseno": diseno,
            "Materiales": materiales,
            "Costo materiales": costo_materiales,
            "Precio": precio,
            "Estado": estado_cita,
            "Notas": notas
        }])

        st.session_state.citas = pd.concat(
            [st.session_state.citas, nueva],
            ignore_index=True
        )

        st.success("Cita guardada correctamente.")


elif menu == "Ventas":
    render_fresha_hero(
        "Ventas",
        "Registra pagos, revisa ventas del día y conecta cada venta con una cita o servicio."
    )

    ventas = st.session_state.ventas.copy()
    ventas["Total"] = pd.to_numeric(ventas["Total"], errors="coerce").fillna(0)
    ventas["Fecha_dt"] = pd.to_datetime(ventas["Fecha"], errors="coerce")

    ventas_hoy = ventas[ventas["Fecha_dt"].dt.date == date.today()]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_stat_card("Ventas hoy", money(ventas_hoy["Total"].sum()), "Total cobrado hoy")
    with c2:
        render_stat_card("Tickets hoy", len(ventas_hoy), "Ventas registradas")
    with c3:
        promedio = ventas_hoy["Total"].mean() if not ventas_hoy.empty else 0
        render_stat_card("Venta promedio", money(promedio), "Promedio por ticket")
    with c4:
        render_stat_card("Ventas totales", money(ventas["Total"].sum()), "Histórico")

    tab1, tab2 = st.tabs(["Nueva venta", "Historial de ventas"])

    with tab1:
        catalogo = st.session_state.catalogo.copy()
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
                metodo_pago = st.selectbox(
                    "Método de pago",
                    ["Efectivo", "Tarjeta", "Zelle", "Cash App", "Otro"]
                )
                descuento = st.number_input("Descuento", min_value=0.0, value=0.0)

            with v3:
                match = catalogo[catalogo["Servicio"] == servicio_venta]
                precio_sugerido = float(match.iloc[0]["Precio"]) if not match.empty else 0.0
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
        st.dataframe(st.session_state.ventas, use_container_width=True)


elif menu == "Lista de clientes":
    render_fresha_hero(
        "Lista de clientes",
        "Base de datos de clientes, cumpleaños, notas y contacto."
    )

    tab1, tab2 = st.tabs(["Clientes", "Agregar cliente"])

    with tab1:
        editado = st.data_editor(
            st.session_state.clientes,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Guardar cambios de clientes"):
            st.session_state.clientes = editado
            st.success("Clientes actualizados.")

    with tab2:
        with st.form("form_cliente"):
            nombre = st.text_input("Nombre")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            cumple = st.text_input("Cumpleaños", placeholder="YYYY-MM-DD")
            notas = st.text_area("Notas / perfil del cliente")
            guardar_cliente = st.form_submit_button("Guardar cliente")

        if guardar_cliente and nombre:
            nuevo = pd.DataFrame([{
                "Nombre": nombre,
                "Telefono": telefono,
                "Email": email,
                "Cumpleanos": cumple,
                "Notas": notas
            }])

            st.session_state.clientes = pd.concat(
                [st.session_state.clientes, nuevo],
                ignore_index=True
            )

            st.success("Cliente agregado.")


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


elif menu == "Online booking":
    render_fresha_hero(
        "Online booking",
        "Simulación de reservas online para clientes. Las solicitudes entran como citas pendientes."
    )

    settings = st.session_state.app_settings

    if not settings.get("online_booking_activo", True):
        st.warning("Online booking está desactivado en Settings.")

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
            empleado_online = st.selectbox(
                "Profesional preferido",
                ["Sin preferencia"] + empleados_activos
            )

        with b3:
            fecha_online = st.date_input("Fecha deseada", value=date.today())
            hora_online = st.time_input("Hora deseada", value=time(10, 0))

        notas_online = st.text_area("Notas / diseño que desea")
        enviar_solicitud = st.form_submit_button("Solicitar cita")

    if enviar_solicitud and cliente_nombre:
        if cliente_nombre not in st.session_state.clientes["Nombre"].tolist():
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

        empleado_final = (
            empleados_activos[0]
            if empleado_online == "Sin preferencia" and empleados_activos
            else empleado_online
        )

        match = servicios_activos[servicios_activos["Servicio"] == servicio_online]
        precio_servicio = float(match.iloc[0]["Precio"]) if not match.empty else 0.0

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
        desde = st.date_input(
            "Desde",
            value=date.today().replace(day=1),
            key="reportes_desde"
        )

    with r2:
        hasta = st.date_input(
            "Hasta",
            value=date.today(),
            key="reportes_hasta"
        )

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
        clientes_unicos = citas_periodo["Cliente"].nunique() if not citas_periodo.empty else 0
        render_stat_card("Clientes únicos", clientes_unicos, "En citas")
    with c4:
        completadas = len(citas_periodo[citas_periodo["Estado"] == "Completada"])
        render_stat_card("Completadas", completadas, "Citas cerradas")

    tab1, tab2, tab3 = st.tabs(["Por empleada", "Por servicio", "Por estado"])

    with tab1:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep = citas_periodo.groupby("Empleado").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()

            st.dataframe(rep, use_container_width=True)

    with tab2:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep = citas_periodo.groupby("Servicio").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()

            st.dataframe(rep, use_container_width=True)

    with tab3:
        if citas_periodo.empty:
            st.info("No hay citas en este periodo.")
        else:
            rep = citas_periodo.groupby("Estado").agg(
                Citas=("Cliente", "count"),
                Ingresos_estimados=("Precio", "sum")
            ).reset_index()

            st.dataframe(rep, use_container_width=True)


elif menu == "WhatsApp":
    render_fresha_hero(
        "WhatsApp",
        "Envía confirmaciones, recordatorios, mensajes de gracias y promociones."
    )

    citas = st.session_state.citas.copy()

    if citas.empty:
        st.info("No hay citas.")
    else:
        opciones = citas.apply(
            lambda r: f"{r['Fecha']} {r['Hora']} - {r['Cliente']} ({r['Servicio']})",
            axis=1
        ).tolist()

        seleccion = st.selectbox("Selecciona cita", opciones)

        row = citas.iloc[opciones.index(seleccion)]

        render_appointment_card(row)
        render_whatsapp_buttons(row)


elif menu == "Empleados":
    require_admin()

    render_fresha_hero(
        "Empleados",
        "Administra técnicas, puestos, sueldos, comisiones y estado activo."
    )

    editado = st.data_editor(
        st.session_state.empleados,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("Guardar empleados"):
        st.session_state.empleados = editado
        st.success("Empleados actualizados.")


elif menu == "Nómina":
    require_admin()

    render_fresha_hero(
        "Nómina",
        "Calcula sueldo base, comisiones y pago estimado por empleada."
    )

    citas = st.session_state.citas.copy()
    empleados = st.session_state.empleados.copy()

    citas["Precio"] = pd.to_numeric(citas["Precio"], errors="coerce").fillna(0)

    desde = st.date_input(
        "Desde",
        value=date.today().replace(day=1),
        key="nomina_desde"
    )

    hasta = st.date_input(
        "Hasta",
        value=date.today(),
        key="nomina_hasta"
    )

    citas["Fecha_dt"] = pd.to_datetime(citas["Fecha"], errors="coerce")

    citas_p = citas[
        (citas["Fecha_dt"].dt.date >= desde) &
        (citas["Fecha_dt"].dt.date <= hasta)
    ]

    rows = []

    for _, emp in empleados.iterrows():
        ventas_emp = citas_p[citas_p["Empleado"] == emp["Nombre"]]["Precio"].sum()
        comision = ventas_emp * (float(emp.get("Comision %", 0)) / 100)
        sueldo = float(emp.get("Sueldo base", 0))

        rows.append({
            "Empleado": emp["Nombre"],
            "Sueldo base": sueldo,
            "Ventas": ventas_emp,
            "Comisión": comision,
            "Pago estimado": sueldo + comision
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)


elif menu == "Inventario":
    require_admin()

    render_fresha_hero(
        "Inventario",
        "Control de materiales, costos y alertas de bajo inventario."
    )

    inv = st.session_state.inventario.copy()

    inv["Cantidad"] = pd.to_numeric(inv["Cantidad"], errors="coerce").fillna(0)
    inv["Minimo"] = pd.to_numeric(inv["Minimo"], errors="coerce").fillna(0)

    bajos = inv[inv["Cantidad"] <= inv["Minimo"]]

    if not bajos.empty:
        st.warning("Hay productos bajos en inventario.")
        st.dataframe(bajos, use_container_width=True)

    editado = st.data_editor(
        st.session_state.inventario,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("Guardar inventario"):
        st.session_state.inventario = editado
        st.success("Inventario actualizado.")


elif menu == "Finanzas":
    require_admin()

    render_fresha_hero(
        "Finanzas",
        "Ingresos, gastos, costos de materiales y ganancia estimada."
    )

    ventas = st.session_state.ventas.copy()
    gastos = st.session_state.gastos.copy()
    citas = st.session_state.citas.copy()

    ventas["Total"] = pd.to_numeric(ventas["Total"], errors="coerce").fillna(0)
    gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)
    citas["Costo materiales"] = pd.to_numeric(
        citas["Costo materiales"],
        errors="coerce"
    ).fillna(0)

    ingresos = ventas["Total"].sum()
    gastos_total = gastos["Monto"].sum()
    materiales = citas["Costo materiales"].sum()
    ganancia = ingresos - gastos_total - materiales

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_stat_card("Ingresos", money(ingresos), "Ventas")
    with c2:
        render_stat_card("Gastos", money(gastos_total), "Gastos registrados")
    with c3:
        render_stat_card("Materiales", money(materiales), "Costo en citas")
    with c4:
        render_stat_card("Ganancia", money(ganancia), "Estimada")

    st.subheader("Gastos")

    editado = st.data_editor(
        st.session_state.gastos,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("Guardar gastos"):
        st.session_state.gastos = editado
        st.success("Gastos actualizados.")


elif menu == "Settings":
    require_admin()

    render_fresha_hero(
        "Settings",
        "Configuración del negocio, usuarios, roles y online booking."
    )

    tab1, tab2, tab3 = st.tabs(["Negocio", "Usuarios y roles", "Permisos"])

    with tab1:
        settings = st.session_state.app_settings

        nombre_negocio = st.text_input(
            "Nombre del negocio",
            value=settings.get("nombre_negocio", "Greta Studio")
        )

        telefono_negocio = st.text_input(
            "Teléfono del negocio",
            value=settings.get("telefono_negocio", "")
        )

        direccion_negocio = st.text_area(
            "Dirección",
            value=settings.get("direccion_negocio", "")
        )

        moneda = st.selectbox(
            "Moneda",
            ["USD", "MXN"],
            index=0 if settings.get("moneda", "USD") == "USD" else 1
        )

        online_booking_activo = st.checkbox(
            "Online booking activo",
            value=settings.get("online_booking_activo", True)
        )

        requiere_confirmacion_online = st.checkbox(
            "Solicitudes online requieren confirmación",
            value=settings.get("requiere_confirmacion_online", True)
        )

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
        usuarios_editados = st.data_editor(
            st.session_state.usuarios,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Guardar usuarios y roles"):
            st.session_state.usuarios = usuarios_editados
            st.success("Usuarios actualizados.")

        st.caption("Por ahora esto simula roles. Después podemos agregar login real con contraseña.")

    with tab3:
        permisos_rows = [
            {
                "Rol": rol,
                "Secciones permitidas": ", ".join(menus)
            }
            for rol, menus in ROLE_MENUS.items()
        ]

        st.dataframe(pd.DataFrame(permisos_rows), use_container_width=True)


elif menu == "Excel / Backup":
    require_admin()

    render_fresha_hero(
        "Excel / Backup",
        "Exporta o importa la información de la app."
    )

    st.download_button(
        "Descargar backup Excel",
        data=export_excel(),
        file_name="greta_studio_backup.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded = st.file_uploader("Importar backup Excel", type=["xlsx"])

    if uploaded is not None:
        if st.button("Importar archivo"):
            import_excel(uploaded)
            st.success("Datos importados correctamente.")