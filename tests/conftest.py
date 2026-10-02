import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    """테스트가 실제 .cache 를 건드리지 않고, AI 판별 모델(3GB)도 내려받지 않도록 한다."""
    import cache
    from ai_pipeline import ai_detect
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(ai_detect, "backend", lambda: "off")
