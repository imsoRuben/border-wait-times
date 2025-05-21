from fastapi import FastAPI
import requests
import uvicorn
import os
import xmltodict


app = FastAPI()

CBP_URL = "https://bwt.cbp.gov/xml/bwt.xml"

@app.get("/")
def read_root():
    return {"message": "Border Wait Times API is live. Go to /wait-times"}

@app.get("/wait-times")
def get_wait_times():
    try:
        response = requests.get(CBP_URL)
        data = xmltodict.parse(response.content)
        ports = data.get("border_wait_times", {}).get("port", [])

        summary = []
        for port in ports:
            item = {
                "crossing_name": port.get("crossing_name", ""),
                "port_name": port.get("port_name", ""),
                "border": port.get("border", ""),
                "date": port.get("date", ""),
                "time": port.get("time", ""),
                "passenger_vehicle_lanes": port.get("passenger_vehicle_lanes", {}),
                "commercial_vehicle_lanes": port.get("commercial_vehicle_lanes", {}),
                "pedestrian_lanes": port.get("pedestrian_lanes", {}),
                "notice": port.get("construction_notice", "")
            }
            summary.append(item)

        return {
            "ports_found": len(summary),
            "all_ports_summary": summary
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/ports")
def get_all_ports():
    try:
        response = requests.get(CBP_URL)
        data = xmltodict.parse(response.content)
        ports = data.get("border_wait_times", {}).get("port", [])
        port_names = sorted({port.get("crossing_name", "Unknown") for port in ports})
        return {"available_ports": port_names}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Starting app on port {port}")
    uvicorn.run("border_app:app", host="0.0.0.0", port=port)