import importlib
import pathlib
from pathlib import Path

import pytest

import fspacker.settings


@pytest.fixture(autouse=True)
def reload_module() -> None:
    importlib.reload(fspacker.settings)


class TestSettings:
    """Test settings module."""

    def test_default_settings(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test default settings."""
        settings = fspacker.settings.get_settings()
        cache_dir = pathlib.Path("~").expanduser() / ".cache" / "fspacker"

        # check default dirs settings
        assert settings.dirs.cache == cache_dir
        assert settings.dirs.libs == cache_dir / "libs-repo"
        assert settings.dirs.embed == cache_dir / "embed-repo"
        assert settings.dirs.tools == cache_dir / "tools"

        dirs = {
            "cache": cache_dir,
            "embed": cache_dir / "embed-repo",
            "libs": cache_dir / "libs-repo",
            "tools": cache_dir / "tools",
        }
        assert str(settings.dirs) == ",".join([
            f"{k}={v}" for k, v in dirs.items()
        ])

        # check default mode settings
        assert not settings.mode.archive
        assert not settings.mode.simplify
        assert "非调试" in str(settings.mode)
        assert "CONSOLE" in str(settings.mode)

        settings.show()
        assert "构建日期:" in str(caplog.text)
        assert f"目录: {settings.dirs}" in str(caplog.text)

    def test_set_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test change mode settings."""
        settings = fspacker.settings.get_settings()

        assert "非调试" in str(settings.mode)
        assert "CONSOLE" in str(settings.mode)
        assert "在线" in str(settings.mode)
        assert "离线" not in str(settings.mode)

        monkeypatch.setattr(
            "fspacker.settings._settings.mode",
            fspacker.settings.PackMode(
                archive=True,
                debug=True,
                gui=True,
                offline=True,
                rebuild=True,
                recursive=True,
                simplify=True,
                use_tk=True,
            ),
        )

        assert "GUI" in str(settings.mode)
        assert "调试" in str(settings.mode)
        assert "非调试" not in str(settings.mode)
        assert "离线" in str(settings.mode)

        settings.mode.reset()

        assert settings.mode == fspacker.settings.PackMode(
            archive=False,
            debug=False,
            gui=False,
            offline=False,
            rebuild=False,
            recursive=False,
            simplify=False,
            use_tk=False,
        )
        assert "GUI" not in str(settings.mode)
        assert "非调试" in str(settings.mode)

    def test_get_dirs_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Test get cache dir from env."""
        monkeypatch.setenv("FSP_DIRS__CACHE", str(tmp_path))
        monkeypatch.setenv("FSP_DIRS__LIBS", str(tmp_path / "libs"))

        settings = fspacker.settings.get_settings()
        assert settings.dirs.cache == tmp_path
        assert settings.dirs.libs == tmp_path / "libs"

    def test_get_dirs_when_env_not_set(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test get cache dir when env not set."""
        monkeypatch.delenv("FSP_DIRS__CACHE", raising=False)
        monkeypatch.delenv("FSP_DIRS__LIBS", raising=False)

        cache_dir = Path("~").expanduser() / ".cache" / "fspacker"
        assert fspacker.settings.get_settings().dirs.cache == cache_dir
