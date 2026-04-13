import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador Tiro Libre", layout="wide")

st.title("🏟️ Simulador de Tiro Libre con Trazado en Tiempo Real")
st.write("Escribe los parámetros en la izquierda y presiona **Lanzar** para ver cómo el balón dibuja su propia trayectoria.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros de Lanzamiento")
v0 = st.sidebar.number_input("Velocidad inicial (m/s)", min_value=1.0, value=25.0, step=1.0)
angle_deg = st.sidebar.number_input("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81, step=0.1)

# --- CONFIGURACIÓN DE LA IMAGEN DE FONDO (ESTADIO) ---
IMAGEN_URL = "https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=2000&auto=format&fit=crop"
image_source = IMAGEN_URL

# --- CÁLCULOS FÍSICOS ---
angle_rad = np.radians(angle_deg)
if g > 0:
    t_vuelo = (2 * v0 * np.sin(angle_rad)) / g
else:
    t_vuelo = 0

# Crear 100 puntos de tiempo para la animación
t = np.linspace(0, t_vuelo, num=100)
x = v0 * np.cos(angle_rad) * t
y = v0 * np.sin(angle_rad) * t - (0.5 * g * t**2)
y = np.maximum(y, 0) # El balón no atraviesa el césped

h_max = np.max(y) if len(y) > 0 else 0
x_max = x[-1] if len(x) > 0 else 0

# --- CÁLCULOS DE VELOCIDAD Y ANÁLISIS FINAL ---
# Arrays de velocidad para cada instante de tiempo
vx = v0 * np.cos(angle_rad) * np.ones_like(t)
vy = v0 * np.sin(angle_rad) - (g * t)
v = np.sqrt(vx**2 + vy**2)

# Valores exactos en el momento del impacto (último punto del array)
vx_final = vx[-1] if len(vx) > 0 else 0
vy_final = vy[-1] if len(vy) > 0 else 0
v_final_magnitud = v[-1] if len(v) > 0 else 0

# Ángulo de impacto usando el arco tangente (en grados)
angle_final_rad = np.arctan2(vy_final, vx_final)
angle_final_deg = np.degrees(angle_final_rad)

# --- CREAR LA ANIMACIÓN CON PLOTLY ---

fig = go.Figure(
    data=[
        go.Scatter(x=[x[0]], y=[y[0]], mode="lines", name="Rastro", line=dict(dash="dash", color="#FFD700", width=3)),
        go.Scatter(x=[x[0]], y=[y[0]], mode="text", text="⚽", textfont=dict(size=30), name="Balón")
    ]
)

frames = []
for i in range(len(t)):
    frames.append(go.Frame(data=[
        go.Scatter(x=x[:i+1], y=y[:i+1], mode="lines", line=dict(dash="dash", color="#FFD700", width=3)), 
        go.Scatter(x=[x[i]], y=[y[i]], mode="text", text="⚽", textfont=dict(size=30))
    ], name=str(i)))

fig.frames = frames

fig.add_annotation(x=0, y=0, text="🧍‍♂️", showarrow=False, font=dict(size=50), xanchor="right", yanchor="bottom")
fig.add_annotation(x=x_max, y=0, text="💥", showarrow=False, font=dict(size=45), yanchor="bottom")

margen_x = 10
margen_y = 5

fig.update_layout(
    xaxis=dict(range=[-2, x_max + margen_x], title="Distancia (m)", showgrid=False, zeroline=False, color="white"),
    yaxis=dict(range=[0, h_max + margen_y], title="Altura (m)", showgrid=False, zeroline=False, color="white"),
    
    images=[dict(
        source=image_source,
        xref="x", yref="y",             
        x=0 - 2, y=h_max + margen_y,   
        sizex=x_max + margen_x + 2, sizey=h_max + margen_y,     
        sizing="stretch", opacity=0.9, layer="below"         
    )],
    
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(
            label="▶️ Lanzar Tiro Libre",
            method="animate",
            args=[None, {"frame": {"duration": 40, "redraw": False}, "fromcurrent": False, "transition": {"duration": 0}}]
        )]
    )],
    showlegend=False,
    height=650, 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',  
)

# --- MOSTRAR RESULTADOS MÉTRICOS BÁSICOS ---
st.write("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tiempo de vuelo", f"{t_vuelo:.2f} s")
col2.metric("Altura máxima", f"{h_max:.2f} m")
col3.metric("Alcance máximo", f"{x_max:.2f} m")
col4.metric("Velocidad de impacto", f"{v_final_magnitud:.2f} m/s")

# Mostrar la gráfica interactiva
st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN NUEVA: ANÁLISIS DE VELOCIDAD FINAL ---
st.markdown("### 📊 Análisis del Impacto")

with st.container():
    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.metric("Velocidad Horizontal Final (Vx)", f"{vx_final:.2f} m/s")
    col_v2.metric("Velocidad Vertical Final (Vy)", f"{vy_final:.2f} m/s")
    col_v3.metric("Ángulo de Impacto", f"{angle_final_deg:.2f}°")
    
    # Texto explicativo dinámico basado en los resultados
    st.info(f"""
    **¿Qué significan estos números?**
    * **Velocidad Horizontal (Vx):** Se mantiene constante en **{vx_final:.2f} m/s** durante todo el vuelo (asumiendo que no hay fricción del aire).
    * **Velocidad Vertical (Vy):** Es negativa (**{vy_final:.2f} m/s**) porque el balón está cayendo en el momento del impacto. La gravedad aceleró el balón hacia abajo.
    * **Ángulo de Impacto:** El balón golpea el césped con una inclinación de **{abs(angle_final_deg):.2f}°** por debajo de la línea horizontal. Dado que iniciaste el tiro al nivel del suelo, el ángulo de caída es igual (pero negativo) al ángulo de lanzamiento.
    """)