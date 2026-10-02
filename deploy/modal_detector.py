"""AI 작성 판별기(Fast-DetectGPT + Qwen2.5-1.5B)를 Modal CPU 컨테이너에 띄운다.

Vercel 함수는 메모리가 2GB라 1.5B 모델을 올릴 수 없어서 판별만 따로 뺐다.
GPU 없이 CPU 4코어로 짧은 글 1건에 1~2초. 쓸 때만 켜지고 마지막 요청 5분 뒤 꺼진다.
인증은 deploy/modal_qwen.py 와 같은 시크릿(localpass-llm)의 LLM_API_KEY 를 쓴다.

  modal deploy deploy/modal_detector.py     # 출력된 주소를 앱의 DETECTOR_URL 로

앱은 이 서비스가 돌려주는 점수(discrepancy)를 data/detector_calibration.json 으로 확률로 바꾼다.
"""
import os

import modal

MODEL = "Qwen/Qwen2.5-1.5B"
MAX_TOKENS = 512

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.6.0", index_url="https://download.pytorch.org/whl/cpu")  # CPU 전용 (CUDA 미포함)
    .pip_install("transformers>=4.45", "safetensors", "fastapi[standard]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)
model_cache = modal.Volume.from_name("localpass-detector-cache", create_if_missing=True)

app = modal.App("localpass-detector")


@app.cls(
    image=image,
    cpu=4,
    memory=8192,                 # fp32 1.5B ≈ 6GB
    volumes={"/cache": model_cache},
    secrets=[modal.Secret.from_name("localpass-llm", required_keys=["LLM_API_KEY"])],
    scaledown_window=5 * 60,     # 마지막 요청 5분 뒤 종료 — 상시 과금 없음
    timeout=10 * 60,
)
@modal.concurrent(max_inputs=8)
class Detector:
    @modal.enter()
    def load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.set_num_threads(4)
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(MODEL, cache_dir="/cache")
        self.model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32, cache_dir="/cache").eval()
        model_cache.commit()

    def discrepancy(self, text: str) -> float:
        """ai_pipeline/local_detector.py 의 discrepancy() 와 같은 계산 (Fast-DetectGPT 해석적 기준)."""
        torch = self.torch
        ids = self.tok(text, return_tensors="pt", truncation=True, max_length=MAX_TOKENS).input_ids
        if ids.shape[1] < 8:
            raise ValueError("text too short")
        with torch.no_grad():
            logits = self.model(ids).logits[:, :-1].float()
        labels = ids[:, 1:]
        lprobs = torch.log_softmax(logits, dim=-1)
        probs = lprobs.exp()
        ll = lprobs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
        mean = (probs * lprobs).sum(-1)
        var = (probs * lprobs.square()).sum(-1) - mean.square()
        return ((ll.sum(-1) - mean.sum(-1)) / var.sum(-1).sqrt()).item()

    @modal.asgi_app()
    def web(self):
        from fastapi import FastAPI, Header, HTTPException
        from pydantic import BaseModel, Field

        api = FastAPI()

        class Body(BaseModel):
            text: str = Field(..., min_length=1, max_length=5000)

        @api.get("/health")
        def health():
            return {"ok": True, "model": MODEL}

        @api.post("/discrepancy")
        def score(body: Body, authorization: str = Header("")):
            if authorization != f"Bearer {os.environ['LLM_API_KEY']}":
                raise HTTPException(401, "unauthorized")
            try:
                return {"score": self.discrepancy(body.text)}
            except ValueError as e:
                raise HTTPException(422, str(e))

        return api
