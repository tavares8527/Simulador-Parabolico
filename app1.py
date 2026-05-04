import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Simulador Tiro Libre", layout="wide")

# --- AUDIO DEL ESTADIO (INTENTO DE AUTOPLAY FORZADO EN HTML) ---
# Usamos un servidor de Wikimedia para asegurar que el archivo no esté caído.
AUDIO_URL = "https://upload.wikimedia.org/wikipedia/commons/7/75/Football_Crowd_-_Match_Atmosphere.ogg"

st.markdown(
    f"""
    <div style="background-color: #1e1e1e; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #2E7D32;">
        <p style="margin: 0; font-weight: bold; color: #ffffff; font-size: 14px;">🔊 Ambiente de Estadio</p>
        <p style="margin: 2px 0 8px 0; font-size: 11px; color: #aaaaaa;">El sonido intentará iniciar solo. Si tu navegador bloquea el autoplay por seguridad, dale Play abajo:</p>
        <audio autoplay loop controls style="width: 100%; height: 35px;">
            <source src="{AUDIO_URL}" type="audio/ogg">
        </audio>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🏟️ Simulador de Tiro Libre con Trazado en Tiempo Real")
st.write("ESCRIBE LOS PARAMETROS DE LA IZQUIERDA Y PRESIONA **LANZAR** PARA VER COMO EL BALON DIBUJA SU PROPIA TRAYECTORIA.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Parámetros de Lanzamiento")
v0 = st.sidebar.number_input("Velocidad inicial (m/s)", min_value=1.0, value=25.0, step=1.0)
angle_deg = st.sidebar.number_input("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81, step=0.1)

# --- CÁLCULOS FÍSICOS BÁSICOS PARA EL VUELO ---
angle_rad = np.radians(angle_deg)

if g > 0:
    t_vuelo = (2 * v0 * np.sin(angle_rad)) / g
else:
    # Si la gravedad es <= 0, el balón nunca cae. Vuelo arbitrario de 5 segundos.
    t_vuelo = 5.0 

# Crear 100 puntos de tiempo para la animación
t = np.linspace(0, t_vuelo, num=100)
x = v0 * np.cos(angle_rad) * t
y = v0 * np.sin(angle_rad) * t - (0.5 * g * t**2)

if g > 0:
    y = np.maximum(y, 0) # El balón no atraviesa el césped

h_max = np.max(y) if len(y) > 0 else 0
x_max = x[-1] if len(x) > 0 else 0

# --- CUADRO PARA MEDIR TIEMPO EN CUALQUIER POSICIÓN ---
st.sidebar.markdown("---")
st.sidebar.header("⏱️ Medir Tiempo por Posición")
st.sidebar.write("Ingresa una distancia para saber en qué momento el balón pasa por ahí.")

# El usuario ingresa una posición en X
x_target = st.sidebar.number_input("Distancia recorrida en X (m)", min_value=0.0, max_value=float(x_max) if x_max > 0 else 100.0, value=float(x_max/2) if x_max > 0 else 0.0, step=0.5)

# Calculamos el tiempo y la altura para esa posición X
if np.isclose(np.cos(angle_rad), 0): # Evitar división por cero si tira a 90 grados exactos
    t_target = 0 if x_target == 0 else float('inf')
    y_target = v0 * t_target - 0.5 * g * t_target**2 if t_target != float('inf') else 0
else:
    t_target = x_target / (v0 * np.cos(angle_rad))
    y_target = v0 * np.sin(angle_rad) * t_target - (0.5 * g * t_target**2)

st.sidebar.success(f"""
**Datos en la posición X = {x_target:.2f} m:**
* ⏱️ **Tiempo transcurrido:** {t_target:.2f} s
* 📍 **Altura (Y):** {y_target:.2f} m
""")

# --- CÁLCULOS DE VELOCIDAD Y ANÁLISIS FINAL ---
vx = v0 * np.cos(angle_rad) * np.ones_like(t)
vy = v0 * np.sin(angle_rad) - (g * t)
v = np.sqrt(vx**2 + vy**2)

vx_final = vx[-1] if len(vx) > 0 else 0
vy_final = vy[-1] if len(vy) > 0 else 0
v_final_magnitud = v[-1] if len(v) > 0 else 0

angle_final_rad = np.arctan2(vy_final, vx_final)
angle_final_deg = np.degrees(angle_final_rad)

# --- CONFIGURACIÓN DE LA IMAGEN DE FONDO ---
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
        Su velocidad vertical final (Vy) es de **{vy_final:.2f} m/s**, lo que significa que a los 5 segundos sigue subiendo con un ángulo ascendente de **{angle_final_deg:.2f}°**.
        """)