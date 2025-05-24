from fastapi import FastAPI
import requests
import uvicorn
import os
import xmltodict
from supabase import create_client, Client

def clean_value(val):
    if val in ("", "N/A", "Lanes Closed", None):
        return None
    return val

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
            if not passenger_ready:
                print(f"⚠️ No 'passenger_ready' data for: {port.get('port_name')}")
            passenger_sentri = port.get("passenger_vehicle_lanes", {}).get("sentri", {})
            if not passenger_sentri:
                print(f"⚠️ No 'passenger_sentri' data for: {port.get('port_name')}")

            commercial = port.get("commercial_vehicle_lanes", {}).get("standard", {})
            if not commercial:
                print(f"⚠️ No 'commercial_standard' data for: {port.get('port_name')}")
            commercial_fast = port.get("commercial_vehicle_lanes", {}).get("fast", {})
            if not commercial_fast:
                print(f"⚠️ No 'commercial_fast' data for: {port.get('port_name')}")

            pedestrian = port.get("pedestrian_lanes", {}).get("standard", {})
            if not pedestrian:
                print(f"⚠️ No 'pedestrian_standard' data for: {port.get('port_name')}")
            pedestrian_ready = port.get("pedestrian_lanes", {}).get("ready", {})
            if not pedestrian_ready:
                print(f"⚠️ No 'pedestrian_ready' data for: {port.get('port_name')}")
            pedestrian_sentri = port.get("pedestrian_lanes", {}).get("sentri", {})
            if not pedestrian_sentri:
                print(f"⚠️ No 'pedestrian_sentri' data for: {port.get('port_name')}")
            pedestrian_ready_sentri = port.get("pedestrian_lanes", {}).get("ready_sentri", {})
            if not pedestrian_ready_sentri:
                print(f"⚠️ No 'pedestrian_ready_sentri' data for: {port.get('port_name')}")

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

                "passenger_standard_delay_minutes": clean_value(passenger.get("delay_minutes")),
                "passenger_standard_lanes_open": clean_value(passenger.get("lanes_open")),
                "passenger_standard_update_time": clean_value(passenger.get("update_time")),

                "passenger_ready_delay_minutes": clean_value(passenger_ready.get("delay_minutes")),
                "passenger_ready_lanes_open": clean_value(passenger_ready.get("lanes_open")),
                "passenger_ready_update_time": clean_value(passenger_ready.get("update_time")),

                "passenger_sentri_delay_minutes": clean_value(passenger_sentri.get("delay_minutes")),
                "passenger_sentri_lanes_open": clean_value(passenger_sentri.get("lanes_open")),
                "passenger_sentri_update_time": clean_value(passenger_sentri.get("update_time")),

                "commercial_standard_delay_minutes": clean_value(commercial.get("delay_minutes")),
                "commercial_standard_lanes_open": clean_value(commercial.get("lanes_open")),
                "commercial_standard_update_time": clean_value(commercial.get("update_time")),

                "commercial_fast_delay_minutes": clean_value(commercial_fast.get("delay_minutes")),
                "commercial_fast_lanes_open": clean_value(commercial_fast.get("lanes_open")),
                "commercial_fast_update_time": clean_value(commercial_fast.get("update_time")),

                "pedestrian_standard_delay_minutes": clean_value(pedestrian.get("delay_minutes")),
                "pedestrian_standard_lanes_open": clean_value(pedestrian.get("lanes_open")),
                "pedestrian_standard_update_time": clean_value(pedestrian.get("update_time")),

                "pedestrian_ready_delay_minutes": clean_value(pedestrian_ready.get("delay_minutes")),
                "pedestrian_ready_lanes_open": clean_value(pedestrian_ready.get("lanes_open")),
                "pedestrian_ready_update_time": clean_value(pedestrian_ready.get("update_time")),

                "pedestrian_sentri_delay_minutes": clean_value(pedestrian_sentri.get("delay_minutes")),
                "pedestrian_sentri_lanes_open": clean_value(pedestrian_sentri.get("lanes_open")),
                "pedestrian_sentri_update_time": clean_value(pedestrian_sentri.get("update_time")),

                "pedestrian_ready_sentri_delay_minutes": clean_value(pedestrian_ready_sentri.get("delay_minutes")),
                "pedestrian_ready_sentri_lanes_open": clean_value(pedestrian_ready_sentri.get("lanes_open")),
                "pedestrian_ready_sentri_update_time": clean_value(pedestrian_ready_sentri.get("update_time")),
                "full_xml": port,
            }

            if item["port_name"] == "Nogales":
                print("🧪 Debug Nogales:", {
                    "passenger_ready_delay": item["passenger_ready_delay_minutes"],
                    "passenger_ready_lanes": item["passenger_ready_lanes_open"],
                    "passenger_ready_update": item["passenger_ready_update_time"]
                })

            # Normalize empty strings to None
            item = {k: (v if v not in ("", None) else None) for k, v in item.items()}

            # Log if important delay or lane data is missing
            if any(v is None for k, v in item.items() if "delay" in k or "lanes_open" in k):
                print(f"⚠️ Incomplete data for {item['port_name']}: {[(k, v) for k, v in item.items() if v is None]}")

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