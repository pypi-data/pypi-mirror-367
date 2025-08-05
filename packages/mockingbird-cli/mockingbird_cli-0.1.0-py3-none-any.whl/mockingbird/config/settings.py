from pathlib import Path
import tomllib # Python 3.11+ tomllib, or use toml package for older versions
# import toml # Use this if you need to write TOML easily or support older Python
from typing import Optional, Any # Added Optional and Any

# Default configuration path
CONFIG_DIR = Path.home() / ".mockingbird"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "llm_providers": {
        # "openai": {"api_key": "YOUR_OPENAI_API_KEY"},
        # "anthropic": {"api_key": "YOUR_ANTHROPIC_API_KEY"},
    },
    "default_output_format": "csv",
}

def load_user_config() -> dict:
    """
    Loads user configuration from ~/.mockingbird/config.toml.
    If not found, returns default configuration (but does not write it).
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy() # Return a copy to prevent modification of defaults

    try:
        with open(CONFIG_FILE, "rb") as f: # tomllib expects bytes
            config_data = tomllib.load(f)
        # Simple merge: user config overrides defaults. For deeper merge, use a utility.
        merged_config = DEFAULT_CONFIG.copy()
        for key, value in config_data.items():
            if isinstance(value, dict) and isinstance(merged_config.get(key), dict):
                merged_config[key].update(value)
            else:
                merged_config[key] = value
        return merged_config
    except tomllib.TOMLDecodeError as e:
        print(f"Error decoding TOML from {CONFIG_FILE}: {e}. Using default config.")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Could not load config from {CONFIG_FILE}: {e}. Using default config.")
        return DEFAULT_CONFIG.copy()

def save_user_config(config: dict) -> None:
    """
    Saves configuration to ~/.mockingbird/config.toml.
    This is a placeholder, as 'tomllib' does not support writing.
    You would use 'toml' package (e.g., toml.dump) for this.
    """
    if not CONFIG_DIR.exists():
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating config directory {CONFIG_DIR}: {e}")
            return

    # Using print as a placeholder for actual toml writing
    print(f"Configuration would be saved to {CONFIG_FILE} (actual saving requires 'toml' package):")
    # import toml # Example with 'toml' package
    # with open(CONFIG_FILE, "w") as f:
    #     toml.dump(config, f)
    # print(f"Configuration saved to {CONFIG_FILE}")
    print(str(config))


def get_api_key(provider_name: str) -> Optional[str]:
    """
    Helper to get an API key for a specific LLM provider.
    Checks environment variables first, then the config file.
    """
    # Placeholder for actual env var names
    # env_var_name = f"MOCKINGBIRD_{provider_name.upper()}_API_KEY"
    # api_key = os.getenv(env_var_name)
    # if api_key:
    #     return api_key

    config = load_user_config()
    return config.get("llm_providers", {}).get(provider_name, {}).get("api_key")
