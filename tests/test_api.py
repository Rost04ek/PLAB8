import pytest
from httpx import ASGITransport, AsyncClient
from task_manager.api import app

@pytest.mark.asyncio
async def test_create_and_get_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        task_payload = {
            "title": "Fix network timeout",
            "description": "Configure retry policy",
            "status": "todo",
            "priority": "high",
            "due_date": "2026-11-01T12:00:00",
        }
        res_create = await ac.post("/tasks", json=task_payload)
        assert res_create.status_code == 201
        data = res_create.json()
        assert data["title"] == "Fix network timeout"
        task_id = data["id"]

        res_get = await ac.get(f"/tasks/{task_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == task_id


@pytest.mark.asyncio
async def test_update_and_delete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        task_payload = {
            "title": "Documentation",
            "status": "todo",
            "priority": "low",
            "due_date": "2026-12-01T10:00:00",
        }
        task = (await ac.post("/tasks", json=task_payload)).json()
        task_id = task["id"]

        patch_res = await ac.patch(f"/tasks/{task_id}", json={"status": "done"})
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "done"

        del_res = await ac.delete(f"/tasks/{task_id}")
        assert del_res.status_code == 204

        get_res = await ac.get(f"/tasks/{task_id}")
        assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_pydantic_validation_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        invalid_payload = {
            "title": "A",
            "status": "invalid_status",
            "due_date": "2026-11-01T12:00:00",
        }
        response = await ac.post("/tasks", json=invalid_payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_statistics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/tasks", json={
            "title": "Task 1",
            "status": "done",
            "priority": "low",
            "due_date": "2026-12-01T10:00:00",
        })
        await ac.post("/tasks", json={
            "title": "Task 2",
            "status": "todo",
            "priority": "high",
            "due_date": "2020-01-01T10:00:00",  # Overdue
        })

        stat_res = await ac.get("/tasks/statistics")
        assert stat_res.status_code == 200
        stats = stat_res.json()
        assert stats["total"] == 2
        assert stats["completed"] == 1
        assert stats["pending"] == 1
        assert stats["overdue"] == 1
