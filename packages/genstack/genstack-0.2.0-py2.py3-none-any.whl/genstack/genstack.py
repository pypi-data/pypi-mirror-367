import httpx
from typing import Dict, Any, Optional, Union
import asyncio

class Genstack:
    def __init__(self, api_key: str, base_url : Optional[str] = "https://host.fly.dev", admin_url : Optional[str] = None):
        if not api_key.startswith("gen-") or any(c.isspace() for c in api_key):
            raise ValueError("API key must start with 'gen-' and contain no spaces or line breaks.")
        self.api_key : str = api_key
        resolved_base_url = admin_url or base_url
        if resolved_base_url is None:
            raise ValueError("A base URL must be provided.")
        self.base_url: str = resolved_base_url
    async def __call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            try:
                response = await client.post(
                    url=f"{self.base_url}/api/v1/sdk/generate",
                    headers={
                        "x-api-key" : f"{self.api_key}"
                    },
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return e.response.json()
            except Exception as e:
                return {"error" : str(e)}
    async def __generate_async(self, payload : Dict[str, Any]) -> Dict[str, Any]:
        return await self.__call(payload=payload)
    def __extract_first_text(self, result: dict) -> str:
        for o in result.get("output", []):
            if o.get("output", {}).get("type") == "TEXT":
                return o["output"].get("text", "")
        return ""
    def generate(self, input : Union[str, Dict[str, Any]], model : Optional[str] = "auto", track : Optional[str] = None) -> Dict[str, Any]:
        if not track :
            raise ValueError("Track is required.")
        if not isinstance(input, (str, dict)):
            raise TypeError("Payload must be a string or a dictionary.")
        if isinstance(input, str):
            inner_payload = {"input": input}
        else:
            inner_payload = input

        payload = {
            "payload": inner_payload,
            "model": model,
            "track": track
        }
        return asyncio.run(self.__generate_async(payload=payload))
    def get_output_text(self, input: Union[str, Dict[str, Any]], model: Optional[str] = "auto", track: Optional[str] = None) -> str:
        result = self.generate(input=input, model=model, track=track)
        first_text : str = self.__extract_first_text(result)
        return first_text