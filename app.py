# import streamlit as st
# from datetime import datetime, date, time
# import requests


# '''
# # TaxiFareModel front
# '''
# ## Here we would like to add some controllers in order to ask the user to select the parameters of the ride
# pickup_date = st.date_input("Pickup date", value=date.today())
# pickup_time = st.time_input("Pickup time", value=time(12, 0))
# pickup_lon = st.number_input("Pickup longitude", value=-73.985428, format="%.6f")
# pickup_lat = st.number_input("Pickup latitude", value=40.748817, format="%.6f")
# dropoff_lon = st.number_input("Dropoff longitude", value=-73.985135, format="%.6f")
# dropoff_lat = st.number_input("Dropoff latitude", value=40.758896, format="%.6f")
# passenger_count = st.number_input("Passenger count", min_value=1, max_value=8, value=1, step=1)


# url = 'https://taxifare.lewagon.ai/predict'

# if url == 'https://taxifare.lewagon.ai/predict':

#     st.markdown('(Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...)')

# if st.button("Predict fare 💸"):
#     pickup_datetime = datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")
#     params = {
#         "pickup_datetime": pickup_datetime,
#         "pickup_longitude": float(pickup_lon),
#         "pickup_latitude": float(pickup_lat),
#         "dropoff_longitude": float(dropoff_lon),
#         "dropoff_latitude": float(dropoff_lat),
#         "passenger_count": int(passenger_count),
#     }

#     try:
#         response = requests.get(url, params=params, timeout=10)
#         print(f"response: {response.status_code}")
#         response.raise_for_status()
#         prediction = response.json().get("fare") or response.json().get("fare_amount")
#         print(f"prediction: {prediction}")
#         if prediction:
#             st.success(f"Estimated fare: ${float(prediction):.2f}")
#         else:
#             st.warning("No fare returned from API")
#             st.json(response.json())
#     except Exception as e:
#         st.error(f"Request failed: {e}")

"""THIS IS AN ALTERNATIVE CREATED WITH A MAP WITH THE HELP OF AI TO SEE WHAT'S POSSIBLE WITH STREAMLIT, ABOVE IS THE ORIGINAL AOLUTION I CAME UP WITH."""

import streamlit as st
import requests
from datetime import datetime, date, time
import math
import folium
from streamlit_folium import st_folium

# ───────────────────────── Page setup ─────────────────────────
st.set_page_config(page_title="TaxiFare", page_icon="🚕", layout="wide")

st.html("""
<style>
  :root {
    --bg: #0f1115;
    --card: #151925;
    --muted: #9aa4b2;
    --text: #e7ecf3;
  }
  .hero {
    text-align: center;
    margin-bottom: 20px;
  }
  .title {
    font-size: 40px;
    font-weight: 800;
    color: var(--text);
  }
  .subtitle {
    font-size: 15px;
    color: var(--muted);
    margin-top: 4px;
  }
  .kpi-card {
    margin-top: 10px; background: var(--card);
    border: 1px solid rgba(255,255,255,.08); border-radius: 16px;
    padding: 18px; text-align:center;
  }
  .kpi-eyebrow { color: var(--muted); font-size: 12px; letter-spacing: .4px; text-transform: uppercase; }
  .kpi-value { font-size: 42px; font-weight: 800; margin: 4px 0; }
  .kpi-sub { color: var(--muted); font-size: 13px; }
</style>

<div class="hero">
  <div class="title">🚕 TaxiFareModel</div>
</div>
""")

# ───────────────────────── Helpers ─────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def midpt(lat1, lon1, lat2, lon2):
    return (lat1 + lat2) / 2, (lon1 + lon2) / 2

# ───────────────────────── Layout (controls + map) ─────────────────────────
left, right = st.columns([1, 1], vertical_alignment="top")

with left:
    with st.form("ride_params", border=False):
        d = st.date_input("Pickup date", value=date.today())
        t = st.time_input("Pickup time", value=time(12, 0))

        c1, c2 = st.columns(2)
        with c1:
            pick_lon = st.number_input("Pickup longitude", value=-73.985428, format="%.6f")
            pick_lat = st.number_input("Pickup latitude",  value=40.748817,  format="%.6f")
        with c2:
            drop_lon = st.number_input("Dropoff longitude", value=-73.985135, format="%.6f")
            drop_lat = st.number_input("Dropoff latitude",  value=40.758896,  format="%.6f")

        pax = st.number_input("Passenger count", min_value=1, max_value=8, value=1, step=1)

        # Spacer to push button down
        st.write("")
        st.write("")
        st.write("")
        go = st.form_submit_button("Predict fare 💸", use_container_width=True)

# ───────────────────────── Map (Folium + OSM) ─────────────────────────
center = midpt(pick_lat, pick_lon, drop_lat, drop_lon)
m = folium.Map(location=center, zoom_start=15, tiles="CartoDB positron", control_scale=True)

folium.Marker([pick_lat, pick_lon], tooltip="Pickup",
              icon=folium.Icon(color="green", icon="taxi", prefix="fa")).add_to(m)
folium.Marker([drop_lat, drop_lon], tooltip="Dropoff",
              icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)
m.fit_bounds([[pick_lat, pick_lon], [drop_lat, drop_lon]], padding=(30, 30))

with right:
    st.caption("Trip preview")
    st_folium(m, use_container_width=True, height=520)

# ───────────────────────── Prediction ─────────────────────────
API_URL = "https://taxifare.lewagon.ai/predict"

if go:
    when = datetime.combine(d, t).strftime("%Y-%m-%d %H:%M:%S")
    params = {
        "pickup_datetime":  when,
        "pickup_longitude": float(pick_lon),
        "pickup_latitude":  float(pick_lat),
        "dropoff_longitude": float(drop_lon),
        "dropoff_latitude":  float(drop_lat),
        "passenger_count":   int(pax),
    }

    try:
        with st.spinner("Calling API…"):
            r = requests.get(API_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()

        fare = data.get("fare") or data.get("fare_amount") or data.get("prediction")
        dist_km = haversine(pick_lat, pick_lon, drop_lat, drop_lon)

        st.html(f"""
        <div class="kpi-card">
          <div class="kpi-eyebrow">Estimated fare</div>
          <div class="kpi-value">${float(fare):.2f}</div>
          <div class="kpi-sub">Approx. distance: {dist_km:.2f} km • Passengers: {pax}</div>
        </div>
        """)

    except Exception as e:
        st.error(f"Request failed: {e}")
