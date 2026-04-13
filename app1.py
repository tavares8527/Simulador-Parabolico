import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

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
# Mantenemos la imagen del estadio de fútbol
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

# --- CREAR LA ANIMACIÓN CON PLOTLY (TRAZADO ACUMULATIVO) ---

# 1. Escenario Inicial (Frame 0)
fig = go.Figure(
    data=[
        # Rastro (Línea punteada): Inicialmente es solo el punto de partida
        go.Scatter(x=[x[0]], y=[y[0]], mode="lines", name="Rastro", line=dict(dash="dash", color="#FFD700", width=3)),
        # El balón (⚽): En el punto de partida
        go.Scatter(x=[x[0]], y=[y[0]], mode="text", text="⚽", textfont=dict(size=30), name="Balón")
    ]
)

# 2. Configurar los "fotogramas" para la animación acumulativa
# Usamos slicing [ : i+1] para dibujar la línea HASTA el punto actual 'i'
frames = []
for i in range(len(t)):
    frames.append(go.Frame(data=[
        # Actualizamos la LÍNEA para que muestre todos los puntos hasta 'i'
        go.Scatter(x=x[:i+1], y=y[:i+1], mode="lines", line=dict(dash="dash", color="#FFD700", width=3)), 
        # Actualizamos el BALÓN para que esté en el punto exacto 'i'
        go.Scatter(x=[x[i]], y=[y[i]], mode="text", text="⚽", textfont=dict(size=30))
    ], name=str(i)))

fig.frames = frames

# 3. Añadir Personaje (🧍‍♂️) y el impacto al caer (💥)
fig.add_annotation(x=0, y=0, text="🧍‍♂️", showarrow=False, font=dict(size=50), xanchor="right", yanchor="bottom")
fig.add_annotation(x=x_max, y=0, text="💥", showarrow=False, font=dict(size=45), yanchor="bottom")

# *** CONFIGURACIÓN DEL FONDO Y DISEÑO ***
margen_x = 10
margen_y = 5

fig.update_layout(
    # Configuración de los ejes (textos en blanco para verse bien)
    xaxis=dict(range=[-2, x_max + margen_x], title="Distancia (m)", showgrid=False, zeroline=False, color="white"),
    yaxis=dict(range=[0, h_max + margen_y], title="Altura (m)", showgrid=False, zeroline=False, color="white"),
    
    # Imagen de fondo (Estadio)
    images=[dict(
        source=image_source,
        xref="x", yref="y",             
        x=0 - 2, y=h_max + margen_y,   
        sizex=x_max + margen_x + 2, sizey=h_max + margen_y,     
        sizing="stretch", opacity=0.9, layer="below"         
    )],
    
    # Botón de Lanzar (ajustamos la duración para que sea suave)
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(
            label="▶️ Lanzar Tiro Libre",
            method="animate",
            # Aumentamos ligeramente la duración del frame para disfrutar el rastro
            args=[None, {"frame": {"duration": 40, "redraw": False}, "fromcurrent": False, "transition": {"duration": 0}}]
        )]
    )],
    showlegend=False,
    height=650, 
    paper_bgcolor='rgba(0,0,0,0)', # Transparente para integrar con Streamlit
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