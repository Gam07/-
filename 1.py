import streamlit as st
import math

# ======================
# 🎨 UI
# ======================
st.set_page_config(page_title="Eccentric Footing", layout="centered")

st.markdown("""
<style>
.title {font-size:38px; font-weight:bold; text-align:center; color:#1f3c88;}
.card {
    background:#ffffff;
    padding:20px;
    border-radius:15px;
    box-shadow:0 5px 15px rgba(0,0,0,0.1);
    margin-bottom:20px;
}
.result {
    background:#eef7ff;
    padding:20px;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🏗️ Eccentric Footing Design</div>', unsafe_allow_html=True)

# ======================
# 🧮 FUNCTION
# ======================
def bearing_factors(phi):
    phi_rad = math.radians(phi)

    if phi == 0:
        Nc, Nq, Ngamma = 5.7, 1, 0
    else:
        Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.radians(45 + phi/2)))**2
        Nc = (Nq - 1) / math.tan(phi_rad)
        Ngamma = 2 * (Nq + 1) * math.tan(phi_rad)

    return Nc, Nq, Ngamma


# ======================
# 📐 INPUT
# ======================
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    B = st.number_input("Footing Width B (m)", value=1.9)
    L = st.number_input("Footing Length L (m)", value=1.9)

with col2:
    Df = st.number_input("Depth Df (m)", value=1.0)
    FS = st.number_input("Factor of Safety", value=3.0)

st.markdown("### 📍 Column Positions + Load")

cols = []
loads = []

for i in range(4):
    c1, c2, c3 = st.columns(3)
    x = c1.number_input(f"x{i+1}", value=0.3 + i*0.2)
    y = c2.number_input(f"y{i+1}", value=0.3 + i*0.2)
    P = c3.number_input(f"P{i+1} (kN)", value=200.0)

    cols.append((x, y))
    loads.append(P)

st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 🌱 SOIL
# ======================
st.markdown('<div class="card">', unsafe_allow_html=True)

c = st.number_input("Cohesion c (kPa)", value=10.0)
phi = st.number_input("Friction angle φ (deg)", value=30.0)
gamma = st.number_input("Unit weight γ (kN/m³)", value=18.0)

st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 🚀 CALC
# ======================
if st.button("🚀 Calculate"):

    P_total = sum(loads)

    # centroid
    x_bar = sum(loads[i]*cols[i][0] for i in range(4)) / P_total
    y_bar = sum(loads[i]*cols[i][1] for i in range(4)) / P_total

    # footing center
    x_center = B / 2
    y_center = L / 2

    ex = x_center - x_bar
    ey = y_center - y_bar

    B_eff = B - 2*abs(ex)
    L_eff = L - 2*abs(ey)

    st.markdown('<div class="card result">', unsafe_allow_html=True)

    st.write("### 📊 Results")
    st.write(f"ex = {ex:.3f} m")
    st.write(f"ey = {ey:.3f} m")

    if B_eff <= 0 or L_eff <= 0:
        st.error("❌ Overturning (B' ≤ 0 or L' ≤ 0)")
    else:
        Nc, Nq, Ngamma = bearing_factors(phi)

        qult = c*Nc + gamma*Df*Nq + 0.5*gamma*B_eff*Ngamma
        qall = qult / FS
        q_actual = P_total / (B_eff * L_eff)

        st.write(f"B' = {B_eff:.2f} m")
        st.write(f"L' = {L_eff:.2f} m")
        st.write(f"q_ult = {qult:.2f} kPa")
        st.write(f"q_all = {qall:.2f} kPa")
        st.write(f"q_actual = {q_actual:.2f} kPa")

        if q_actual <= qall:
            st.success("✅ SAFE DESIGN")
        else:
            st.error("❌ NOT SAFE")

    st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # 🧭 SIMPLE DIAGRAM
    # ======================
    st.write("### 📐 Layout (Text Diagram)")

    st.write(f"Footing center = ({x_center:.2f}, {y_center:.2f})")
    st.write(f"Load centroid = ({x_bar:.2f}, {y_bar:.2f})")

    for i, (x,y) in enumerate(cols):
        st.write(f"Column {i+1}: ({x:.2f}, {y:.2f})")
