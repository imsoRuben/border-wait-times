from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import os
import xmltodict
from supabase import create_client, Client

def clean_value(val):
    if val is None or isinstance(val, str) and val.strip() in ("", "N/A", "Lanes Closed"):
        return None
    return val

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider specifying allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
            passenger = port.get("passenger_vehicle_lanes", {}).get("standard_lanes", {})
            passenger_ready = port.get("passenger_vehicle_lanes", {}).get("ready_lanes", {})
            if not passenger_ready:
                print(f"⚠️ No 'passenger_ready' data for: {port.get('port_name')}")
            passenger_sentri = port.get("passenger_vehicle_lanes", {}).get("NEXUS_SENTRI_lanes", {})
            if not passenger_sentri:
                print(f"⚠️ No 'passenger_sentri' data for: {port.get('port_name')}")

            commercial = port.get("commercial_vehicle_lanes", {}).get("standard_lanes", {})
            if not commercial:
                print(f"⚠️ No 'commercial_standard' data for: {port.get('port_name')}")
            commercial_fast = port.get("commercial_vehicle_lanes", {}).get("FAST_lanes", {})
            if not commercial_fast:
                print(f"⚠️ No 'commercial_fast' data for: {port.get('port_name')}")

            pedestrian = port.get("pedestrian_lanes", {}).get("standard_lanes", {})
            if not pedestrian:
                print(f"⚠️ No 'pedestrian_standard' data for: {port.get('port_name')}")
            pedestrian_ready = port.get("pedestrian_lanes", {}).get("ready_lanes", {})
            if not pedestrian_ready:
                print(f"⚠️ No 'pedestrian_ready' data for: {port.get('port_name')}")
            pedestrian_sentri = port.get("pedestrian_lanes", {}).get("sentri_lanes", {})
            if not pedestrian_sentri:
                print(f"⚠️ No 'pedestrian_sentri' data for: {port.get('port_name')}")
            pedestrian_ready_sentri = port.get("pedestrian_lanes", {}).get("ready_sentri_lanes", {})
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
                    "passenger_standard": {
                        "delay": item["passenger_standard_delay_minutes"],
                        "lanes": item["passenger_standard_lanes_open"],
                        "update": item["passenger_standard_update_time"]
                    },
                    "passenger_ready": {
                        "delay": item["passenger_ready_delay_minutes"],
                        "lanes": item["passenger_ready_lanes_open"],
                        "update": item["passenger_ready_update_time"]
                    },
                    "passenger_sentri": {
                        "delay": item["passenger_sentri_delay_minutes"],
                        "lanes": item["passenger_sentri_lanes_open"],
                        "update": item["passenger_sentri_update_time"]
                    },
                    "commercial_standard": {
                        "delay": item["commercial_standard_delay_minutes"],
                        "lanes": item["commercial_standard_lanes_open"],
                        "update": item["commercial_standard_update_time"]
                    },
                    "commercial_fast": {
                        "delay": item["commercial_fast_delay_minutes"],
                        "lanes": item["commercial_fast_lanes_open"],
                        "update": item["commercial_fast_update_time"]
                    },
                    "pedestrian_standard": {
                        "delay": item["pedestrian_standard_delay_minutes"],
                        "lanes": item["pedestrian_standard_lanes_open"],
                        "update": item["pedestrian_standard_update_time"]
                    },
                    "pedestrian_ready": {
                        "delay": item["pedestrian_ready_delay_minutes"],
                        "lanes": item["pedestrian_ready_lanes_open"],
                        "update": item["pedestrian_ready_update_time"]
                    },
                    "pedestrian_sentri": {
                        "delay": item["pedestrian_sentri_delay_minutes"],
                        "lanes": item["pedestrian_sentri_lanes_open"],
                        "update": item["pedestrian_sentri_update_time"]
                    },
                    "pedestrian_ready_sentri": {
                        "delay": item["pedestrian_ready_sentri_delay_minutes"],
                        "lanes": item["pedestrian_ready_sentri_lanes_open"],
                        "update": item["pedestrian_ready_sentri_update_time"]
                    }
                })

            # Normalize empty strings to None (keep 0 intact)
            item = {k: (v if v not in ("", None) else None) if not isinstance(v, (int, float)) else v for k, v in item.items()}

            # Add nested lane structures for frontend
            item["passenger_vehicle_lanes"] = {
                "standard_lanes": {
                    "delay_minutes": item.pop("passenger_standard_delay_minutes"),
                    "lanes_open": item.pop("passenger_standard_lanes_open"),
                },
                "ready_lanes": {
                    "delay_minutes": item.pop("passenger_ready_delay_minutes"),
                    "lanes_open": item.pop("passenger_ready_lanes_open"),
                },
                "sentri_lanes": {
                    "delay_minutes": item.pop("passenger_sentri_delay_minutes"),
                    "lanes_open": item.pop("passenger_sentri_lanes_open"),
                },
            }
            item["commercial_vehicle_lanes"] = {
                "standard_lanes": {
                    "delay_minutes": item.pop("commercial_standard_delay_minutes"),
                    "lanes_open": item.pop("commercial_standard_lanes_open"),
                },
                "FAST_lanes": {
                    "delay_minutes": item.pop("commercial_fast_delay_minutes"),
                    "lanes_open": item.pop("commercial_fast_lanes_open"),
                },
            }
            item["pedestrian_lanes"] = {
                "standard_lanes": {
                    "delay_minutes": item.pop("pedestrian_standard_delay_minutes"),
                    "lanes_open": item.pop("pedestrian_standard_lanes_open"),
                },
                "ready_lanes": {
                    "delay_minutes": item.pop("pedestrian_ready_delay_minutes"),
                    "lanes_open": item.pop("pedestrian_ready_lanes_open"),
                },
                "sentri_lanes": {
                    "delay_minutes": item.pop("pedestrian_sentri_delay_minutes"),
                    "lanes_open": item.pop("pedestrian_sentri_lanes_open"),
                },
                "ready_sentri_lanes": {
                    "delay_minutes": item.pop("pedestrian_ready_sentri_delay_minutes"),
                    "lanes_open": item.pop("pedestrian_ready_sentri_lanes_open"),
                },
            }

            # Log if important delay or lane data is missing, with enhanced logging for which field and value
            for k, v in item.items():
                if ("delay" in k or "lanes_open" in k) and v is None:
                    print(f"⚠️ None value for {k} at port {item['port_name']}: expected a value but got None")

            known_keys = {
                "crossing_name", "port_name", "port_code", "state", "region", "hours", "border",
                "date", "time", "construction_notice", "note", "port_status",
                "passenger_vehicle_lanes", "commercial_vehicle_lanes", "pedestrian_lanes"
            }
            unknown_keys = set(port.keys()) - known_keys
            if unknown_keys:
                print(f"🔍 Unparsed keys found at {port.get('port_name')}: {unknown_keys}")

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
        ports = data.get("border_wait_time", {}).get("port", [])
        port_names = sorted({port.get("crossing_name", "Unknown") for port in ports})
        return {"available_ports": port_names}
    except Exception as e:
        return {"error": str(e)}

@app.post("/record-wait-times")
def record_wait_times():
    try:
        response = requests.get(CBP_URL)
        data = xmltodict.parse(response.content)
        ports = data.get("border_wait_time", {}).get("port", [])
        inserted = 0
        skipped = 0

        for port in ports:
            port_code = port.get("port_code")
            cbp_date = port.get("date")
            cbp_time = port.get("time")

            if not cbp_time:
                cbp_time = (
                    port.get("passenger_vehicle_lanes", {})
                        .get("standard_lanes", {})
                        .get("update_time")
                )

            # Add diagnostic logging before checking if cbp_time is None
            if cbp_time is None:
                print(f"⚠️ No cbp_time found for port: {port.get('port_name')}")
                print(f"🔎 Raw port: {port}")

            is_stale = cbp_time is None

            if is_stale:
                cbp_time = "00:00"

            # Check if entry already exists
            existing = supabase.table("border_wait_history") \
                .select("id") \
                .eq("port_code", port_code) \
                .eq("date", cbp_date) \
                .eq("time", cbp_time) \
                .execute()

            if existing.data:
                skipped += 1
                continue

            # Build initial item dict, now including full_xml for all records
            item = {
                "crossing_name": port.get("crossing_name", ""),
                "port_name": port.get("port_name", ""),
                "port_code": port_code,
                "state": port.get("state", ""),
                "region": port.get("region", ""),
                "hours": port.get("hours", ""),
                "border": port.get("border", ""),
                "date": cbp_date or None,
                "time": cbp_time,  # ensure this is set to "00:00" if cbp_time was None above
                "notice": port.get("construction_notice", ""),
                "note": port.get("note", ""),
                "port_status": port.get("port_status", ""),

                "passenger_standard_delay_minutes": clean_value(port.get("passenger_vehicle_lanes", {}).get("standard_lanes", {}).get("delay_minutes")),
                "passenger_standard_lanes_open": clean_value(port.get("passenger_vehicle_lanes", {}).get("standard_lanes", {}).get("lanes_open")),
                "passenger_standard_update_time": clean_value(port.get("passenger_vehicle_lanes", {}).get("standard_lanes", {}).get("update_time")),

                "passenger_ready_delay_minutes": clean_value(port.get("passenger_vehicle_lanes", {}).get("ready_lanes", {}).get("delay_minutes")),
                "passenger_ready_lanes_open": clean_value(port.get("passenger_vehicle_lanes", {}).get("ready_lanes", {}).get("lanes_open")),
                "passenger_ready_update_time": clean_value(port.get("passenger_vehicle_lanes", {}).get("ready_lanes", {}).get("update_time")),

                "passenger_sentri_delay_minutes": clean_value(port.get("passenger_vehicle_lanes", {}).get("NEXUS_SENTRI_lanes", {}).get("delay_minutes")),
                "passenger_sentri_lanes_open": clean_value(port.get("passenger_vehicle_lanes", {}).get("NEXUS_SENTRI_lanes", {}).get("lanes_open")),
                "passenger_sentri_update_time": clean_value(port.get("passenger_vehicle_lanes", {}).get("NEXUS_SENTRI_lanes", {}).get("update_time")),

                "commercial_standard_delay_minutes": clean_value(port.get("commercial_vehicle_lanes", {}).get("standard_lanes", {}).get("delay_minutes")),
                "commercial_standard_lanes_open": clean_value(port.get("commercial_vehicle_lanes", {}).get("standard_lanes", {}).get("lanes_open")),
                "commercial_standard_update_time": clean_value(port.get("commercial_vehicle_lanes", {}).get("standard_lanes", {}).get("update_time")),

                "commercial_fast_delay_minutes": clean_value(port.get("commercial_vehicle_lanes", {}).get("FAST_lanes", {}).get("delay_minutes")),
                "commercial_fast_lanes_open": clean_value(port.get("commercial_vehicle_lanes", {}).get("FAST_lanes", {}).get("lanes_open")),
                "commercial_fast_update_time": clean_value(port.get("commercial_vehicle_lanes", {}).get("FAST_lanes", {}).get("update_time")),

                "pedestrian_standard_delay_minutes": clean_value(port.get("pedestrian_lanes", {}).get("standard_lanes", {}).get("delay_minutes")),
                "pedestrian_standard_lanes_open": clean_value(port.get("pedestrian_lanes", {}).get("standard_lanes", {}).get("lanes_open")),
                "pedestrian_standard_update_time": clean_value(port.get("pedestrian_lanes", {}).get("standard_lanes", {}).get("update_time")),

                "pedestrian_ready_delay_minutes": clean_value(port.get("pedestrian_lanes", {}).get("ready_lanes", {}).get("delay_minutes")),
                "pedestrian_ready_lanes_open": clean_value(port.get("pedestrian_lanes", {}).get("ready_lanes", {}).get("lanes_open")),
                "pedestrian_ready_update_time": clean_value(port.get("pedestrian_lanes", {}).get("ready_lanes", {}).get("update_time")),

                "pedestrian_sentri_delay_minutes": clean_value(port.get("pedestrian_lanes", {}).get("sentri_lanes", {}).get("delay_minutes")),
                "pedestrian_sentri_lanes_open": clean_value(port.get("pedestrian_lanes", {}).get("sentri_lanes", {}).get("lanes_open")),
                "pedestrian_sentri_update_time": clean_value(port.get("pedestrian_lanes", {}).get("sentri_lanes", {}).get("update_time")),

                "pedestrian_ready_sentri_delay_minutes": clean_value(port.get("pedestrian_lanes", {}).get("ready_sentri_lanes", {}).get("delay_minutes")),
                "pedestrian_ready_sentri_lanes_open": clean_value(port.get("pedestrian_lanes", {}).get("ready_sentri_lanes", {}).get("lanes_open")),
                "pedestrian_ready_sentri_update_time": clean_value(port.get("pedestrian_lanes", {}).get("ready_sentri_lanes", {}).get("update_time")),
                "stale": is_stale,
                "full_xml": port,
            }

            # Clean values (normalize empty strings to None, but preserve "00:00" for time)
            cleaned_item = {k: (v if v not in ("", None) else None) if not isinstance(v, (int, float)) else v for k, v in item.items()}
            # Explicitly ensure time is set to cbp_time (which is "00:00" if it was None originally)
            cleaned_item["time"] = cbp_time

            if cleaned_item["time"] is None:
                cleaned_item["time"] = "00:00"
            supabase.table("border_wait_history").insert(cleaned_item).execute()
            inserted += 1

        return {"inserted": inserted, "skipped": skipped}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Starting app on port {port}")
    uvicorn.run("border_app:app", host="0.0.0.0", port=port)