import requests

url = "https://api.eu.platform.xweather.com/measurements/urn:dev:ops:16961-AQT530-U4130410?start_time=2024-10-10T20:00:00Z&end_time=2024-10-10T20:10:00Z"

payload={}
headers = {
  'Accept': 'application/json',
  'X-API-KEY': 'aur_prod_01J9WRDBAJ8NXQBM57QR5AMDNQ.qkW2E3tUeM7agrbmU-C0CtQ2qi7xjxDE0Pe26LekEgu7EQX8Xiy4krhVbKq3kaIV'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)