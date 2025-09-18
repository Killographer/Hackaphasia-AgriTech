from __future__ import annotations

from dataclasses import dataclass
import os
from typing import List, Dict, Optional, Any

import numpy as np
import pandas as pd


@dataclass
class Recommendation:
    crop: str
    score: float
    expected_yield_t_ha: float
    expected_revenue_per_ha: float
    area_share_pct: float


def _scale_01(value: float, min_v: float, max_v: float) -> float:
    if max_v == min_v:
        return 0.0
    return float(np.clip((value - min_v) / (max_v - min_v), 0.0, 1.0))


def compute_scores(
    region: str,
    season: str,
    crops_df: pd.DataFrame,
    soil_df: pd.DataFrame,
    climate_df: pd.DataFrame,
    regions_df: pd.DataFrame,
    market_df: pd.DataFrame | None = None,
    diversity_weight: float = 0.15,
    soil_override: Optional[Dict[str, Any]] = None,
    extra_rain_mm: float = 0.0,
) -> pd.DataFrame:
    soil = soil_df.loc[soil_df["region"] == region].iloc[0].copy()
    climate = climate_df.loc[(climate_df["region"] == region) & (climate_df["season"] == season)].iloc[0].copy()
    region_row = regions_df.loc[regions_df["region"] == region].iloc[0]

    # apply optional user overrides
    if soil_override is not None:
        if "ph" in soil_override and soil_override["ph"] is not None:
            soil["ph"] = float(soil_override["ph"])
        if "drainage" in soil_override and soil_override["drainage"]:
            soil["drainage"] = str(soil_override["drainage"])  # expected values: poor/moderate/well
        if "organic_matter_pct" in soil_override and soil_override["organic_matter_pct"] is not None:
            soil["organic_matter_pct"] = float(soil_override["organic_matter_pct"])
    if extra_rain_mm:
        climate["forecast_rain_mm"] = float(climate["forecast_rain_mm"]) + float(extra_rain_mm)

    def ph_fit(row: pd.Series) -> float:
        ideal_min, ideal_max = row["ideal_ph_min"], row["ideal_ph_max"]
        if soil["ph"] < ideal_min:
            return _scale_01(soil["ph"], ideal_min - 1.5, ideal_min)
        if soil["ph"] > ideal_max:
            return _scale_01(ideal_max, ideal_max, soil["ph"] + 1.5)
        # inside range → closer to center is better
        center = (ideal_min + ideal_max) / 2.0
        half = (ideal_max - ideal_min) / 2.0
        if half == 0:
            return 0.0
        return 1.0 - abs(soil["ph"] - center) / half

    def drainage_fit(row: pd.Series) -> float:
        pref = row["drainage_pref"]
        actual = soil["drainage"]
        if pref == actual:
            return 1.0
        if {pref, actual} == {"moderate", "well"}:
            return 0.7
        if {pref, actual} == {"moderate", "poor"}:
            return 0.6
        return 0.4

    def water_fit(row: pd.Series) -> float:
        need = float(row["water_need_mm"])
        have = float(climate["forecast_rain_mm"])
        # linear penalty for mismatch
        ratio = have / max(need, 1.0)
        if ratio >= 1:
            return _scale_01(min(ratio, 1.5), 1.0, 1.5)
        return _scale_01(ratio, 0.4, 1.0)

    def temp_fit(row: pd.Series) -> float:
        t = float(climate["forecast_temp_c"])
        tmin, tmax = float(row["heat_tolerance_c_min"]), float(row["heat_tolerance_c_max"])
        if t < tmin:
            return _scale_01(t, tmin - 10, tmin)
        if t > tmax:
            return _scale_01(tmax, tmax, t + 10)
        center = (tmin + tmax) / 2.0
        half = (tmax - tmin) / 2.0
        if half == 0:
            return 0.0
        return 1.0 - abs(t - center) / half

    def market_fit(row: pd.Series) -> float:
        price = float(row["price_per_ton"]) * float(region_row["market_index"])
        # demand-supply adjustment (if provided)
        pressure = 1.0
        if market_df is not None:
            mrow = market_df.loc[(market_df["region"] == region) & (market_df["crop"] == row["crop"])].head(1)
            if not mrow.empty:
                demand = float(mrow.iloc[0]["demand_index"])  # higher is better
                supply = float(mrow.iloc[0]["supply_index"])  # higher reduces margin
                # price pressure factor: sigmoid of demand/supply ratio
                ratio = demand / max(supply, 1e-6)
                pressure = 1.0 / (1.0 + np.exp(-(ratio - 1.0) * 2.0))  # 0..1
        # scale price among available crops, then modulate by pressure
        pmin, pmax = crops_df["price_per_ton"].min(), crops_df["price_per_ton"].max()
        return _scale_01(price, pmin, pmax) * pressure

    df = crops_df.copy()
    df["soil_ph_score"] = df.apply(ph_fit, axis=1)
    df["drainage_score"] = df.apply(drainage_fit, axis=1)
    df["water_score"] = df.apply(water_fit, axis=1)
    df["temp_score"] = df.apply(temp_fit, axis=1)
    df["market_score"] = df.apply(market_fit, axis=1)

    # base suitability: emphasize agronomy, then market
    df["base_score"] = (
        0.25 * df["soil_ph_score"]
        + 0.20 * df["drainage_score"]
        + 0.20 * df["water_score"]
        + 0.20 * df["temp_score"]
        + 0.15 * df["market_score"]
    )

    # diversity encouragement: reduce score if many in same group later
    # We will compute area shares after ranking and then apply a group penalty
    return df


def diversify_portfolio(
    scored_df: pd.DataFrame,
    max_crops: int = 5,
    group_min_spread: float = 0.15,
    diversity_weight: float = 0.15,
) -> List[Recommendation]:
    df = scored_df.sort_values("base_score", ascending=False).head(max_crops).reset_index(drop=True)

    # initial area shares proportional to score
    weights = df["base_score"].to_numpy()
    if weights.sum() == 0:
        weights = np.ones_like(weights)
    shares = weights / weights.sum()

    # encourage group diversity by capping per-group dominance
    groups = df["group"].tolist()
    for _ in range(3):
        group_totals: Dict[str, float] = {}
        for g, s in zip(groups, shares):
            group_totals[g] = group_totals.get(g, 0.0) + float(s)
        # if any group dominates, shift some area to underrepresented groups
        for i, g in enumerate(groups):
            if group_totals[g] > 0.6:  # too dominant
                excess = group_totals[g] - 0.6
                shares[i] -= excess * 0.5 / (df.shape[0])
        # ensure minimum spread across groups
        for i, g in enumerate(groups):
            shares[i] = max(shares[i], group_min_spread / len(set(groups)))
        shares = np.clip(shares, 0.01, 0.9)
        shares = shares / shares.sum()

    # compute economics
    expected_yield = df["base_yield_t_ha"].to_numpy() * (0.7 + 0.6 * df["temp_score"].to_numpy()) * (
        0.7 + 0.6 * df["water_score"].to_numpy()
    )
    region_price = df["price_per_ton"].to_numpy()
    expected_revenue = expected_yield * region_price

    results: List[Recommendation] = []
    for i, row in df.iterrows():
        results.append(
            Recommendation(
                crop=str(row["crop"]),
                score=float(row["base_score"]),
                expected_yield_t_ha=float(expected_yield[i]),
                expected_revenue_per_ha=float(expected_revenue[i]),
                area_share_pct=float(shares[i] * 100.0),
            )
        )
    return results


def load_data(base_path: str) -> Dict[str, pd.DataFrame]:
    crops = pd.read_csv(f"{base_path}/data/crops.csv")
    regions = pd.read_csv(f"{base_path}/data/regions.csv")
    soil = pd.read_csv(f"{base_path}/data/soil.csv")
    climate = pd.read_csv(f"{base_path}/data/climate.csv")
    market_path = f"{base_path}/data/market.csv"
    market = pd.read_csv(market_path) if os.path.exists(market_path) else None
    return {"crops": crops, "regions": regions, "soil": soil, "climate": climate, "market": market}


# Simple, rule-based disease risk assessment per crop using climate/soil
def disease_warnings_for_crop(
    crop: str,
    region: str,
    season: str,
    soil_row: pd.Series,
    climate_row: pd.Series,
    irrigation: str = "rainfed",
    user_flags: Optional[Dict[str, bool]] = None,
) -> List[Dict[str, str]]:
    warnings: List[Dict[str, str]] = []
    user_flags = user_flags or {}
    t = float(climate_row["forecast_temp_c"]) if "forecast_temp_c" in climate_row else 25.0
    r = float(climate_row["forecast_rain_mm"]) if "forecast_rain_mm" in climate_row else 600.0
    drainage = str(soil_row.get("drainage", "moderate"))

    def add(name: str, risk: str, tips: str) -> None:
        warnings.append({"disease": name, "risk": risk, "prevention": tips})

    # Rice
    if crop.lower() == "rice":
        if r > 800 or irrigation in ("canal/well", "drip"):
            add(
                "Blast/Blight",
                "medium-high",
                "Use resistant varieties, balanced N, ensure field sanitation; prophylactic tricyclazole in endemic areas.",
            )
        if drainage == "poor":
            add(
                "Sheath rot",
                "medium",
                "Improve drainage, avoid excess N, ensure proper spacing; remove infected debris.",
            )
    # Cotton
    if crop.lower() == "cotton":
        if t > 27 and 500 <= r <= 900:
            add(
                "Bollworm/Whitefly",
                "medium",
                "Use trap crops, timely sowing, pheromone traps; rotate insecticides; maintain field hygiene.",
            )
        if drainage == "poor":
            add(
                "Root rot",
                "medium",
                "Improve drainage, seed treat with Trichoderma, avoid waterlogging.",
            )
    # Groundnut
    if crop.lower() == "groundnut":
        if r > 600 or drainage != "well":
            add(
                "Leaf spot/Rust",
                "medium",
                "Use disease-free seed, seed treat with fungicide, ensure 15–20 cm spacing; avoid overhead irrigation.",
            )
    # Chickpea
    if crop.lower() == "chickpea":
        if t < 20 and r > 350:
            add(
                "Wilt/Rust",
                "medium",
                "Use resistant varieties, seed treat with Trichoderma, avoid early sowing in wet fields.",
            )
    # Maize/Sorghum/Millets
    if crop.lower() in ("maize", "sorghum", "millet"):
        if r > 500:
            add(
                "Downy mildew",
                "medium",
                "Treat seed (metalaxyl/Thiram as per local guidance), ensure field sanitation; avoid dense canopy.",
            )
    # Vegetables/Fruits generic
    if crop.lower() in ("vegetables", "fruits"):
        if r > 600:
            add(
                "Fungal foliar diseases",
                "medium",
                "Mulch to reduce splash, prune for airflow, copper-based preventives per label in humid periods.",
            )

    # user flags
    if user_flags.get("saved_seed", False):
        add("Seed-borne issues", "medium", "Prefer certified seed; hot water treatment where applicable.")
    if user_flags.get("flood_prone", False):
        add("Waterlogging stress", "high", "Raised beds, drainage channels, avoid sensitive crops in monsoon.")

    return warnings


