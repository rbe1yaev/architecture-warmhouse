import random

import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime, timezone

SENSOR_TO_LOCATION: dict[str, str] = {
    "1": "Living Room",
    "2": "Bedroom",
    "3": "Kitchen",
}

LOCATION_TO_SENSOR: dict[str, str] = {v: k for k, v in SENSOR_TO_LOCATION.items()}

TEMPERATURE_RANGES: dict[str, tuple[float, float]] = {
    "Living Room": (19.0, 25.0),
    "Bedroom": (17.0, 23.0),
    "Kitchen": (20.0, 28.0),
    "Unknown": (15.0, 30.0),
}

SENSOR_DESCRIPTIONS: dict[str, str] = {
    "Living Room": "Temperature sensor in the living room",
    "Bedroom": "Temperature sensor in the bedroom",
    "Kitchen": "Temperature sensor in the kitchen",
    "Unknown": "Temperature sensor in unknown location",
}

app = FastAPI(
    title="Temperature API",
    description="Имитация удалённого датчика температуры.",
    version="1.0.0"
)


class TemperatureResponse(BaseModel):
    sensor_id: str
    location: str
    value: float
    unit: str
    timestamp: str
    status: str
    sensor_type: str
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sensor_id": "1",
                    "location": "Living Room",
                    "value": 22.4,
                    "unit": "celsius",
                    "timestamp": "2024-11-01T10:00:00Z",
                    "status": "active",
                    "sensor_type": "temperature",
                    "description": "Temperature sensor in the living room",
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str


def resolve_location_and_sensor(
        location: str,
        sensor_id: str,
) -> tuple[str, str]:
    if sensor_id and not location:
        location = SENSOR_TO_LOCATION.get(sensor_id, "Unknown")

    if location and not sensor_id:
        sensor_id = LOCATION_TO_SENSOR.get(location, "0")

    if not location:
        location = "Unknown"
    if not sensor_id:
        sensor_id = "0"

    return location, sensor_id


def get_random_temperature(location: str) -> float:
    low, high = TEMPERATURE_RANGES.get(location, (15.0, 30.0))
    return round(random.uniform(low, high), 1)


@app.get(
    "/temperature",
    response_model=TemperatureResponse,
    summary="Получить температуру по локации или идентификатору датчика",
    tags=["Температура"],
)
async def get_temperature(
        location: str = Query(
            default="",
            description="Название комнаты: Living Room, Bedroom, Kitchen",
            example="Living Room",
        ),
        sensorId: str = Query(
            default="",
            description="Идентификатор датчика: 1, 2, 3",
            example="1",
        ),
):
    resolved_location, resolved_sensor_id = resolve_location_and_sensor(
        location=location,
        sensor_id=sensorId,
    )

    value = get_random_temperature(resolved_location)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    return TemperatureResponse(
        sensor_id=resolved_sensor_id,
        location=resolved_location,
        value=value,
        unit="celsius",
        timestamp=timestamp,
        status="active",
        sensor_type="temperature",
        description=SENSOR_DESCRIPTIONS.get(resolved_location, "Temperature sensor"),
    )


@app.get(
    "/sensors",
    summary="Получить список датчиков",
    tags=["Датчики"],
)
async def get_sensors():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT sensor_id, location, status, last_updated
            FROM sensors
            ORDER BY sensor_id
            """
        )

    return {
        "items": [
            {
                "sensor_id": LOCATION_TO_SENSOR.get(row["location"], "0"),
                "location": row["location"],
                "sensor_type": "temperature",
                "status": row["status"],
                "last_updated": row["last_updated"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "temperature_range": {
                    "min": TEMPERATURE_RANGES.get(row["location"], (15.0, 30.0))[0],
                    "max": TEMPERATURE_RANGES.get(row["location"], (15.0, 30.0))[1],
                    "unit": "celsius",
                },
            }
            for row in rows
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
