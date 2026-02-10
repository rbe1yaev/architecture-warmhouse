import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from warmhouse.ms_auth.depends.dependencies import get_db
from warmhouse.ms_device.dto.device import DeviceResponse, DeviceCreate, DeviceUpdate, DeviceCommand

router = APIRouter(prefix="/devices")

@router.get("", response_model=List[DeviceResponse])
async def get_devices(
        pool=Depends(get_db),
        device_type: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
):
    query = "SELECT * FROM devices"
    conditions = []
    params = []
    idx = 1

    if device_type:
        conditions.append(f"device_type = ${idx}")
        params.append(device_type)
        idx += 1

    if location:
        conditions.append(f"location = ${idx}")
        params.append(location)
        idx += 1

    if status:
        conditions.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
    params.extend([limit, skip])

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str,  pool=Depends(get_db),):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM devices WHERE id = $1", device_id)
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
        return dict(row)


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(device: DeviceCreate,  pool=Depends(get_db)):
    device_id = str(uuid.uuid4())
    now = datetime.utcnow()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO devices (id, name, device_type, status, location, configuration, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, device_id, device.name, device.device_type.value, "offline",
                           device.location, json.dumps(device.configuration or {}),
                           json.dumps(device.metadata or {}), now, now)

    return {
        "id": device_id,
        "name": device.name,
        "device_type": device.device_type,
        "status": "offline",
        "location": device.location,
        "configuration": device.configuration or {},
        "metadata": device.metadata or {},
        "created_at": now,
        "updated_at": now,
        "last_seen": None
    }


@router.patch("/devices/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: str, update: DeviceUpdate, pool=Depends(get_db), ):
    async with pool.acquire() as conn:
        # Проверяем существование устройства
        existing = await conn.fetchrow("SELECT * FROM devices WHERE id = $1", device_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Device not found")
        updates = []
        values = []
        idx = 1

        update_dict = update.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field in ["configuration", "metadata"] and value is not None:
                updates.append(f"{field} = ${idx}")
                values.append(json.dumps(value))
            elif value is not None:
                updates.append(f"{field} = ${idx}")
                values.append(value)
            idx += 1

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(device_id)
        values.append(datetime.utcnow())

        query = f"""
            UPDATE devices 
            SET {', '.join(updates)}, updated_at = ${idx}
            WHERE id = ${idx + 1}
            RETURNING *
        """

        updated = await conn.fetchrow(query, *values)
        return dict(updated)


@router.post("/devices/{device_id}/command")
async def send_command(device_id: str, command: DeviceCommand, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        device = await conn.fetchrow("SELECT * FROM devices WHERE id = $1", device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        await conn.execute(
            "UPDATE devices SET status = 'online', last_seen = $1 WHERE id = $2",
            datetime.utcnow(), device_id
        )

    data = {
        "command": command.command,
        "parameters": command.parameters,
        "priority": command.priority
    }
    #! todo send to external api device

    return {
        "command_id": str(uuid.uuid4()),
        "status": "accepted",
        "message": f"Command '{command.command}' sent to device {device_id}"
    }
