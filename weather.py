"""
/api/weather — Weather-aware farming advice using FAISS + IBM watsonx.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.rag_service import retrieve, format_context
from app.services.ibm_service import ask_watsonx

router = APIRouter()

WEATHER_INSTRUCTIONS = """
You are a weather-aware farming advisor. Given the weather and crop info:
1. Assess weather impact on the crop at its current stage
2. Give specific advice on irrigation, spraying, harvesting windows
3. Warn about disease risk (high humidity = fungal risk, etc.)
4. If wind > 15 km/h: advise against spraying
5. Give day-by-day recommendations if forecast is provided
Keep advice practical and time-sensitive.
"""


class WeatherData(BaseModel):
    temperature_c:      Optional[float] = None
    humidity_percent:   Optional[float] = None
    rainfall_mm:        Optional[float] = None
    wind_speed_kmh:     Optional[float] = None
    condition:          Optional[str]   = Field(default=None, description="sunny/cloudy/rainy/foggy/stormy")
    forecast_next_days: Optional[str]   = Field(default=None, description="e.g. '3 days of rain expected'")


class WeatherRequest(BaseModel):
    crop:             str              = Field(..., description="Crop name")
    crop_stage:       Optional[str]   = Field(default=None, description="seedling/vegetative/flowering/fruiting/harvest-ready")
    planned_activity: Optional[str]   = Field(default=None, description="What you plan to do today")
    location:         Optional[str]   = Field(default=None, description="State or region")
    weather:          WeatherData
    language:         str             = Field(default="en")


class WeatherResponse(BaseModel):
    crop:          str
    advice:        str
    sources:       list[str]
    language_used: str
    mode:          str


@router.post("/advice", response_model=WeatherResponse, summary="Get weather-based crop advice")
def weather_advice(req: WeatherRequest):
    """
    Get farming advice tailored to current weather conditions.
    Handles irrigation decisions, spray timing, frost/heat alerts, harvest windows.
    """
    w = req.weather
    weather_parts = []
    if w.condition:          weather_parts.append(f"Condition: {w.condition}")
    if w.temperature_c:      weather_parts.append(f"Temp: {w.temperature_c}°C")
    if w.humidity_percent:   weather_parts.append(f"Humidity: {w.humidity_percent}%")
    if w.rainfall_mm:        weather_parts.append(f"Rainfall: {w.rainfall_mm}mm")
    if w.wind_speed_kmh:     weather_parts.append(f"Wind: {w.wind_speed_kmh} km/h")
    if w.forecast_next_days: weather_parts.append(f"Forecast: {w.forecast_next_days}")

    search_query = f"{req.crop} {req.planned_activity or 'farming advice'} weather {w.condition or ''}"
    results = retrieve(search_query)
    context = format_context(results)
    sources = list({src for _, src, _ in results})

    parts = [f"Crop: {req.crop}"]
    if req.crop_stage:       parts.append(f"Stage: {req.crop_stage}")
    if req.location:         parts.append(f"Location: {req.location}")
    if req.planned_activity: parts.append(f"Planned activity: {req.planned_activity}")
    parts.append("Weather: " + " | ".join(weather_parts))
    parts.append("What should I do for my crop today?")

    result = ask_watsonx(
        user_message="\n".join(parts),
        context=context,
        language=req.language,
        extra_instructions=WEATHER_INSTRUCTIONS,
    )

    return WeatherResponse(
        crop=req.crop,
        advice=result["answer"],
        sources=sources,
        language_used=result["language_used"],
        mode=result["source"],
    )
