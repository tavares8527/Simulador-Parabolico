import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página web
st.set_page_config(page_title="Simulador de Movimiento Parabólico", layout="centered")

st.title("🚀 Simulador de Movimiento Parabólico")
st.write("Ajusta los parámetros en la barra lateral para ver cómo cambia la trayectoria del proyectil.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros de Lanzamiento")

v0 = st.sidebar.slider("Velocidad inicial (m/s)", min_value=1.0, max_value=100.0, value=20.0, step=1.0)
angle_deg = st.sidebar.slider("Ángulo de lanzamiento (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)
g = st.sidebar.number_input("Gravedad (m/s²)", value=9.81)

# --- CÁLCULOS FÍSICOS ---
# Convertir ángulo a radianes
angle_rad = np.radians(angle_deg)

# Calcular tiempo de vuelo
t_vuelo = (2 * v0 * np.sin(angle_rad)) / g

# Crear un arreglo de tiempos desde 0 hasta el tiempo de vuelo
t = np.linspace(0, t_vuelo, num=200)

# Ecuaciones de posición
x = v0 * np.cos(angle_rad) * t
y = v0 * np.sin(angle_rad) * t - (0.5 * g * t**2)

# Altura máxima y alcance máximo
h_max = (v0**2 * (np.sin(angle_rad))**2) / (2 * g)
x_max = v0 * np.cos(angle_rad) * t_vuelo

# --- MOSTRAR RESULTADOS ---
col1, col2, col3 = st.columns(3)
col1.metric("Tiempo de vuelo", f"{t_vuelo:.2f} s")
col2.metric("Altura máxima", f"{h_max:.2f} m")
col3.metric("Alcance máximo", f"{x_max:.2f} m")

# --- GRÁFICA ---
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, y, label="Trayectoria", color="b", linewidth=2)
ax.fill_between(x, y, alpha=0.2, color="b") # Sombra bajo la curva

# Configuraciones del gráfico
ax.set_title("Trayectoria del Proyectil")
ax.set_xlabel("Distancia horizontal (m)")
ax.set_ylabel("Altura (m)")
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.grid(True, linestyle="--", alpha=0.7)
ax.legend()

# Mostrar la gráfica en Streamlit
st.pyplot(fig)