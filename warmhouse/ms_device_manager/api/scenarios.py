import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from warmhouse.ms_device_manager.depends.dependencies import get_db
from warmhouse.ms_device_manager.dto.scenarios import ScenarioCreate
from warmhouse.ms_device_manager.services.scenarios import execute_scenario_async

router = APIRouter(prefix="/scenarios")

logger = logging.getLogger(__name__)


@router.get("")
async def get_scenarios(db_pool=Depends(get_db), enabled: Optional[bool] = None):
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM scenarios"
        params = []

        if enabled is not None:
            query += " WHERE enabled = $1"
            params.append(enabled)

        query += " ORDER BY created_at DESC"

        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


@router.get("/{scenario_id}")
async def get_scenario(
    scenario_id: str,
    db_pool=Depends(get_db),
):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM scenarios WHERE id = $1", scenario_id)
        if not row:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return dict(row)


@router.post("")
async def create_scenario(
    scenario: ScenarioCreate,
    db_pool=Depends(get_db),
):
    scenario_id = str(uuid.uuid4())
    now = datetime.utcnow()

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO scenarios (id, name, description, trigger_type, cron_schedule, actions, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
            scenario_id,
            scenario.name,
            scenario.description,
            scenario.trigger_type,
            scenario.cron_schedule,
            json.dumps([action.dict() for action in scenario.actions]),
            now,
            now,
        )

    return {
        "id": scenario_id,
        "name": scenario.name,
        "description": scenario.description,
        "trigger_type": scenario.trigger_type,
        "actions": [action.dict() for action in scenario.actions],
        "created_at": now,
    }


@router.post("/{scenario_id}/execute")
async def execute_scenario(
    scenario_id: str,
    db_pool=Depends(get_db),
):
    async with db_pool.acquire() as conn:
        scenario = await conn.fetchrow("SELECT * FROM scenarios WHERE id = $1 AND enabled = TRUE", scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found or disabled")

    await execute_scenario_async(scenario_id, db_pool)
    return {
        "status": "accepted",
        "message": "Scenario execution started",
        "scenario_id": scenario_id,
        "started_at": datetime.utcnow().isoformat(),
    }
