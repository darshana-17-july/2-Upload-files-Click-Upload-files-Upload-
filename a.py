import streamlit as st
from PIL import Image
import piexif
import folium
from streamlit_folium import st_folium
import requests
import os

# ===== HEADER =====
logo_path = "logo4.jpeg"

col1, col2 = st.columns([1,5])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=90)

with col2:
    st.markdown(
        "<h1 style='padding-top:20px;'>🌱 Geo-Tagged Plant Identification</h1>",
        unsafe_allow_html=True
    )

st.write("---")

# ===== Convert GPS =====
def convert_to_degrees(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]
    return d + (m / 60.0) + (s / 3600.0)

# ===== Upload =====
uploaded_file = st.file_uploader("📷 Upload Plant Image", type=["jpg","jpeg","png"])

API_KEY = "2b10By6ROq3kpVx4dLUOidu"

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    # ================= PLANTNET AI =================
    image.save("temp.jpg")

    url = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"
    files = [("images", open("temp.jpg","rb"))]

    response = requests.post(url, files=files)

    if response.status_code == 200:
        data = response.json()

        if data.get("results"):
            plant = data["results"][0]

            st.subheader("🌿 Plant Prediction")

            st.success(
                plant["species"]["scientificNameWithoutAuthor"]
            )

            names = plant["species"].get("commonNames", [])
            if names:
                st.write("### Common Names:")
                for n in names:
                    st.write(f"- {n}")

    # ================= GPS DATA =================
    if "exif" in image.info:
        exif_dict = piexif.load(image.info["exif"])
        gps = exif_dict["GPS"]

        if gps:
            lat = convert_to_degrees(gps[2])
            lon = convert_to_degrees(gps[4])

            if gps.get(1) == b'S':
                lat = -lat
            if gps.get(3) == b'W':
                lon = -lon

            st.subheader("📍 GPS Details")
            st.success(f"Latitude: {lat}")
            st.success(f"Longitude: {lon}")

            # Date & Time
            date = exif_dict["0th"].get(piexif.ImageIFD.DateTime, b"").decode()
            if date:
                st.info(f"🕒 Date & Time: {date}")

            # Google Maps link
            st.markdown(f"[🌍 Open in Google Maps](https://www.google.com/maps?q={lat},{lon})")

            # Map
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon]).add_to(m)
            st_folium(m, width=700)

        else:
            st.warning("No GPS data found")

    else:
        st.warning("No EXIF data found")