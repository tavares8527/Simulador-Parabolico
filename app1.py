import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador Tiro Libre", layout="wide")

st.title("🏟️ Simulador de Tiro Libre con Trazado en Tiempo Real")
st.write("ESCRIBE LOS PARAMETROS DE LA IZQUIERDA Y PRESIONA **LANZAR** PARA VER COMO EL BALON DIBUJA SU PROPIA TRAYECTORIA.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Parámetros de Lanzamiento")
v0 = st.sidebar.number_input("Velocidad inicial (m/s)", min_value=1.0, value=25.0, step=1.0)
angle_deg = st.sidebar.number_input("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)

# NUEVO: Se permite la gravedad negativa
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81, step=0.1)

# --- CÁLCULOS FÍSICOS BÁSICOS PARA EL VUELO ---
angle_rad = np.radians(angle_deg)

# NUEVO: Lógica para manejar gravedad cero o negativa
if g > 0:
    t_vuelo = (2 * v0 * np.sin(angle_rad)) / g
else:
    # Si la gravedad es <= 0, el balón nunca cae. Establecemos 5 segundos de vuelo para observar cómo se eleva.
    t_vuelo = 5.0 

# --- NUEVO: CONSULTA DE POSICIÓN POR TIEMPO ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Consultar Posición")
t_consulta = st.sidebar.slider("Selecciona un momento del vuelo (s)", min_value=0.0, max_value=float(t_vuelo), value=0.0, step=0.01)

# Cálculos para ese tiempo específico
x_consulta = v0 * np.cos(angle_rad) * t_consulta
y_consulta = v0 * np.sin(angle_rad) * t_consulta - (0.5 * g * t_consulta**2)

st.sidebar.info(f"""
**A los {t_consulta:.2f} segundos:**
📍 **Distancia (X):** {x_consulta:.2f} m
📍 **Altura (Y):** {y_consulta:.2f} m
""")

# --- NUEVO: AUDIO DEL ESTADIO ---
st.sidebar.markdown("---")
st.sidebar.header("🔊 Ambiente")
reproducir_audio = st.sidebar.checkbox("Activar sonido de estadio", value=False)
if reproducir_audio:
    # URL de sonido de estadio de uso libre (Google Sounds)
    audio_url = "https://actions.google.com/sounds/v1/crowds/stadium_crowd_exterior.ogg"
    st.sidebar.audio(audio_url, format="audio/ogg", autoplay=True)

# --- CONTINÚAN LOS CÁLCULOS PARA LA GRÁFICA ---
# Crear 100 puntos de tiempo para la animación
t = np.linspace(0, t_vuelo, num=100)
x = v0 * np.cos(angle_rad) * t
y = v0 * np.sin(angle_rad) * t - (0.5 * g * t**2)

if g > 0:
    y = np.maximum(y, 0) # El balón no atraviesa el césped (solo aplica en gravedad normal)

h_max = np.max(y) if len(y) > 0 else 0
x_max = x[-1] if len(x) > 0 else 0

# --- CÁLCULOS DE VELOCIDAD Y ANÁLISIS FINAL ---
vx = v0 * np.cos(angle_rad) * np.ones_like(t)
vy = v0 * np.sin(angle_rad) - (g * t)
v = np.sqrt(vx**2 + vy**2)

vx_final = vx[-1] if len(vx) > 0 else 0
vy_final = vy[-1] if len(vy) > 0 else 0
v_final_magnitud = v[-1] if len(v) > 0 else 0

angle_final_rad = np.arctan2(vy_final, vx_final)
angle_final_deg = np.degrees(angle_final_rad)

# --- CONFIGURACIÓN DE LA IMAGEN DE FONDO (ESTADIO) ---
IMAGEN_URL = "https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=2000&auto=format&fit=crop"

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
# Si la gravedad es <= 0, no mostramos el impacto porque nunca choca con el suelo
if g > 0:
    fig.add_annotation(x=x_max, y=0, text="💥", showarrow=False, font=dict(size=45), yanchor="bottom")

margen_x = 10
margen_y = 5

fig.update_layout(
    xaxis=dict(range=[-2, x_max + margen_x], title="Distancia (m)", showgrid=False, zeroline=False, color="white"),
    yaxis=dict(range=[0, h_max + margen_y], title="Altura (m)", showgrid=False, zeroline=False, color="white"),
    
    images=[dict(
        source=IMAGEN_URL,
        xref="x", yref="y",             
        x=0 - 2, y=h_max + margen_y,   
        sizex=x_max + margen_x + 2, sizey=h_max + margen_y,     
        sizing="stretch", opacity=0.9, layer="below"        
    )],
    
    updatemenus=[dict(
        type="buttons",
        bordercolor="#2E7D32",
        buttons=[dict(
            label="<span style='color: #FF0000;'>▶️ Lanzar Tiro Libre</span>",
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
col3.metric("Alcance final en X", f"{x_max:.2f} m")
col4.metric("Velocidad final", f"{v_final_magnitud:.2f} m/s")

# Mostrar la gráfica interactiva
st.plotly_chart(fig, use_container_width=True)

# --- ANÁLISIS DE VELOCIDAD FINAL ---
st.markdown("### 📊 Análisis del Último Instante")

with st.container():
    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.metric("Velocidad Horizontal Final (Vx)", f"{vx_final:.2f} m/s")
    col_v2.metric("Velocidad Vertical Final (Vy)", f"{vy_final:.2f} m/s")
    col_v3.metric("Ángulo Final", f"{angle_final_deg:.2f}°")
    
    # Mensaje dinámico según la gravedad
    if g > 0:
        st.info(f"""
        **¿Qué significan estos números (Gravedad Normal)?**
        * **Velocidad Horizontal (Vx):** Se mantiene constante en **{vx_final:.2f} m/s** durante todo el vuelo.
        * **Velocidad Vertical (Vy):** Es negativa (**{vy_final:.2f} m/s**) porque el balón está cayendo en el momento del impacto.
        * **Ángulo de Impacto:** El balón golpea el césped con una inclinación de **{abs(angle_final_deg):.2f}°** hacia abajo.
        """)
    else:
        st.warning(f"""
        **¡Alerta de Gravedad Anómala!**
        Como la gravedad está configurada en **{g:.2f} m/s²**, el balón no está cayendo. 
        Su velocidad vertical final (Vy) es de **{vy_final:.2f} m/s**, lo que significa que a los 5 segundos sigue subiendo hacia el espacio con un ángulo ascendente de **{angle_final_deg:.2f}°**.
        """)