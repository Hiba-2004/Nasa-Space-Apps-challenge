import json
from pathlib import Path

from backend.app.main import app

target = Path(__file__).parents[1] / "contracts" / "openapi.json"
target.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"Wrote {target}")

