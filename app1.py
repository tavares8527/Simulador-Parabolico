import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Tiro Libre PRO", layout="wide")

st.title("🏟️ Simulador de Tiro Libre Avanzado")
st.write("Modifica los parámetros físicos y ambientales en la barra lateral y presiona **▶️ Lanzar Tiro Libre**.")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("⚙️ Parámetros de Lanzamiento")
v0 = st.sidebar.number_input("Velocidad inicial (m/s)", min_value=1.0, value=25.0, step=1.0)
angle_deg = st.sidebar.number_input("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=35.0, step=1.0)
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("🌤️ Condiciones Ambientales")

# Control de Viento
viento_fuerza = st.sidebar.slider("Fuerza del Viento (m/s)", min_value=-20.0, max_value=20.0, value=0.0, step=1.0)
st.sidebar.caption("Valores negativos = Viento en contra | Valores positivos = Viento a favor")

# Control de Lluvia
lluvia = st.sidebar.selectbox("Intensidad de la Lluvia", ["Ninguna (Despejado)", "Lluvia Ligera", "Tormenta Fuerte"])

# --- CONFIGURACIÓN FÍSICA DEL BALÓN ---
# Masa y radio típicos de un balón de fútbol (FIFA)
masa = 0.430  # kg
radio = 0.11  # m
area_transversal = np.pi * (radio ** 2)

# Densidad del aire según el clima
if lluvia == "Ninguna (Despejado)":
    rho_aire = 1.225  # kg/m³ (Estándar)
    c_arrastre = 0.47  # Coeficiente de arrastre de una esfera
elif lluvia == "Lluvia Ligera":
    rho_aire = 1.250  # El aire húmedo/gotas aumentan ligeramente la resistencia
    c_arrastre = 0.52  
else: # Tormenta Fuerte
    rho_aire = 1.300  
    c_arrastre = 0.65  # Mayor resistencia por el impacto constante de las gotas

# --- SIMULACIÓN FÍSICA EN TIEMPO REAL (Método de Euler) ---
angle_rad = np.radians(angle_deg)

# Vectores iniciales
x_pos, y_pos = [0.0], [0.0]
vx_actual = v0 * np.cos(angle_rad)
vy_actual = v0 * np.sin(angle_rad)

vx_hist, vy_hist = [vx_actual], [vy_actual]
t_hist = [0.0]

dt = 0.02  # Paso de tiempo pequeño para la precisión
t_actual = 0.0

# Ejecutar simulación hasta que toque el suelo (o llegue a un límite de seguridad)
while t_actual < 10.0:
    # Velocidad relativa del balón respecto al viento
    v_rel_x = vx_actual - viento_fuerza
    v_rel_y = vy_actual  # Asumimos viento puramente horizontal
    v_rel_magnitud = np.sqrt(v_rel_x**2 + v_rel_y**2)
    
    # Fuerza de Arrastre (F = 0.5 * rho * A * Cd * v^2)
    f_arrastre = 0.5 * rho_aire * area_transversal * c_arrastre * (v_rel_magnitud ** 2)
    
    # Descomposición de la fuerza de arrastre
    if v_rel_magnitud > 0:
        f_arrastre_x = -f_arrastre * (v_rel_x / v_rel_magnitud)
        f_arrastre_y = -f_arrastre * (v_rel_y / v_rel_magnitud)
    else:
        f_arrastre_x, f_arrastre_y = 0.0, 0.0
        
    # Aceleraciones (F = m * a  ->  a = F / m)
    ax = f_arrastre_x / masa
    ay = -g + (f_arrastre_y / masa)
    
    # Actualizar velocidades
    vx_actual += ax * dt
    vy_actual += ay * dt
    
    # Actualizar posiciones
    nuevo_x = x_pos[-1] + vx_actual * dt
    nuevo_y = y_pos[-1] + vy_actual * dt
    
    if nuevo_y < 0 and t_actual > 0:
        # Intersección matemática exacta con el suelo para el último punto
        fraccion = -y_pos[-1] / (nuevo_y - y_pos[-1]) if (nuevo_y - y_pos[-1]) != 0 else 0
        x_pos.append(x_pos[-1] + (nuevo_x - x_pos[-1]) * fraccion)
        y_pos.append(0.0)
        vx_hist.append(vx_actual)
        vy_hist.append(vy_actual)
        t_hist.append(t_actual + dt * fraccion)
        break
        
    x_pos.append(nuevo_x)
    y_pos.append(nuevo_y)
    vx_hist.append(vx_actual)
    vy_hist.append(vy_actual)
    t_actual += dt
    t_hist.append(t_actual)

# Conversión a arrays de numpy para facilidad de cálculo
x = np.array(x_pos)
y = np.array(y_pos)
t = np.array(t_hist)

h_max = np.max(y)
x_max = x[-1]
t_vuelo = t[-1]

# Reducir la cantidad de frames para que la animación fluya en Streamlit
max_frames = 40
indices = np.linspace(0, len(t) - 1, num=max_frames, dtype=int)
x_anim = x[indices]
y_anim = y[indices]
t_anim = t[indices]

# --- MEDIDOR DE POSICIÓN POR TIEMPO ---
st.sidebar.markdown("---")
st.sidebar.header("📏 Medir Posición por Tiempo")
t_target = st.sidebar.number_input(
    "Tiempo de vuelo objetivo (s)", 
    min_value=0.0, 
    max_value=float(t_vuelo), 
    value=float(t_vuelo / 2), 
    step=0.1
)

# Encontrar el valor más cercano en la simulación
idx_target = (np.abs(t - t_target)).argmin()
st.sidebar.success(f"""
**Datos en el segundo t = {t[idx_target]:.2f} s:**
* 📏 **Distancia en X:** {x[idx_target]:.2f} m
* 📍 **Altura (Y):** {y[idx_target]:.2f} m
""")

# --- GRÁFICO ANIMADO ---
IMAGEN_URL = "https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=2000&auto=format&fit=crop"

fig = go.Figure(
    data=[
        go.Scatter(x=[x_anim[0]], y=[y_anim[0]], mode="lines", name="Rastro", line=dict(dash="dash", color="#FFD700", width=3)),
        go.Scatter(x=[x_anim[0]], y=[y_anim[0]], mode="text", text="⚽", textfont=dict(size=30), name="Balón")
    ]
)

frames = []
for i in range(len(t_anim)):
    frames.append(go.Frame(data=[
        go.Scatter(x=x_anim[:i+1], y=y_anim[:i+1], mode="lines", line=dict(dash="dash", color="#FFD700", width=3)), 
        go.Scatter(x=[x_anim[i]], y=[y_anim[i]], mode="text", text="⚽", textfont=dict(size=30))
    ], name=str(i)))

fig.frames = frames

fig.add_annotation(x=0, y=0, text="🧍‍♂️", showarrow=False, font=dict(size=50), xanchor="right", yanchor="bottom")
fig.add_annotation(x=x_max, y=0, text="💥", showarrow=False, font=dict(size=45), yanchor="bottom")

margen_x = 5
margen_y = 3

fig.update_layout(
    xaxis=dict(range=[-2, x_max + margen_x], title="Distancia (m)", color="white"),
    yaxis=dict(range=[0, h_max + margen_y], title="Altura (m)", color="white"),
    images=[dict(
        source=IMAGEN_URL,
        xref="x", yref="y", 
        x=-2, y=h_max + margen_y, 
        sizex=x_max + margen_x + 2, sizey=h_max + margen_y, 
        sizing="stretch", opacity=0.85, layer="below"
    )],
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(
            label="<span style='color: #00FF00;'>▶️ Lanzar Tiro Libre</span>",
            method="animate",
            args=[None, {"frame": {"duration": 35, "redraw": False}, "fromcurrent": False, "transition": {"duration": 0}}]
        )]
    )],
    showlegend=False,
    height=600,
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)'
)

# --- PANEL DE METRICAS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tiempo de vuelo total", f"{t_vuelo:.2f} s")
col2.metric("Altura máxima", f"{h_max:.2f} m")
col3.metric("Alcance final (X)", f"{x_max:.2f} m")
v_final = np.sqrt(vx_hist[-1]**2 + vy_hist[-1]**2)
col4.metric("Velocidad de impacto", f"{v_final:.2f} m/s")

st.plotly_chart(fig, use_container_width=True)

# --- ANÁLISIS METEOROLÓGICO ---
st.markdown("### 🌦️ Reporte del Efecto Climático en el Balón")
col_info1, col_info2 = st.columns(2)

with col_info1:
    if viento_fuerza < 0:
        st.error(f"💨 **Viento en Contra de {abs(viento_fuerza)} m/s:** El balón experimenta mayor resistencia horizontal, reduciendo drásticamente el alcance final.")
    elif viento_fuerza > 0:
        st.success(f"💨 **Viento a Favor de {viento_fuerza} m/s:** El aire empuja el balón ayudándole a viajar más lejos.")
    else:
        st.info("💨 **Sin Viento:** El desplazamiento horizontal depende puramente de la inercia inicial.")

with col_info2:
    if lluvia == "Lluvia Ligera":
        st.warning("🌧️ **Lluvia Ligera:** Las gotas aumentan la densidad del entorno, frenando sutilmente la velocidad tanto vertical como horizontal.")
    elif lluvia == "Tormenta Fuerte":
        st.error("⛈️ **Tormenta Fuerte:** El coeficiente de arrastre aumenta debido al impacto severo del agua. El balón perderá energía rápidamente y caerá antes.")
    else:
        st.success("☀️ **Clima Despejado:** Condiciones óptimas de fricción aerodinámica estándar.")