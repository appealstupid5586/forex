from __future__ import annotations


class IdentityManager:
    def __init__(self):
        self.name = "identity"

    def load_config(self):
        return {"system_name": "TUNGNS Copilot OS"}
