import requests

def main():
    try:
        r = requests.post("https://border-wait-times.onrender.com/record-wait-times")
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()