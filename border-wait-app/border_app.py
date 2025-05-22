from fastapi import FastAPI
import requests
import uvicorn
import os
import xmltodict
from supabase import create_client, Client

app = FastAPI()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CBP_URL = "https://bwt.cbp.gov/xml/bwt.xml"

@app.get("/")
def read_root():
    return {"message": "Border Wait Times API is live. Go to /wait-times"}

@app.get("/wait-times")
def get_wait_times():
    try:
        response = requests.get(CBP_URL)
        data = xmltodict.parse(response.content)
        ports = data.get("border_wait_time", {}).get("port", [])

        summary = []
        for port in ports:
            passenger = port.get("passenger_vehicle_lanes", {}).get("standard", {})
            passenger_ready = port.get("passenger_vehicle_lanes", {}).get("ready", {})
            passenger_sentri = port.get("passenger_vehicle_lanes", {}).get("sentri", {})

            commercial = port.get("commercial_vehicle_lanes", {}).get("standard", {})
            commercial_fast = port.get("commercial_vehicle_lanes", {}).get("fast", {})

            pedestrian = port.get("pedestrian_lanes", {}).get("standard", {})
            pedestrian_ready = port.get("pedestrian_lanes", {}).get("ready", {})
            pedestrian_sentri = port.get("pedestrian_lanes", {}).get("sentri", {})
            pedestrian_ready_sentri = port.get("pedestrian_lanes", {}).get("ready_sentri", {})

            item = {
                "crossing_name": port.get("crossing_name", ""),
                "port_name": port.get("port_name", ""),
                "port_code": port.get("port_code", ""),
                "state": port.get("state", ""),
                "region": port.get("region", ""),
                "hours": port.get("hours", ""),
                "border": port.get("border", ""),
                "date": port.get("date") or None,
                "time": port.get("time") or None,
                "notice": port.get("construction_notice", ""),
                "note": port.get("note", ""),
                "port_status": port.get("port_status", ""),

                "passenger_standard_delay_minutes": passenger.get("delay_minutes"),
                "passenger_standard_lanes_open": passenger.get("lanes_open"),
                "passenger_standard_update_time": passenger.get("update_time"),

                "passenger_ready_delay_minutes": passenger_ready.get("delay_minutes"),
                "passenger_ready_lanes_open": passenger_ready.get("lanes_open"),
                "passenger_ready_update_time": passenger_ready.get("update_time"),

                "passenger_sentri_delay_minutes": passenger_sentri.get("delay_minutes"),
                "passenger_sentri_lanes_open": passenger_sentri.get("lanes_open"),
                "passenger_sentri_update_time": passenger_sentri.get("update_time"),

                "commercial_standard_delay_minutes": commercial.get("delay_minutes"),
                "commercial_standard_lanes_open": commercial.get("lanes_open"),
                "commercial_standard_update_time": commercial.get("update_time"),

                "commercial_fast_delay_minutes": commercial_fast.get("delay_minutes"),
                "commercial_fast_lanes_open": commercial_fast.get("lanes_open"),
                "commercial_fast_update_time": commercial_fast.get("update_time"),

                "pedestrian_standard_delay_minutes": pedestrian.get("delay_minutes"),
                "pedestrian_standard_lanes_open": pedestrian.get("lanes_open"),
                "pedestrian_standard_update_time": pedestrian.get("update_time"),

                "pedestrian_ready_delay_minutes": pedestrian_ready.get("delay_minutes"),
                "pedestrian_ready_lanes_open": pedestrian_ready.get("lanes_open"),
                "pedestrian_ready_update_time": pedestrian_ready.get("update_time"),

                "pedestrian_sentri_delay_minutes": pedestrian_sentri.get("delay_minutes"),
                "pedestrian_sentri_lanes_open": pedestrian_sentri.get("lanes_open"),
                "pedestrian_sentri_update_time": pedestrian_sentri.get("update_time"),

                "pedestrian_ready_sentri_delay_minutes": pedestrian_ready_sentri.get("delay_minutes"),
                "pedestrian_ready_sentri_lanes_open": pedestrian_ready_sentri.get("lanes_open"),
                "pedestrian_ready_sentri_update_time": pedestrian_ready_sentri.get("update_time"),
                "full_xml": port,
            }

            known_keys = {
                "crossing_name", "port_name", "port_code", "state", "region", "hours", "border",
                "date", "time", "construction_notice", "note", "port_status",
                "passenger_vehicle_lanes", "commercial_vehicle_lanes", "pedestrian_lanes"
            }
            unknown_keys = set(port.keys()) - known_keys
            if unknown_keys:
                print(f"🔍 Unparsed keys found at {port.get('port_name')}: {unknown_keys}")

            summary.append(item)
            result = supabase.table("border_wait_history").insert(item).execute()
            print("🔁 Insert result:", result)

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
        ports = data.get("border_wait_time", {}).get("port", [])
        port_names = sorted({port.get("crossing_name", "Unknown") for port in ports})
        return {"available_ports": port_names}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Starting app on port {port}")
    uvicorn.run("border_app:app", host="0.0.0.0", port=port)