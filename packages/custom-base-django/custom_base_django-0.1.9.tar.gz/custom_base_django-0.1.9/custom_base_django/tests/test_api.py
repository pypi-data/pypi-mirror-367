import asyncio
import aiohttp
import time
import json
from typing import Callable, List, Dict, Any


async def get_token_for_user(auth_url: str, username: str, password: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(auth_url, json={"username": username, "password": password}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("access_token") or data.get("token")
                else:
                    print(f"[Auth] Failed for {username}: Status {resp.status}")
        except Exception as e:
            print(f"[Auth] Error for {username}: {e}")
    return None


async def generate_users_with_tokens(auth_url: str, user_credentials: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    users = []
    for user in user_credentials:
        token = await get_token_for_user(auth_url, user["username"], user["password"])
        if token:
            users.append({
                "username": user["username"],
                "token": token
            })
        else:
            print(f"❌ Token not retrieved for {user['username']}")
    return users


async def stress_test_api(
    user_credentials: List[Dict[str, str]],
    auth_url: str,
    method: str,
    target_url: str,
    requests_per_user: int,
    param_generator: Callable[[Dict[str, Any], int], Dict[str, Any]],
    output_path: str=None,  # ← مسیر فایل جیسون
):
    start_time = time.time()
    method = method.upper()
    users = await generate_users_with_tokens(auth_url, user_credentials)

    results = []

    async def simulate_user(user_id: int, user_data: Dict[str, Any], session: aiohttp.ClientSession):
        headers = {
            "Authorization": f"Bearer {user_data['token']}",
            "Content-Type": "application/json"
        }

        for i in range(requests_per_user):
            request_info = {
                "user_id": user_id,
                "username": user_data["username"],
                "request_index": i,
                "method": method,
                "url": target_url,
                "status": None,
                "duration_ms": None,
                "error": None
            }

            try:
                payload = param_generator(user_data, i) or {}
                params = payload.get("params", {})
                json_body = payload.get("json", {})

                t0 = time.time()
                if method == 'GET':
                    async with session.get(target_url, params=params, headers=headers) as resp:
                        request_info["status"] = resp.status
                elif method == 'POST':
                    async with session.post(target_url, params=params, json=json_body, headers=headers) as resp:
                        request_info["status"] = resp.status
                else:
                    request_info["error"] = f"Unsupported method: {method}"
                    print(f"[User {user_id}] Unsupported method: {method}")
                t1 = time.time()

                request_info["duration_ms"] = round((t1 - t0) * 1000, 2)
                print(f"[User {user_id}] {method} {request_info['status']} in {request_info['duration_ms']} ms")

            except Exception as e:
                request_info["error"] = str(e)
                print(f"[User {user_id}] Error: {e}")

            results.append(request_info)

    connector = aiohttp.TCPConnector(limit=len(users) * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [simulate_user(i + 1, user, session) for i, user in enumerate(users)]
        await asyncio.gather(*tasks)

    duration = time.time() - start_time
    print(f"\n✅ Completed {len(users) * requests_per_user} requests in {duration:.2f} seconds.")

    # ذخیره نتایج در فایل JSON
    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📁 Results saved to '{output_path}'.")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")


if __name__ == "__main__":
    async def main():
        user_credentials = [
            {"username": "ali", "password": "123456"}
        ]

        def generate_params(user, request_index):
            return {
                "params": {},
                "json": {},
            }

        # ← گرفتن مسیر فایل از کاربر
        output_path = None #input("Enter path to save results JSON file (e.g., stress_test_results.json): ").strip()


        await stress_test_api(
            user_credentials=user_credentials,
            auth_url="http://127.0.0.1:2020/api2/token/",
            method="GET",
            target_url="http://127.0.0.1:2020/products/",
            requests_per_user=5000,
            param_generator=generate_params,
            output_path=output_path
        )

    asyncio.run(main())
