"""원격(Modal) GPU·CPU 서비스 공통 — 상태 확인과 콜드 스타트 대기.

서버리스(Vercel)에서는 요청이 끝나면 백그라운드 작업이 멈출 수 있고 인스턴스끼리 메모리를 공유하지 않으므로,
상태를 기억하지 않고 필요할 때마다 /health 에 직접 묻는다. Modal은 꺼져 있을 때 요청을 받으면 켜지기 시작하고,
켜지는 동안은 503(또는 응답 지연)을 돌려준다.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import requests

log = logging.getLogger(__name__)


def health_state(url: str, timeout: float = 4) -> str:
    """'ready' | 'starting' | 'offline' — 이 확인 자체가 꺼진 서비스를 깨운다."""
    try:
        code = requests.get(url, timeout=timeout).status_code
    except requests.RequestException:
        return "starting"  # 켜지는 동안 연결을 붙잡고 있는 경우
    if code == 200:
        return "ready"
    return "starting" if code in (502, 503, 504) else "offline"


def warm_status(health_urls: list[str]) -> dict:
    """여러 원격 서비스를 한꺼번에 확인해 가장 덜 준비된 상태를 돌려준다."""
    if not health_urls:
        return {"remote": False, "state": "ready"}
    with ThreadPoolExecutor(max_workers=len(health_urls)) as pool:
        states = list(pool.map(health_state, health_urls))
    for s in ("offline", "starting"):
        if s in states:
            return {"remote": True, "state": s}
    return {"remote": True, "state": "ready"}


def wait_ready(url: str, timeout: float) -> bool:
    """켜질 때까지 몇 초마다 확인한다. 준비되면 바로 멈춘다 (계속 두드리면 꺼지지 않아 요금이 나간다)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = health_state(url, timeout=30)
        if state == "ready":
            return True
        if state == "offline":
            return False
        time.sleep(4)
    log.warning("%s 가 %.0f초 안에 켜지지 않음", url, timeout)
    return False
