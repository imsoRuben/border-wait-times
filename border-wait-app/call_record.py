import requests

def main():
    try:
        r = requests.post("https://border-wait-times.onrender.com/record-wait-times")
        try:
            data = r.json()
        except ValueError:
            data = r.text
        print(f"Status: {r.status_code}, Response: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()