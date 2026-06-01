import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Wczytaj klucz API z .env
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def load_cities():
    """Wczytuje miasta z pliku CSV"""
    df = pd.read_csv("cities.csv")
    return df


def show_cities(df):
    """Wyświetla listę miast z numerami"""
    print("\n=== Dostępne miasta ===\n")
    for _, row in df.iterrows():
        print(f"{row['id']:>3}. {row['city']} ({row['country']})")
    print()


def get_weather(city):
    """Pobiera pogodę dla jednego miasta"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pl"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code != 200:
        print(f"  Błąd dla {city}: {data.get('message', 'nieznany błąd')}")
        return None

    return {
        "Miasto": city,
        "Kraj": data["sys"]["country"],
        "Temperatura (°C)": round(data["main"]["temp"], 1),
        "Odczuwalna (°C)": round(data["main"]["feels_like"], 1),
        "Wilgotność (%)": data["main"]["humidity"],
        "Wiatr (m/s)": data["wind"]["speed"],
        "Opis": data["weather"][0]["description"].capitalize()
    }


def save_results(results):
    """Zapisuje wyniki do CSV i Excel"""
    df = pd.DataFrame(results)

    os.makedirs("data", exist_ok=True)

    # CSV
    df.to_csv("data/pogoda.csv", index=False, encoding="utf-8-sig")
    print("\nZapisano do data/pogoda.csv")

    # Excel
    with pd.ExcelWriter("data/pogoda.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Pogoda", index=False)
        ws = writer.sheets["Pogoda"]
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 8
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 18
        ws.column_dimensions["E"].width = 16
        ws.column_dimensions["F"].width = 14
        ws.column_dimensions["G"].width = 25
    print("Zapisano do data/pogoda.xlsx")

    return df


def main():
    print("=== Weather ETL Pipeline ===")

    # 1. Wczytaj miasta z CSV
    cities_df = load_cities()

    # 2. Pokaż listę miast
    show_cities(cities_df)

    # 3. Użytkownik wybiera numery miast
    wybor = input("Wpisz numery miast oddzielone przecinkami (np. 1,3,5): ")
    numery = [int(x.strip()) for x in wybor.split(",")]

    # 4. Filtruj wybrane miasta
    wybrane = cities_df[cities_df["id"].isin(numery)]

    if wybrane.empty:
        print("Nie wybrano żadnych miast!")
        return

    print(f"\nPobieram pogodę dla {len(wybrane)} miast...\n")

    # 5. Pobierz pogodę dla każdego wybranego miasta
    results = []
    for _, row in wybrane.iterrows():
        print(f"  {row['city']}...")
        weather = get_weather(row["city"])
        if weather:
            results.append(weather)

    if not results:
        print("Brak danych pogodowych!")
        return

    # 6. Zapisz i wyświetl wyniki
    df = save_results(results)

    print("\n=== WYNIKI ===\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()