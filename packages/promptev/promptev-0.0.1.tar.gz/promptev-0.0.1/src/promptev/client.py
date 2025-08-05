from typing import Dict, Optional, List
from dataclasses import dataclass
import threading
import time
import httpx

try:
    from cachetools import TTLCache
except ImportError:
    TTLCache = None


@dataclass
class Prompt:
    prompt: str
    variables: List[str]

    def format(self, values: Optional[Dict[str, str]] = None) -> str:
        formatted = self.prompt
        if values is None:
            values = {}

        required = self.variables or []
        if not required:
            return formatted

        missing = [v for v in required if v not in values]
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        for key, val in values.items():
            formatted = formatted.replace(f"{{{{{key}}}}}", str(val))

        return formatted


class PromptevClient:
    def __init__(
        self,
        project_key: str,
        base_url: str = "https://api.promptev.ai",
        refresh_interval: int = 30
    ):
        self.project_key = project_key
        self.base_url = base_url.rstrip("/")
        self.refresh_interval = refresh_interval
        self.is_ready = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.prompt_cache: Dict[str, Prompt] = {}
        if TTLCache:
            self.prompt_cache = TTLCache(maxsize=1000, ttl=3600)

        self._start_background_refresh()
        self.is_ready = True

    def _start_background_refresh(self):
        def _loop():
            while not self._stop_event.is_set():
                time.sleep(self.refresh_interval)
                # Future: Add cache refresh logic
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def dispose(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if hasattr(self.prompt_cache, "clear"):
            self.prompt_cache.clear()

    def _fetch_prompt_sync(self, prompt_key: str) -> Prompt:
        url = f"{self.base_url}/api/sdk/v1/prompt/client/{self.project_key}/{prompt_key}"
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        variables = data.get("variables", [])
        if isinstance(variables, str):
            variables = [v.strip() for v in variables.split(",") if v.strip()]
        return Prompt(prompt=data["prompt"], variables=variables)

    def get_prompt(self, prompt_key: str, values: Optional[Dict[str, str]] = None) -> str:
        if prompt_key in self.prompt_cache:
            prompt = self.prompt_cache[prompt_key]
            return prompt.format(values) if prompt.variables else prompt.prompt

        prompt = self._fetch_prompt_sync(prompt_key)
        self.prompt_cache[prompt_key] = prompt
        return prompt.format(values) if prompt.variables else prompt.prompt

    async def aget_prompt(self, prompt_key: str, values: Optional[Dict[str, str]] = None) -> str:
        if prompt_key in self.prompt_cache:
            prompt = self.prompt_cache[prompt_key]
            return prompt.format(values) if prompt.variables else prompt.prompt

        url = f"{self.base_url}/api/sdk/v1/prompt/client/{self.project_key}/{prompt_key}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        variables = data.get("variables", [])
        if isinstance(variables, str):
            variables = [v.strip() for v in variables.split(",") if v.strip()]
        prompt = Prompt(prompt=data["prompt"], variables=variables)
        self.prompt_cache[prompt_key] = prompt
        return prompt.format(values) if prompt.variables else prompt.prompt

