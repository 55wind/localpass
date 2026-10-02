import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    """테스트가 실제 .cache 를 건드리지 않도록 임시 폴더로 돌린다."""
    import cache
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
