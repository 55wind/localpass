"""Qwen2.5-7B-Instruct를 Modal GPU(L4)에 vLLM OpenAI 호환 서버로 띄운다.

요청이 있을 때만 켜지고, 마지막 요청 후 5분이 지나면 꺼진다 (꺼져 있는 동안 요금 0).
주소가 공개되므로 vLLM --api-key 로 막는다. 앱(.env)의 LLM_API_KEY 와 같은 값을 써야 한다.

  1) modal token new                                         # 최초 1회 로그인
  2) modal secret create localpass-llm LLM_API_KEY=<임의의 긴 문자열>
  3) modal deploy deploy/modal_qwen.py                       # 출력되는 https://...modal.run 주소 확인
  4) .env:  LLM_BASE_URL=<주소>/v1   LLM_API_KEY=<2번 값>   (LLM_MODEL 은 그대로 둬도 됨)
  5) modal run deploy/modal_qwen.py                          # (선택) 동작 확인
"""
import os
import subprocess

import modal

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
SERVED_NAMES = [MODEL_NAME, "qwen2.5:7b-instruct"]  # 로컬 Ollama 이름도 받아서 .env 의 LLM_MODEL 을 안 바꿔도 되게
VLLM_PORT = 8000
MINUTES = 60

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)

# 모델 가중치·컴파일 캐시를 저장해 두어, 다시 켜질 때 내려받지 않는다
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)

app = modal.App("localpass-qwen")


@app.server(
    image=vllm_image,
    gpu="L4",                      # 24GB — 7B bf16 (약 15GB) + KV 캐시
    scaledown_window=5 * MINUTES,  # 마지막 요청 후 5분 뒤 자동 종료 (min_containers 미설정 → 상시 과금 없음)
    startup_timeout=15 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
    secrets=[modal.Secret.from_name("localpass-llm", required_keys=["LLM_API_KEY"])],
    port=VLLM_PORT,
    target_concurrency=8,
    unauthenticated=True,          # Modal 프록시 인증 대신 vLLM API 키로 인증 (앱이 Bearer 토큰을 보냄)
)
class Server:
    @modal.enter()
    def start(self):
        cmd = [
            "vllm", "serve", MODEL_NAME,
            "--served-model-name", *SERVED_NAMES,
            "--host", "0.0.0.0", "--port", str(VLLM_PORT),
            "--api-key", os.environ["LLM_API_KEY"],
            "--max-model-len", "8192",
            "--gpu-memory-utilization", "0.90",
            "--enforce-eager",  # CUDA 그래프 캡처를 건너뛰어 콜드 스타트 단축
        ]
        print(*[c if c != os.environ["LLM_API_KEY"] else "***" for c in cmd])
        self.process = subprocess.Popen(cmd)

    @modal.exit()
    def stop(self):
        self.process.terminate()


@app.local_entrypoint()
def test(prompt: str = "성수동을 한 문장으로 소개해 줘."):
    """배포된 서버에 헬스체크 후 한 번 질문한다. 키는 로컬 환경변수 LLM_API_KEY 에서 읽는다."""
    import json
    import time
    import urllib.request

    url = Server.get_url()
    key = os.environ.get("LLM_API_KEY", "")
    print("서버:", url)
    deadline = time.time() + 15 * MINUTES
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=60) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(3)
    body = json.dumps({"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "max_tokens": 120}).encode()
    req = urllib.request.Request(f"{url}/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        print(json.loads(r.read())["choices"][0]["message"]["content"])
