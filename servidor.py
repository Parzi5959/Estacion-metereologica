from flask import Flask, jsonify
import requests

app = Flask(__name__)

LAT = 19.604044
LON = -99.041635

def obtener_ubicacion(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        headers = {"User-Agent": "ESP32"}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        res.close()

        address = data.get("address", {})
        ciudad = address.get("city") or address.get("town") or address.get("village") or "Ciudad desconocida"
        estado = address.get("state", "")
        pais = address.get("country", "")
        return f"{ciudad}, {estado}, {pais}"
    except Exception as e:
        print("❌ Error al obtener ubicación:", e)
        return "Ubicación desconocida"

@app.route("/datos")
def obtener_datos():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LAT}&longitude={LON}&current_weather=true&hourly=precipitation_probability,relative_humidity_2m,visibility&timezone=auto"
        )
        clima_res = requests.get(url, timeout=5)
        clima_data = clima_res.json()

        current = clima_data.get("current_weather", {})
        hourly = clima_data.get("hourly", {})

        ubicacion = obtener_ubicacion(LAT, LON)

        lluvia_prob = hourly.get("precipitation_probability", [0])
        if isinstance(lluvia_prob, list) and len(lluvia_prob) > 0:
            lluvia_prob = lluvia_prob[0]
        else:
            lluvia_prob = 0

        humedad = hourly.get("relative_humidity_2m", [0])
        if isinstance(humedad, list) and len(humedad) > 0:
            humedad = humedad[0]
        else:
            humedad = 0

        visib = hourly.get("visibility", [0])
        if isinstance(visib, list) and len(visib) > 0:
            visib = visib[0]
        else:
            visib = 0

        return jsonify({
            "temp": current.get("temperature", -1),
            "hum": humedad,
            "viento": current.get("windspeed", -1),
            "lluvia_prob": lluvia_prob,
            "visib": visib,
            "ubicacion": ubicacion
        })

    except Exception as e:
        print("❌ Error general:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)