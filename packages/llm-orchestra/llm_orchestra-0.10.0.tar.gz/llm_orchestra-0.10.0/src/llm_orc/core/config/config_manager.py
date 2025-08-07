"""Configuration management system for llm-orc."""

import os
import shutil
from pathlib import Path
from typing import Any

import yaml


class ConfigurationManager:
    """Manages configuration directories and file locations."""

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._global_config_dir = self._get_global_config_dir()
        self._local_config_dir = self._discover_local_config()

        # Create global config directory and setup defaults
        self._global_config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_default_config()
        self._setup_default_ensembles()

    def _get_global_config_dir(self) -> Path:
        """Get the global configuration directory following XDG spec."""
        # Check for XDG_CONFIG_HOME environment variable
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            return Path(xdg_config_home) / "llm-orc"

        # Default to ~/.config/llm-orc
        return Path.home() / ".config" / "llm-orc"

    def _discover_local_config(self) -> Path | None:
        """Discover local .llm-orc directory walking up from cwd."""
        current = Path.cwd()

        # Stop at root directory or when we've walked up too far
        while current != current.parent:
            llm_orc_dir = current / ".llm-orc"
            if llm_orc_dir.exists() and llm_orc_dir.is_dir():
                return llm_orc_dir
            current = current.parent

            # Stop if we've reached the file system root
            if current == current.parent:
                break

        return None

    @property
    def global_config_dir(self) -> Path:
        """Get the global configuration directory."""
        return self._global_config_dir

    def ensure_global_config_dir(self) -> None:
        """Ensure the global configuration directory exists."""
        self._global_config_dir.mkdir(parents=True, exist_ok=True)
        self._setup_default_config()
        self._setup_default_ensembles()

    def _setup_default_config(self) -> None:
        """Set up default global config.yaml by copying template content."""
        config_file = self._global_config_dir / "config.yaml"

        # Only create if doesn't exist (don't overwrite user configurations)
        if config_file.exists():
            return

        try:
            # Get the template config content from library
            template_content = self._get_template_config_content("global-config.yaml")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(template_content)
        except FileNotFoundError:
            # Fallback to empty config if template not found
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump({"model_profiles": {}}, f, default_flow_style=False, indent=2)

    def _setup_default_ensembles(self) -> None:
        """Set up default validation ensembles by copying template files."""
        ensembles_dir = self._global_config_dir / "ensembles"
        ensembles_dir.mkdir(exist_ok=True)

        # Get the template ensembles directory
        template_dir = self._get_template_ensembles_dir()

        if not template_dir.exists():
            # Fallback to empty directory if templates not found
            return

        # Copy each template file to the ensembles directory if it doesn't exist
        for template_file in template_dir.glob("*.yaml"):
            target_file = ensembles_dir / template_file.name
            if not target_file.exists():
                shutil.copy2(template_file, target_file)

    def _get_template_ensembles_dir(self) -> Path:
        """Get the template ensembles directory path."""
        # Get the llm_orc package directory (parent of core)
        package_dir = Path(__file__).parent.parent.parent
        return package_dir / "templates" / "ensembles"

    def _get_template_config_content(self, filename: str) -> str:
        """Get template config content from library repository."""
        from llm_orc.cli_library.library import get_template_content

        try:
            return get_template_content(filename)
        except FileNotFoundError:
            # Fallback to local template if library template not found
            package_dir = Path(__file__).parent.parent.parent
            local_template_path = package_dir / "templates" / filename

            if local_template_path.exists():
                with open(local_template_path, encoding="utf-8") as f:
                    return f.read()
            else:
                raise FileNotFoundError(f"Template not found: {filename}") from None

    @property
    def local_config_dir(self) -> Path | None:
        """Get the local configuration directory if found."""
        return self._local_config_dir

    def get_ensembles_dirs(self) -> list[Path]:
        """Get ensemble directories in priority order (local first, then global)."""
        dirs = []

        # Local config takes precedence
        if self._local_config_dir:
            local_ensembles = self._local_config_dir / "ensembles"
            if local_ensembles.exists():
                dirs.append(local_ensembles)

        # Global config as fallback
        global_ensembles = self._global_config_dir / "ensembles"
        if global_ensembles.exists():
            dirs.append(global_ensembles)

        return dirs

    def get_credentials_file(self) -> Path:
        """Get the credentials file path (always in global config)."""
        return self._global_config_dir / "credentials.yaml"

    def get_encryption_key_file(self) -> Path:
        """Get the encryption key file path (always in global config)."""
        return self._global_config_dir / ".encryption_key"

    def load_project_config(self) -> dict[str, Any]:
        """Load project-specific configuration if available."""
        if not self._local_config_dir:
            return {}

        config_file = self._local_config_dir / "config.yaml"
        if not config_file.exists():
            return {}

        try:
            with open(config_file) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _load_global_config(self) -> dict[str, Any]:
        """Load global configuration from config.yaml file."""
        config_file = self._global_config_dir / "config.yaml"
        if not config_file.exists():
            return {}

        try:
            with open(config_file) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def load_performance_config(self) -> dict[str, Any]:
        """Load performance configuration with sensible defaults."""
        # Default performance settings
        defaults = {
            "concurrency": {
                "max_concurrent_agents": 0,  # 0 = use smart defaults
                "connection_pool": {
                    "max_connections": 100,
                    "max_keepalive": 20,
                    "keepalive_expiry": 30,
                },
            },
            "execution": {
                "default_timeout": 60,
                "monitoring_enabled": True,
                "streaming_enabled": True,
            },
            "memory": {
                "efficient_mode": False,
                "max_memory_mb": 0,  # 0 = unlimited
            },
        }

        # Try to load from global config
        global_config = self._load_global_config()
        global_performance = global_config.get("performance", {})

        # Try to load from local config
        local_config = self.load_project_config()
        local_performance = local_config.get("performance", {})

        # Merge configurations: defaults -> global -> local
        merged_config = defaults.copy()
        self._deep_merge_dict(merged_config, global_performance)
        self._deep_merge_dict(merged_config, local_performance)

        return merged_config

    def _deep_merge_dict(self, base: dict[str, Any], overlay: dict[str, Any]) -> None:
        """Deep merge overlay dict into base dict."""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value

    def init_local_config(self, project_name: str | None = None) -> None:
        """Initialize local configuration in current directory."""
        local_dir = Path.cwd() / ".llm-orc"

        if local_dir.exists():
            raise ValueError("Local .llm-orc directory already exists")

        # Create directory structure
        local_dir.mkdir()
        (local_dir / "ensembles").mkdir()
        (local_dir / "models").mkdir()
        (local_dir / "scripts").mkdir()

        # Create config file from template
        config_file = local_dir / "config.yaml"

        try:
            # Get template content from library
            template_content = self._get_template_config_content("local-config.yaml")

            # Replace placeholder with actual project name
            actual_project_name = project_name or Path.cwd().name
            config_content = template_content.replace(
                "{project_name}", actual_project_name
            )

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
        except FileNotFoundError:
            # Fallback to minimal config if template not found
            config_data = {
                "project": {"name": project_name or Path.cwd().name},
                "model_profiles": {},
            }
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)

        # Copy example ensemble template to local ensembles directory
        try:
            example_template_content = self._get_template_config_content(
                "example-local-ensemble.yaml"
            )
            local_ensemble_file = (
                local_dir / "ensembles" / "example-local-ensemble.yaml"
            )
            with open(local_ensemble_file, "w", encoding="utf-8") as f:
                f.write(example_template_content)
        except FileNotFoundError:
            # If template not found in library, try local fallback
            template_ensemble_dir = self._get_template_ensembles_dir()
            example_template = template_ensemble_dir / "example-local-ensemble.yaml"
            if example_template.exists():
                local_ensemble_file = (
                    local_dir / "ensembles" / "example-local-ensemble.yaml"
                )
                shutil.copy2(example_template, local_ensemble_file)

        # Create .gitignore for credentials if they are stored locally
        gitignore_file = local_dir / ".gitignore"
        with open(gitignore_file, "w") as f:
            f.write("# Local credentials (if any)\ncredentials.yaml\n.encryption_key\n")

    def get_model_profiles(self) -> dict[str, dict[str, str]]:
        """Get merged model profiles from global and local configs."""
        # Start with global profiles
        global_profiles = {}
        global_config_file = self._global_config_dir / "config.yaml"
        if global_config_file.exists():
            with open(global_config_file) as f:
                global_config = yaml.safe_load(f) or {}
                global_profiles = global_config.get("model_profiles", {})

        # Merge with local profiles (local overrides global)
        local_profiles = {}
        if self._local_config_dir:
            local_config_file = self._local_config_dir / "config.yaml"
            if local_config_file.exists():
                with open(local_config_file) as f:
                    local_config = yaml.safe_load(f) or {}
                    local_profiles = local_config.get("model_profiles", {})

        # Merge profiles with local taking precedence
        merged_profiles = {**global_profiles, **local_profiles}
        return merged_profiles

    def resolve_model_profile(self, profile_name: str) -> tuple[str, str]:
        """Resolve a model profile to (model, provider) tuple."""
        profiles = self.get_model_profiles()

        if profile_name not in profiles:
            raise ValueError(f"Model profile '{profile_name}' not found")

        profile = profiles[profile_name]
        model = profile.get("model")
        provider = profile.get("provider")

        if not model or not provider:
            raise ValueError(
                f"Model profile '{profile_name}' is incomplete. "
                f"Both 'model' and 'provider' are required."
            )

        return model, provider

    def get_model_profile(self, profile_name: str) -> dict[str, Any] | None:
        """Get a specific model profile configuration.

        Args:
            profile_name: Name of the model profile to retrieve

        Returns:
            Model profile configuration dict or None if not found
        """
        profiles = self.get_model_profiles()
        return profiles.get(profile_name)
