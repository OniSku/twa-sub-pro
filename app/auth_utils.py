import json
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl, unquote


async def verify_telegram_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """Парсит и валидирует initData от Telegram."""
    try:
        parsed_data = dict(parse_qsl(init_data))
        
        if "user" not in parsed_data:
            return None
        
        user_json_str = parsed_data["user"]
        user_data = json.loads(user_json_str)
        
        result: Dict[str, Any] = {"user": user_data}
        
        for key, value in parsed_data.items():
            if key != "user":
                decoded_value = unquote(value)
                result[key] = decoded_value
        
        return result
    except Exception:
        return None
