from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_airports() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "airports.csv")


def load_routes() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "routes.csv")


def load_pricing_rules() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "pricing_rules.csv")


def get_airport_by_code(code: str) -> dict | None:
    airports_df = load_airports()
    airport = airports_df[airports_df["airport_code"] == code.upper()]

    if airport.empty:
        return None

    return airport.iloc[0].to_dict()


def get_region_by_airport_code(code: str) -> str | None:
    airport = get_airport_by_code(code)
    if not airport:
        return None
    return airport["region"]


def get_pricing_rule(origin_region: str, destination_region: str) -> dict | None:
    pricing_df = load_pricing_rules()

    rule = pricing_df[
        (pricing_df["origin_region"] == origin_region)
        & (pricing_df["destination_region"] == destination_region)
    ]

    if rule.empty:
        return None

    return rule.iloc[0].to_dict()