import base64
import io
import json
import urllib.request

from PIL import Image


class VLM:
    """llama-server(OpenAI 호환 API)로 띄운 Qwen3.5를 부른다. serve_vlm.sh 참고."""

    def __init__(self, base_url: str, max_new_tokens: int = 2048, timeout: int = 1800):
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.max_new_tokens = max_new_tokens
        self.timeout = timeout

    def ask(self, image: Image.Image, prompt: str) -> str:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=92)
        b64 = base64.b64encode(buf.getvalue()).decode()
        body = {
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": prompt},
            ]}],
            "max_tokens": self.max_new_tokens,
            "temperature": 0.7, "top_p": 0.8, "top_k": 20,   # Qwen3.5 non-thinking 권장값
            "chat_template_kwargs": {"enable_thinking": False},
        }
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            out = json.load(r)
        t = out.get("timings", {})
        if t:
            print(f"    {t.get('prompt_n', 0)} prompt tok @ {t.get('prompt_per_second', 0):.0f}/s, "
                  f"{t.get('predicted_n', 0)} gen tok @ {t.get('predicted_per_second', 0):.1f}/s")
        return (out["choices"][0]["message"]["content"] or "").strip()

