import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from io import BytesIO
from urllib.parse import quote
import re

st.set_page_config(
    page_title="Greta Studio App",
    page_icon="💅",
    layout="wide"
)

# =========================
# ESTILOS
# =========================

st.markdown("""
<style>
.main {
    background-color: #fff7fb;
}
.block-container {
    padding-top: 1.5rem;
}
.metric-card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.08);
    border-left: 6px solid #d94f91;
}
.app-title {
    font-size: 34px;
    font-weight: 800;
    color: #7a1f4d;
}
.small-muted {
    color: #777;
    font-size: 14px;
}
.gretta-card {
    background-color: #ffe1ef;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
    border-left: 5px solid #d94f91;
}
.eva-card {
    background-color: #e7f1ff;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
    border-left: 5px solid #3f7fd9;
}
.day-box {
    background: white;
    border-radius: 16px;
    padding: 12px;
    min-height: 230px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.07);
}
.fresha-hero {
    background: linear-gradient(135deg, #ffffff 0%, #fff0f7 100%);
    border: 1px solid #f4c9dd;
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0px 8px 24px rgba(122,31,77,0.08);
}
.fresha-title {
    font-size: 30px;
    font-weight: 850;
    color: #41122a;
    margin-bottom: 4px;
}
.fresha-subtitle {
    color: #7b6170;
    font-size: 15px;
}
.fresha-stat-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 16px;
    border: 1px solid #f1d6e3;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.05);
}
.fresha-stat-label {
    color: #8b6b7b;
    font-size: 13px;
    font-weight: 650;
}
.fresha-stat-value {
    color: #351020;
    font-size: 25px;
    font-weight: 850;
}
.fresha-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 750;
    margin-top: 6px;
}
.pill-confirmada { background: #e7f8ee; color: #14783d; }
.pill-pendiente { background: #fff4d6; color: #8a6100; }
.pill-cancelada { background: #ffe3e3; color: #a32626; }
.pill-completada { background: #e7f1ff; color: #2458a8; }
.appointment-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #f1d6e3;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
}
.appointment-time {
    font-size: 18px;
    font-weight: 850;
    color: #341020;
}
.appointment-client {
    font-size: 15px;
    font-weight: 750;
    color: #4a2032;
}
.appointment-meta {
    color: #77606b;
    font-size: 13px;
    line-height: 1.35;
}
.timeline-row {
    display: grid;
    grid-template-columns: 72px 1fr;
    gap: 12px;
    align-items: start;
    margin-bottom: 12px;
}
.timeline-hour {
    color: #7a1f4d;
    font-weight: 850;
    padding-top: 12px;
}
.quick-action-box {
    background: #fffafc;
    border: 1px dashed #e9accb;
    border-radius: 18px;
    padding: 14px;
    margin-top: 10px;
}
.section-chip {
    display: inline-block;
    background: #f7dce9;
    color: #7a1f4d;
    padding: 6px 11px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# DATOS INICIALES
# =========================

def init_data():
    if "clientes" not in st.session_state:
        st.session_state.clientes = pd.DataFrame([
            {
                "Nombre": "Maria Lopez",
                "Telefono": "555-111-2222",
                "Email": "maria@email.com",
                "Cumpleanos": "1990-05-12",
                "Notas": "Prefiere diseños naturales"
            },
            {
                "Nombre": "Ana Torres",
                "Telefono": "555-333-4444",
                "Email": "ana@email.com",
                "Cumpleanos": "1988-09-21",
                "Notas": "Le gusta el color rojo"
            }
        ])

    if "empleados" not in st.session_state:
        st.session_state.empleados = pd.DataFrame([
            {
                "Nombre": "Greta",
                "Puesto": "Dueña",
                "Activo": True,
                "Tipo pago": "Dueña",
                "Sueldo base": 0.0,
                "Comision %": 0.0
            },
            {
                "Nombre": "Eva",
                "Puesto": "Empleada",
                "Activo": True,
                "Tipo pago": "Sueldo + comisión",
                "Sueldo base": 600.0,
                "Comision %": 20.0
            }
        ])

    if "citas" not in st.session_state:
        hoy = date.today()
        st.session_state.citas = pd.DataFrame([
            {
                "Fecha": str(hoy),
                "Hora": "10:00",
                "Cliente": "Maria Lopez",
                "Empleado": "Greta",
                "Servicio": "Manicure gel",
                "Diseno": "French sencillo",
                "Materiales": "Gel base, top coat, blanco",
                "Costo materiales": 8.0,
                "Precio": 55.0,
                "Estado": "Confirmada",
                "Notas": "Cliente frecuente"
            },
            {
                "Fecha": str(hoy),
                "Hora": "12:30",
                "Cliente": "Ana Torres",
                "Empleado": "Eva",
                "Servicio": "Acrílico",
                "Diseno": "Rojo con glitter",
                "Materiales": "Acrílico, tips, glitter",
                "Costo materiales": 12.0,
                "Precio": 75.0,
                "Estado": "Confirmada",
                "Notas": "Primera vez"
            }
        ])

    if "inventario" not in st.session_state:
        st.session_state.inventario = pd.DataFrame([
            {
                "Producto": "Gel base",
                "Categoria": "Gel",
                "Cantidad": 10,
                "Minimo": 3,
                "Costo unidad": 7.5,
                "Barcode": "GEL001"
            },
            {
                "Producto": "Top coat",
                "Categoria": "Gel",
                "Cantidad": 2,
                "Minimo": 3,
                "Costo unidad": 8.0,
                "Barcode": "GEL002"
            }
        ])

    if "gastos" not in st.session_state:
        st.session_state.gastos = pd.DataFrame([
            {
                "Fecha": str(date.today()),
                "Concepto": "Materiales",
                "Categoria": "Inventario",
                "Monto": 120.0,
                "Notas": "Compra inicial"
            }
        ])


init_data()


# =========================
# FUNCIONES
# =========================

def money(x):
    try:
        return f"${float(x):,.2f}"
    except:
        return "$0.00"


# ========== Fresha UI helpers ==========

def status_class(status):
    status_clean = str(status).strip().lower()
    mapping = {
        "confirmada": "pill-confirmada",
        "pendiente": "pill-pendiente",
        "cancelada": "pill-cancelada",
        "completada": "pill-completada"
    }
    return mapping.get(status_clean, "pill-pendiente")


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


def render_appointment_card(row, compact=False):
    pill_class = status_class(row.get("Estado", "Pendiente"))
    diseno = row.get("Diseno", "")
    materiales = row.get("Materiales", "")
    extra = "" if compact else f"<br>Diseño: {diseno}<br>Materiales: {materiales}"
    st.markdown(f"""
    <div class="appointment-card">
        <div class="appointment-time">{row['Hora']}</div>
        <div class="appointment-client">{row['Cliente']}</div>
        <div class="appointment-meta">
            {row['Servicio']} · {row['Empleado']}<br>
            Precio: <b>{money(row['Precio'])}</b>{extra}
        </div>
        <span class="fresha-pill {pill_class}">{row.get('Estado', 'Pendiente')}</span>
    </div>
    """, unsafe_allow_html=True)



def get_employee_class(nombre):
    if nombre == "Greta":
        return "gretta-card"
    if nombre == "Eva":
        return "eva-card"
    return "gretta-card"


def clean_phone_for_whatsapp(phone):
    """Limpia el teléfono para usarlo con WhatsApp.
    Si tiene 10 dígitos, asume número de Estados Unidos y agrega 1.
    """
    digits = re.sub(r"\D", "", str(phone))

    if len(digits) == 10:
        digits = "1" + digits

    return digits


def get_client_info(client_name):
    clientes = st.session_state.clientes.copy()
    cliente_info = clientes[clientes["Nombre"] == client_name]

    if cliente_info.empty:
        return None

    return cliente_info.iloc[0]


def build_whatsapp_url(phone, message):
    clean_phone = clean_phone_for_whatsapp(phone)
    encoded_message = quote(message)
    return f"https://wa.me/{clean_phone}?text={encoded_message}"


def whatsapp_template(tipo, cliente="", fecha="", hora="", empleado="", servicio="", descuento=""):
    templates = {
        "Confirmación cálida": (
            f"Hola {cliente}, te escribimos de Greta Studio para confirmar tu cita "
            f"del {fecha} a las {hora} con {empleado} para {servicio}. "
            f"¿Nos confirmas por favor? 💅"
        ),
        "Confirmación breve": (
            f"Hola {cliente}, solo queremos confirmar tu cita en Greta Studio: "
            f"{fecha} a las {hora}. Servicio: {servicio}. ¿Confirmas?"
        ),
        "Recordatorio cálido": (
            f"Hola {cliente}, te recordamos tu cita en Greta Studio el {fecha} "
            f"a las {hora} con {empleado}. Servicio: {servicio}. ¡Te esperamos! 💗"
        ),
        "Recordatorio con política": (
            f"Hola {cliente}, te recordamos tu cita en Greta Studio el {fecha} a las {hora}. "
            f"Si necesitas cambiarla, avísanos con tiempo por favor. ¡Gracias!"
        ),
        "Gracias después de cita": (
            f"Hola {cliente}, muchas gracias por visitar Greta Studio. "
            f"Esperamos que te haya encantado tu servicio de {servicio}. "
            f"Será un gusto verte de nuevo 💗"
        ),
        "Pedir reseña": (
            f"Hola {cliente}, gracias por visitarnos en Greta Studio. "
            f"Si te gustó tu servicio de {servicio}, nos ayudaría mucho que nos recomendaras "
            f"o nos dejaras una reseña. ¡Gracias por tu apoyo! 💅"
        ),
        "Promo general": (
            f"Hola {cliente}, tenemos una promoción especial en Greta Studio. "
            f"Esta semana puedes aprovechar {descuento or 'un descuento especial'} en servicios seleccionados. "
            f"¿Te gustaría agendar?"
        ),
        "Cumpleaños": (
            f"¡Feliz cumpleaños, {cliente}! 🎉 De parte de Greta Studio queremos consentirte con "
            f"{descuento or 'un descuento especial'} en tu próxima visita. "
            f"Cuando gustes, te ayudamos a agendar 💗"
        ),
        "Reactivar cliente": (
            f"Hola {cliente}, hace tiempo que no te vemos por Greta Studio. "
            f"Nos encantaría atenderte otra vez. Tenemos espacios disponibles esta semana, "
            f"¿quieres que te ayudemos a agendar?"
        )
    }
    return templates.get(tipo, "")


def render_whatsapp_buttons(row, custom_messages=None):
    cliente = get_client_info(row["Cliente"])

    if cliente is None:
        st.caption("No se encontró teléfono del cliente para WhatsApp.")
        return

    telefono = cliente.get("Telefono", "")
    clean_phone = clean_phone_for_whatsapp(telefono)

    if not clean_phone:
        st.caption("Este cliente no tiene teléfono registrado.")
        return

    default_messages = {
        "confirmacion": whatsapp_template(
            "Confirmación cálida",
            cliente=row["Cliente"],
            fecha=row["Fecha"],
            hora=row["Hora"],
            empleado=row["Empleado"],
            servicio=row["Servicio"]
        ),
        "recordatorio": whatsapp_template(
            "Recordatorio cálido",
            cliente=row["Cliente"],
            fecha=row["Fecha"],
            hora=row["Hora"],
            empleado=row["Empleado"],
            servicio=row["Servicio"]
        ),
        "gracias": whatsapp_template(
            "Gracias después de cita",
            cliente=row["Cliente"],
            fecha=row["Fecha"],
            hora=row["Hora"],
            empleado=row["Empleado"],
            servicio=row["Servicio"]
        )
    }

    if custom_messages:
        default_messages.update(custom_messages)

    confirm_url = build_whatsapp_url(telefono, default_messages["confirmacion"])
    reminder_url = build_whatsapp_url(telefono, default_messages["recordatorio"])
    thanks_url = build_whatsapp_url(telefono, default_messages["gracias"])

    w1, w2, w3 = st.columns(3)
    w1.link_button("✅ Confirmar", confirm_url)
    w2.link_button("⏰ Recordar", reminder_url)
    w3.link_button("💗 Gracias", thanks_url)


def export_excel():
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.clientes.to_excel(writer, index=False, sheet_name="Clientes")
        st.session_state.empleados.to_excel(writer, index=False, sheet_name="Empleados")
        st.session_state.citas.to_excel(writer, index=False, sheet_name="Citas")
        st.session_state.inventario.to_excel(writer, index=False, sheet_name="Inventario")
        st.session_state.gastos.to_excel(writer, index=False, sheet_name="Gastos")
    return output.getvalue()


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


# =========================
# HEADER
# =========================

st.markdown('<div class="app-title">💅 Greta Studio App</div>', unsafe_allow_html=True)
st.markdown('<div class="small-muted">Agenda, clientes, WhatsApp, inventario, empleados, nómina y finanzas en un solo lugar</div>', unsafe_allow_html=True)
st.divider()


# =========================
# SIDEBAR
# =========================

menu = st.sidebar.radio(
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


# =========================
# INICIO Y AGENDA FRESHA
# =========================

if menu == "Inicio":
    render_fresha_hero(
        "Inicio del estudio",
        "Vista rápida tipo Fresha: ventas, próximas citas, clientes y accesos rápidos."
    )

    citas = st.session_state.citas.copy()
    gastos = st.session_state.gastos.copy()
    clientes = st.session_state.clientes.copy()
    inventario = st.session_state.inventario.copy()

    citas["Precio"] = pd.to_numeric(citas["Precio"], errors="coerce").fillna(0)
    citas["Costo materiales"] = pd.to_numeric(citas["Costo materiales"], errors="coerce").fillna(0)
    gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)
    inventario["Cantidad"] = pd.to_numeric(inventario["Cantidad"], errors="coerce").fillna(0)
    inventario["Minimo"] = pd.to_numeric(inventario["Minimo"], errors="coerce").fillna(0)

    hoy = str(date.today())
    citas_hoy = citas[citas["Fecha"].astype(str) == hoy]
    ingresos = citas["Precio"].sum()
    materiales = citas["Costo materiales"].sum()
    gastos_total = gastos["Monto"].sum()
    ganancia = ingresos - materiales - gastos_total
    bajos = inventario[inventario["Cantidad"] <= inventario["Minimo"]]

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        render_stat_card("Ventas totales", money(ingresos), "Ingresos de citas registradas")
    with s2:
        render_stat_card("Citas de hoy", len(citas_hoy), "Servicios agendados hoy")
    with s3:
        render_stat_card("Clientes", len(clientes), "Base de datos actual")
    with s4:
        render_stat_card("Ganancia estimada", money(ganancia), "Después de materiales y gastos")

    st.markdown("### Agenda de hoy")

    if citas_hoy.empty:
        st.info("No hay citas para hoy.")
    else:
        for _, row in citas_hoy.sort_values("Hora").iterrows():
            render_appointment_card(row)
            render_whatsapp_buttons(row)

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### Resumen por empleada")
        if citas.empty:
            st.info("No hay citas registradas.")
        else:
            resumen = citas.groupby("Empleado").agg(
                Citas=("Cliente", "count"),
                Ingresos=("Precio", "sum"),
                Materiales=("Costo materiales", "sum")
            ).reset_index()
            resumen["Ganancia antes de nómina"] = resumen["Ingresos"] - resumen["Materiales"]
            st.dataframe(resumen, use_container_width=True)

    with right:
        st.markdown("### Acciones rápidas")
        st.markdown("""
        <div class="quick-action-box">
            <b>Flujo recomendado</b><br>
            1. Agrega cliente<br>
            2. Agenda cita<br>
            3. Confirma por WhatsApp<br>
            4. Marca como completada<br>
            5. Revisa finanzas y nómina
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
        "Vista de agenda diaria con timeline, detalles del cliente y acciones rápidas."
    )

    citas = st.session_state.citas.copy()
    clientes = st.session_state.clientes.copy()

    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    top1, top2, top3 = st.columns([1, 1, 1])
    with top1:
        fecha_agenda = st.date_input("Fecha de agenda", value=date.today(), key="agenda_fresha_fecha")
    with top2:
        filtro_empleado = st.selectbox("Profesional", ["Todas"] + empleados_activos, key="agenda_fresha_empleado")
    with top3:
        filtro_estado = st.selectbox("Estado", ["Todos", "Confirmada", "Pendiente", "Cancelada", "Completada"], key="agenda_fresha_estado")

    busqueda = st.text_input("Buscar cliente, servicio o notas", key="agenda_fresha_busqueda")

    citas_dia = citas[citas["Fecha"].astype(str) == str(fecha_agenda)]

    if filtro_empleado != "Todas":
        citas_dia = citas_dia[citas_dia["Empleado"] == filtro_empleado]

    if filtro_estado != "Todos":
        citas_dia = citas_dia[citas_dia["Estado"] == filtro_estado]

    if busqueda:
        mask = citas_dia.apply(
            lambda r: busqueda.lower() in " ".join([str(v) for v in r.values]).lower(),
            axis=1
        )
        citas_dia = citas_dia[mask]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_stat_card("Citas filtradas", len(citas_dia), "Resultado actual")
    with k2:
        render_stat_card("Ventas del día", money(pd.to_numeric(citas_dia.get("Precio", 0), errors="coerce").fillna(0).sum()), "Según filtros")
    with k3:
        render_stat_card("Materiales", money(pd.to_numeric(citas_dia.get("Costo materiales", 0), errors="coerce").fillna(0).sum()), "Costo estimado")
    with k4:
        render_stat_card("Clientes únicos", citas_dia["Cliente"].nunique() if not citas_dia.empty else 0, "En esta vista")

    agenda_col, detalle_col = st.columns([1.35, 1])

    with agenda_col:
        st.markdown("### Timeline del día")

        if citas_dia.empty:
            st.info("No hay citas con esos filtros.")
        else:
            for idx, row in citas_dia.sort_values("Hora").iterrows():
                st.markdown('<div class="timeline-row">', unsafe_allow_html=True)
                st.markdown(f'<div class="timeline-hour">{row["Hora"]}</div>', unsafe_allow_html=True)
                render_appointment_card(row)
                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander(f"Abrir cita: {row['Cliente']} · {row['Hora']}"):
                    cliente_info = clientes[clientes["Nombre"] == row["Cliente"]]

                    if not cliente_info.empty:
                        cli = cliente_info.iloc[0]
                        st.write(f"**Teléfono:** {cli['Telefono']}")
                        st.write(f"**Email:** {cli['Email']}")
                        st.write(f"**Perfil cliente:** {cli['Notas']}")

                    st.write(f"**Servicio:** {row['Servicio']}")
                    st.write(f"**Diseño / tipo de trabajo:** {row['Diseno']}")
                    st.write(f"**Materiales:** {row['Materiales']}")
                    st.write(f"**Costo materiales:** {money(row['Costo materiales'])}")
                    st.write(f"**Precio:** {money(row['Precio'])}")
                    st.write(f"**Estado:** {row['Estado']}")
                    st.write(f"**Notas:** {row['Notas']}")
                    st.divider()
                    render_whatsapp_buttons(row)

    with detalle_col:
        st.markdown("### Panel rápido")

        if citas_dia.empty:
            st.info("Selecciona otra fecha o filtro para ver detalles.")
        else:
            opciones = citas_dia.sort_values("Hora").apply(
                lambda r: f"{r['Hora']} - {r['Cliente']} ({r['Servicio']})",
                axis=1
            ).tolist()
            seleccion = st.selectbox("Selecciona cita", opciones, key="agenda_fresha_detalle")
            selected_row = citas_dia.sort_values("Hora").iloc[opciones.index(seleccion)]

            st.markdown('<span class="section-chip">Detalle de cita</span>', unsafe_allow_html=True)
            render_appointment_card(selected_row)

            cliente_info = get_client_info(selected_row["Cliente"])
            if cliente_info is not None:
                st.write(f"**Teléfono:** {cliente_info.get('Telefono', '')}")
                st.write(f"**Email:** {cliente_info.get('Email', '')}")
                st.write(f"**Perfil:** {cliente_info.get('Notas', '')}")

            st.write(f"**Notas de cita:** {selected_row['Notas']}")
            st.write(f"**Materiales:** {selected_row['Materiales']}")
            st.write(f"**Diseño:** {selected_row['Diseno']}")
            st.divider()
            render_whatsapp_buttons(selected_row)


# =========================
# CALENDARIO
# =========================

elif menu == "Calendario":
    st.header("Calendario de citas")

    citas = st.session_state.citas.copy()

    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    filtro_empleado = st.selectbox(
        "Filtrar por empleada",
        ["Todas"] + empleados_activos
    )

    fecha_base = st.date_input("Semana de", value=date.today())

    inicio_semana = fecha_base - timedelta(days=fecha_base.weekday())
    dias = [inicio_semana + timedelta(days=i) for i in range(7)]

    if filtro_empleado != "Todas":
        citas = citas[citas["Empleado"] == filtro_empleado]

    cols = st.columns(7)

    for i, dia in enumerate(dias):
        with cols[i]:
            st.markdown(f"""
            <div class="day-box">
            <b>{dia.strftime('%A')}</b><br>
            {dia.strftime('%d/%m/%Y')}
            <hr>
            """, unsafe_allow_html=True)

            citas_dia = citas[citas["Fecha"].astype(str) == str(dia)]

            if citas_dia.empty:
                st.caption("Sin citas")
            else:
                for idx, row in citas_dia.sort_values("Hora").iterrows():
                    render_appointment_card(row, compact=True)

                    with st.expander(f"Ver detalles - {row['Cliente']} {row['Hora']}"):
                        cliente_info = st.session_state.clientes[
                            st.session_state.clientes["Nombre"] == row["Cliente"]
                        ]

                        if not cliente_info.empty:
                            cli = cliente_info.iloc[0]
                            st.write(f"**Teléfono:** {cli['Telefono']}")
                            st.write(f"**Email:** {cli['Email']}")
                            st.write(f"**Perfil cliente:** {cli['Notas']}")

                        st.write(f"**Diseño:** {row['Diseno']}")
                        st.write(f"**Materiales:** {row['Materiales']}")
                        st.write(f"**Costo materiales:** {money(row['Costo materiales'])}")
                        st.write(f"**Estado:** {row['Estado']}")
                        st.write(f"**Notas cita:** {row['Notas']}")
                        st.divider()
                        st.write("**WhatsApp del cliente**")
                        render_whatsapp_buttons(row)

            st.markdown("</div>", unsafe_allow_html=True)


# =========================
# NUEVA CITA
# =========================

elif menu == "Nueva cita":
    st.header("Agregar nueva cita")

    clientes = st.session_state.clientes["Nombre"].tolist()
    empleados_activos = st.session_state.empleados[
        st.session_state.empleados["Activo"] == True
    ]["Nombre"].tolist()

    with st.form("form_cita"):
        c1, c2, c3 = st.columns(3)

        with c1:
            fecha = st.date_input("Fecha", value=date.today())
            hora = st.time_input("Hora", value=time(10, 0))
            cliente = st.selectbox("Cliente", clientes)

        with c2:
            empleado = st.selectbox("Empleado / Técnica", empleados_activos)
            servicio = st.text_input("Servicio", "Manicure gel")
            estado = st.selectbox("Estado", ["Confirmada", "Pendiente", "Cancelada", "Completada"])

        with c3:
            precio = st.number_input("Precio", min_value=0.0, value=55.0)
            costo_materiales = st.number_input("Costo materiales", min_value=0.0, value=8.0)

        diseno = st.text_input("Diseño / tipo de trabajo")
        materiales = st.text_area("Materiales a usar")
        notas = st.text_area("Notas")

        guardar = st.form_submit_button("Guardar cita")

    if guardar:
        nueva = pd.DataFrame([{
            "Fecha": str(fecha),
            "Hora": hora.strftime("%H:%M"),
            "Cliente": cliente,
            "Empleado": empleado,
            "Servicio": servicio,
            "Diseno": diseno,
            "Materiales": materiales,
            "Costo materiales": costo_materiales,
            "Precio": precio,
            "Estado": estado,
            "Notas": notas
        }])

        st.session_state.citas = pd.concat(
            [st.session_state.citas, nueva],
            ignore_index=True
        )

        st.success("Cita guardada correctamente.")


# =========================
# CLIENTES
# =========================

elif menu == "Clientes":
    st.header("Clientes")

    with st.expander("Agregar cliente"):
        with st.form("form_cliente"):
            nombre = st.text_input("Nombre")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            cumple = st.date_input("Cumpleaños", value=date(1990, 1, 1))
            notas = st.text_area("Notas / perfil del cliente")

            guardar = st.form_submit_button("Guardar cliente")

        if guardar and nombre:
            nuevo = pd.DataFrame([{
                "Nombre": nombre,
                "Telefono": telefono,
                "Email": email,
                "Cumpleanos": str(cumple),
                "Notas": notas
            }])
            st.session_state.clientes = pd.concat(
                [st.session_state.clientes, nuevo],
                ignore_index=True
            )
            st.success("Cliente agregado.")

    st.dataframe(st.session_state.clientes, use_container_width=True)

    st.subheader("WhatsApp rápido a cliente")

    clientes_lista = st.session_state.clientes["Nombre"].tolist()

    if clientes_lista:
        cliente_wa = st.selectbox("Cliente", clientes_lista, key="cliente_whatsapp_select")
        cliente_info = get_client_info(cliente_wa)

        if cliente_info is not None:
            telefono = cliente_info.get("Telefono", "")
            mensaje = st.text_area(
                "Mensaje",
                value=f"Hola {cliente_wa}, te escribimos de Greta Studio. ¿Cómo estás?",
                key="mensaje_whatsapp_cliente"
            )
            whatsapp_url = build_whatsapp_url(telefono, mensaje)
            st.link_button("📲 Abrir WhatsApp", whatsapp_url)
    else:
        st.info("Agrega clientes para usar WhatsApp rápido.")



# =========================
# WHATSAPP
# =========================

elif menu == "WhatsApp":
    st.header("WhatsApp")
    st.info("Esta versión abre WhatsApp con mensajes prellenados. No envía mensajes automáticamente, así evitamos costos y configuración complicada por ahora.")

    citas = st.session_state.citas.copy()
    clientes = st.session_state.clientes.copy()

    tab1, tab2, tab3 = st.tabs(["Mensajes por cita", "Mensaje libre", "Promos y cumpleaños"])

    with tab1:
        st.subheader("Enviar mensaje relacionado con una cita")

        if citas.empty:
            st.info("No hay citas registradas.")
        else:
            citas["Etiqueta"] = citas.apply(
                lambda r: f"{r['Fecha']} {r['Hora']} - {r['Cliente']} con {r['Empleado']} ({r['Servicio']})",
                axis=1
            )
            etiqueta = st.selectbox("Selecciona una cita", citas["Etiqueta"].tolist())
            row = citas[citas["Etiqueta"] == etiqueta].iloc[0]

            cliente_info = get_client_info(row["Cliente"])

            if cliente_info is None:
                st.warning("No se encontró el cliente de esta cita.")
            else:
                st.write(f"**Cliente:** {row['Cliente']}")
                st.write(f"**Teléfono:** {cliente_info.get('Telefono', '')}")
                st.write(f"**Cita:** {row['Fecha']} a las {row['Hora']} con {row['Empleado']}")
                st.write(f"**Servicio:** {row['Servicio']}")

                st.markdown("### Templates de mensajes")
                st.caption("Escoge un template, edítalo si quieres y luego abre WhatsApp.")

                plantilla_confirmacion = st.selectbox(
                    "Template para confirmación",
                    ["Confirmación cálida", "Confirmación breve"],
                    key="wa_template_confirmacion"
                )
                msg_confirmacion = st.text_area(
                    "Mensaje de confirmación",
                    value=whatsapp_template(
                        plantilla_confirmacion,
                        cliente=row["Cliente"],
                        fecha=row["Fecha"],
                        hora=row["Hora"],
                        empleado=row["Empleado"],
                        servicio=row["Servicio"]
                    ),
                    height=110,
                    key=f"wa_msg_confirmacion_{etiqueta}_{plantilla_confirmacion}"
                )

                plantilla_recordatorio = st.selectbox(
                    "Template para recordatorio",
                    ["Recordatorio cálido", "Recordatorio con política"],
                    key="wa_template_recordatorio"
                )
                msg_recordatorio = st.text_area(
                    "Mensaje de recordatorio",
                    value=whatsapp_template(
                        plantilla_recordatorio,
                        cliente=row["Cliente"],
                        fecha=row["Fecha"],
                        hora=row["Hora"],
                        empleado=row["Empleado"],
                        servicio=row["Servicio"]
                    ),
                    height=110,
                    key=f"wa_msg_recordatorio_{etiqueta}_{plantilla_recordatorio}"
                )

                plantilla_gracias = st.selectbox(
                    "Template para agradecimiento",
                    ["Gracias después de cita", "Pedir reseña"],
                    key="wa_template_gracias"
                )
                msg_gracias = st.text_area(
                    "Mensaje de agradecimiento",
                    value=whatsapp_template(
                        plantilla_gracias,
                        cliente=row["Cliente"],
                        fecha=row["Fecha"],
                        hora=row["Hora"],
                        empleado=row["Empleado"],
                        servicio=row["Servicio"]
                    ),
                    height=110,
                    key=f"wa_msg_gracias_{etiqueta}_{plantilla_gracias}"
                )

                render_whatsapp_buttons(row, custom_messages={
                    "confirmacion": msg_confirmacion,
                    "recordatorio": msg_recordatorio,
                    "gracias": msg_gracias
                })

    with tab2:
        st.subheader("Mensaje libre a cliente")

        clientes_lista = clientes["Nombre"].tolist()

        if not clientes_lista:
            st.info("No hay clientes registrados.")
        else:
            cliente_nombre = st.selectbox("Cliente", clientes_lista, key="whatsapp_mensaje_libre_cliente")
            cliente_info = get_client_info(cliente_nombre)

            if cliente_info is not None:
                telefono = cliente_info.get("Telefono", "")
                mensaje = st.text_area(
                    "Mensaje personalizado",
                    value=f"Hola {cliente_nombre}, te escribimos de Greta Studio.",
                    height=140
                )

                st.write(f"**Teléfono:** {telefono}")
                st.link_button("📲 Abrir WhatsApp con este mensaje", build_whatsapp_url(telefono, mensaje))


    with tab3:
        st.subheader("Promos, descuentos y cumpleaños")
        st.caption("Usa esta sección para mandar promociones generales, descuentos de cumpleaños o reactivar clientes.")

        clientes_lista = clientes["Nombre"].tolist()

        if not clientes_lista:
            st.info("No hay clientes registrados.")
        else:
            cliente_promo = st.selectbox("Cliente", clientes_lista, key="whatsapp_promo_cliente")
            cliente_info = get_client_info(cliente_promo)

            tipo_promo = st.selectbox(
                "Tipo de mensaje",
                ["Promo general", "Cumpleaños", "Reactivar cliente"],
                key="whatsapp_tipo_promo"
            )

            descuento = st.text_input(
                "Descuento o promoción",
                value="15% de descuento",
                key="whatsapp_descuento_promo"
            )

            mensaje_promo = st.text_area(
                "Mensaje promocional",
                value=whatsapp_template(
                    tipo_promo,
                    cliente=cliente_promo,
                    descuento=descuento
                ),
                height=150,
                key=f"wa_msg_promo_{cliente_promo}_{tipo_promo}_{descuento}"
            )

            if cliente_info is not None:
                telefono = cliente_info.get("Telefono", "")
                cumple = cliente_info.get("Cumpleanos", "")
                st.write(f"**Teléfono:** {telefono}")
                st.write(f"**Cumpleaños registrado:** {cumple}")
                st.link_button("📲 Abrir WhatsApp con promo", build_whatsapp_url(telefono, mensaje_promo))

            st.divider()
            st.subheader("Clientes con cumpleaños este mes")

            clientes_cumple = clientes.copy()
            clientes_cumple["Cumpleanos_dt"] = pd.to_datetime(clientes_cumple["Cumpleanos"], errors="coerce")
            clientes_cumple = clientes_cumple[clientes_cumple["Cumpleanos_dt"].dt.month == date.today().month]

            if clientes_cumple.empty:
                st.info("No hay cumpleaños registrados para este mes.")
            else:
                st.dataframe(
                    clientes_cumple.drop(columns=["Cumpleanos_dt"]),
                    use_container_width=True
                )

# =========================
# EMPLEADOS
# =========================

elif menu == "Empleados":
    st.header("Empleados")

    st.info("Sección de administración. Aquí se manejan Greta, Eva y futuras técnicas.")

    with st.expander("Agregar empleada"):
        with st.form("form_empleado"):
            nombre = st.text_input("Nombre empleada")
            puesto = st.text_input("Puesto", "Técnica")
            activo = st.checkbox("Activo", value=True)
            tipo_pago = st.selectbox("Tipo de pago", ["Sueldo", "Comisión", "Sueldo + comisión", "Dueña"])
            sueldo = st.number_input("Sueldo base", min_value=0.0, value=0.0)
            comision = st.number_input("Comisión %", min_value=0.0, max_value=100.0, value=20.0)

            guardar = st.form_submit_button("Guardar empleada")

        if guardar and nombre:
            nuevo = pd.DataFrame([{
                "Nombre": nombre,
                "Puesto": puesto,
                "Activo": activo,
                "Tipo pago": tipo_pago,
                "Sueldo base": sueldo,
                "Comision %": comision
            }])
            st.session_state.empleados = pd.concat(
                [st.session_state.empleados, nuevo],
                ignore_index=True
            )
            st.success("Empleada agregada.")

    edited = st.data_editor(
        st.session_state.empleados,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("Guardar cambios de empleados"):
        st.session_state.empleados = edited
        st.success("Cambios guardados.")


# =========================
# NÓMINA
# =========================

elif menu == "Nómina":
    st.header("Nómina y comisiones")

    citas = st.session_state.citas.copy()
    empleados = st.session_state.empleados.copy()

    citas["Precio"] = pd.to_numeric(citas["Precio"], errors="coerce").fillna(0)
    citas["Costo materiales"] = pd.to_numeric(citas["Costo materiales"], errors="coerce").fillna(0)

    fecha_inicio = st.date_input("Desde", value=date.today().replace(day=1))
    fecha_fin = st.date_input("Hasta", value=date.today())

    citas["Fecha_dt"] = pd.to_datetime(citas["Fecha"], errors="coerce")
    citas_periodo = citas[
        (citas["Fecha_dt"].dt.date >= fecha_inicio) &
        (citas["Fecha_dt"].dt.date <= fecha_fin)
    ]

    rows = []

    for _, emp in empleados.iterrows():
        nombre = emp["Nombre"]
        citas_emp = citas_periodo[citas_periodo["Empleado"] == nombre]

        ingresos = citas_emp["Precio"].sum()
        materiales = citas_emp["Costo materiales"].sum()
        comision_pct = float(emp["Comision %"])
        sueldo_base = float(emp["Sueldo base"])

        comision_monto = ingresos * (comision_pct / 100)
        total_pago = sueldo_base + comision_monto

        rows.append({
            "Empleado": nombre,
            "Puesto": emp["Puesto"],
            "Tipo pago": emp["Tipo pago"],
            "Citas": len(citas_emp),
            "Ingresos generados": ingresos,
            "Costo materiales": materiales,
            "Sueldo base": sueldo_base,
            "Comisión %": comision_pct,
            "Comisión $": comision_monto,
            "Total a pagar": total_pago
        })

    nomina = pd.DataFrame(rows)

    st.dataframe(nomina, use_container_width=True)

    st.subheader("Detalle de citas del periodo")
    st.dataframe(citas_periodo.drop(columns=["Fecha_dt"]), use_container_width=True)


# =========================
# INVENTARIO
# =========================

elif menu == "Inventario":
    st.header("Inventario")

    with st.expander("Agregar producto"):
        with st.form("form_producto"):
            producto = st.text_input("Producto")
            categoria = st.text_input("Categoría")
            cantidad = st.number_input("Cantidad", min_value=0, value=1)
            minimo = st.number_input("Mínimo antes de alerta", min_value=0, value=3)
            costo = st.number_input("Costo unidad", min_value=0.0, value=0.0)
            barcode = st.text_input("Barcode / código")

            guardar = st.form_submit_button("Guardar producto")

        if guardar and producto:
            nuevo = pd.DataFrame([{
                "Producto": producto,
                "Categoria": categoria,
                "Cantidad": cantidad,
                "Minimo": minimo,
                "Costo unidad": costo,
                "Barcode": barcode
            }])
            st.session_state.inventario = pd.concat(
                [st.session_state.inventario, nuevo],
                ignore_index=True
            )
            st.success("Producto agregado.")

    inventario = st.session_state.inventario.copy()
    inventario["Cantidad"] = pd.to_numeric(inventario["Cantidad"], errors="coerce").fillna(0)
    inventario["Minimo"] = pd.to_numeric(inventario["Minimo"], errors="coerce").fillna(0)

    bajos = inventario[inventario["Cantidad"] <= inventario["Minimo"]]

    if not bajos.empty:
        st.warning("Hay productos bajos en inventario.")
        st.dataframe(bajos, use_container_width=True)

    edited = st.data_editor(
        inventario,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("Guardar cambios de inventario"):
        st.session_state.inventario = edited
        st.success("Inventario actualizado.")


# =========================
# FINANZAS
# =========================

elif menu == "Finanzas":
    st.header("Finanzas")

    citas = st.session_state.citas.copy()
    gastos = st.session_state.gastos.copy()

    citas["Precio"] = pd.to_numeric(citas["Precio"], errors="coerce").fillna(0)
    citas["Costo materiales"] = pd.to_numeric(citas["Costo materiales"], errors="coerce").fillna(0)
    gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)

    ingresos = citas["Precio"].sum()
    costo_materiales = citas["Costo materiales"].sum()
    gastos_total = gastos["Monto"].sum()
    ganancia = ingresos - costo_materiales - gastos_total

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos citas", money(ingresos))
    c2.metric("Materiales usados", money(costo_materiales))
    c3.metric("Gastos registrados", money(gastos_total))
    c4.metric("Ganancia estimada", money(ganancia))

    st.subheader("Registrar gasto")

    with st.form("form_gasto"):
        fecha = st.date_input("Fecha gasto", value=date.today())
        concepto = st.text_input("Concepto")
        categoria = st.text_input("Categoría")
        monto = st.number_input("Monto", min_value=0.0, value=0.0)
        notas = st.text_area("Notas")

        guardar = st.form_submit_button("Guardar gasto")

    if guardar and concepto:
        nuevo = pd.DataFrame([{
            "Fecha": str(fecha),
            "Concepto": concepto,
            "Categoria": categoria,
            "Monto": monto,
            "Notas": notas
        }])
        st.session_state.gastos = pd.concat(
            [st.session_state.gastos, nuevo],
            ignore_index=True
        )
        st.success("Gasto guardado.")

    st.subheader("Gastos")
    st.dataframe(st.session_state.gastos, use_container_width=True)


# =========================
# EXCEL / BACKUP
# =========================

elif menu == "Excel / Backup":
    st.header("Excel / Backup")

    st.subheader("Exportar información")

    excel_data = export_excel()

    st.download_button(
        label="Descargar backup Excel",
        data=excel_data,
        file_name="greta_studio_backup.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("Importar Excel")

    archivo = st.file_uploader("Subir archivo Excel de backup", type=["xlsx"])

    if archivo is not None:
        if st.button("Importar archivo"):
            try:
                import_excel(archivo)
                st.success("Información importada correctamente.")
            except Exception as e:
                st.error(f"No se pudo importar el archivo: {e}")

    st.divider()

    st.subheader("Datos actuales")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Clientes", "Empleados", "Citas", "Inventario", "Gastos"]
    )

    with tab1:
        st.dataframe(st.session_state.clientes, use_container_width=True)
    with tab2:
        st.dataframe(st.session_state.empleados, use_container_width=True)
    with tab3:
        st.dataframe(st.session_state.citas, use_container_width=True)
    with tab4:
        st.dataframe(st.session_state.inventario, use_container_width=True)
    with tab5:
        st.dataframe(st.session_state.gastos, use_container_width=True)