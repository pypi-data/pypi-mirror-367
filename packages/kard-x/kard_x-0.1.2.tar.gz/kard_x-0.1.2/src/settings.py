# src/settings.py
import json5
from importlib import resources

class Settings:
    def __init__(self, package_path: str, filename: str):
        self.package_path = package_path
        self.filename = filename
        self.data = self._load_defaults()
        self.load()

    def _load_defaults(self) -> dict:
        return {
            "show_enemy_hand": True,
            "enable_colors": True,
            "enable_menu_animations": True,

            "animation_speed_multiplier": 1.0,
            "color_theme": "default",
        }

    def _get_path(self):
        return resources.files(self.package_path).joinpath(self.filename)

    def load(self):
        try:
            path = self._get_path()
            user_settings = json5.loads(path.read_text(encoding="utf-8"))
            self.data.update(user_settings)
        except (FileNotFoundError, Exception):
            pass # Fail silently if settings file not found in package

    def save(self):
        """
        Saves settings. NOTE: This is complex for installed packages.
        A real app saves to a user-specific config directory.
        For this sandbox, we'll attempt to write to the source file,
        which works in a developer environment.
        """
        try:
            # as_file provides a temporary real filesystem path to the resource
            with resources.as_file(self._get_path()) as file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # json5.dumps needs these settings to produce valid JSONC/JSON
                    f.write(json5.dumps(self.data, indent=2, quote_keys=True, trailing_commas=False))
        except Exception:
            # Fail silently if installed in a read-only location (e.g., site-packages)
            pass

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

# Use the package path "src.data"
settings_manager = Settings("src.data", "settings.jsonc")