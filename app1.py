import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

# Configuración de la página web
st.set_page_config(page_title="Simulador en el Estadio", layout="wide")

st.title("🏟️ Lanzamiento Parabólico en el Estadio")
st.write("Escribe los parámetros en la izquierda y presiona **Lanzar** en la gráfica para ver el tiro libre.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros de Lanzamiento")
v0 = st.sidebar.number_input("Velocidad inicial (m/s)", min_value=1.0, value=25.0, step=1.0)
angle_deg = st.sidebar.number_input("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)
vf = st.sidebar.number_input("Velocidad Final (m/s)", min_value=1.0, value=25.0, step=1.0)
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81, step=0.1)

# --- CONFIGURACIÓN DE LA IMAGEN DE FONDO (ESTADIO) ---
# Hemos cambiado la URL por la de un impresionante estadio de fútbol.
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
y = np.maximum(y, 0) # Asegurar que el balón no atraviese el césped

h_max = np.max(y) if len(y) > 0 else 0
x_max = x[-1] if len(x) > 0 else 0

# --- CREAR LA ANIMACIÓN CON PLOTLY Y FONDO DE ESTADIO ---
fig = go.Figure(
    data=[
        # Trayectoria punteada de color blanco/amarillo para que resalte en el césped
        go.Scatter(x=x, y=y, mode="lines", name="Ruta", line=dict(dash="dash", color="#FFFACD", width=3)),
        # El balón (⚽)
        go.Scatter(x=[x[0]], y=[y[0]], mode="text", text="⚽", textfont=dict(size=30), name="Balón")
    ]
)

# Configurar los fotogramas para la animación
frames = [
    go.Frame(data=[
        go.Scatter(x=x, y=y, mode="lines", line=dict(dash="dash", color="#FFFACD", width=3)), 
        go.Scatter(x=[x[i]], y=[y[i]], mode="text", text="⚽", textfont=dict(size=30))
    ], name=str(i))
    for i in range(len(t))
]
fig.frames = frames

# Añadir Jugador (🧍‍♂️) y el impacto al caer (💥)
fig.add_annotation(x=0, y=0, text="🧍‍♂️", showarrow=False, font=dict(size=50), xanchor="right", yanchor="bottom")
fig.add_annotation(x=x_max, y=0, text="💥", showarrow=False, font=dict(size=45), yanchor="bottom")

# *** CONFIGURACIÓN DEL FONDO DEL ESTADIO ***
margen_x = 10
margen_y = 5

fig.update_layout(
    # Configuración de los ejes (textos en blanco para verse bien de noche)
    xaxis=dict(range=[-2, x_max + margen_x], title="Distancia (m)", showgrid=False, zeroline=False, color="white"),
    yaxis=dict(range=[0, h_max + margen_y], title="Altura (m)", showgrid=False, zeroline=False, color="white"),
    
    # Lista de imágenes de fondo
    images=[dict(
        source=image_source,
        xref="x",             
        yref="y",             
        x=0 - 2,              
        y=h_max + margen_y,   
        sizex=x_max + margen_x + 2, 
        sizey=h_max + margen_y,     
        sizing="stretch",     
        opacity=0.9,          # Un toquecito de transparencia para integrar la gráfica
        layer="below"         
    )],
    
    # Botón de Lanzar
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(
            label="▶️ Lanzar Balón",
            method="animate",
            args=[None, {"frame": {"duration": 30, "redraw": False}, "fromcurrent": False, "transition": {"duration": 0}}]
        )]
    )],
    showlegend=False,
    height=650, 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',  
)

# --- MOSTRAR RESULTADOS MÉTRICOS ---
st.write("---")
col1, col2, col3 = st.columns(3)
col1.metric("Tiempo de vuelo", f"{t_vuelo:.2f} s")
col2.metric("Altura máxima", f"{h_max:.2f} m")
col3.metric("Alcance máximo", f"{x_max:.2f} m")

# Mostrar la gráfica interactiva
st.plotly_chart(fig, use_container_width=True)