import asyncio
import httpx

async def fetch_user_tasks_with_retry(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    base_url: str,
    user_id: int,
    attempts: int = 3,
) -> list[dict]:
    url = f"{base_url}/users/{user_id}/tasks"

    async with semaphore:
        for attempt in range(1, attempts + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError):
                if attempt == attempts:
                    raise
                await asyncio.sleep(0.5 * attempt)

    raise RuntimeError("Не вдалося отримати відповідь після повторних спроб")


async def fetch_multiple_users_tasks(
    base_url: str,
    user_ids: list[int],
    max_concurrency: int = 3,
    timeout: float = 5.0,
) -> dict[int, list[dict]]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async with httpx.AsyncClient(timeout=timeout) as client:
        # Використання asyncio.Task
        tasks: list[asyncio.Task] = [
            asyncio.create_task(
                fetch_user_tasks_with_retry(client, semaphore, base_url, uid)
            )
            for uid in user_ids
        ]

        # Паралельне очікування через asyncio.gather
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return dict(zip(user_ids, results))
