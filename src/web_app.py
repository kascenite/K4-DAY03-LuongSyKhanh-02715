"""
🌐 REACT AGENT — STREAMING CHAT UI (BONUS — KHÔNG TÍNH ĐIỂM RUBRIC)
Flask server nhỏ phục vụ giao diện chat trực tiếp với ReAct Agent (Cấp 3),
hiển thị Thought/Action/Observation theo thời gian thực. Không sửa đổi logic
CLI/agent gốc (tools.py, mcp_server.py, providers.py không đổi; app.py chỉ
thêm 1 tham số callback tùy chọn, mặc định None) — chỉ import và gọi lại các
hàm/state đã có.
"""

import json
import os
import queue
import re
import sys
import threading
import time

from flask import Flask, Response, jsonify, request

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MCPAcademicServer
from providers import get_llm_provider
from tools import get_weekly_plan_summary, update_weekly_targets, reset_weekly_plan
from app import run_react_agent, load_test_cases

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")

provider = get_llm_provider()
mcp_server = MCPAcademicServer()

WORD_SPLIT_RE = re.compile(r"\S+\s*")
TYPEWRITER_DELAY_SECONDS = 0.03


def typewriter_chunks(text):
    """Tách văn bản thành các mẩu theo từ (giữ khoảng trắng) để mô phỏng hiệu ứng gõ chữ."""
    return WORD_SPLIT_RE.findall(text or "")


def sse_event(channel, payload):
    return f"data: {json.dumps({'channel': channel, 'payload': payload}, ensure_ascii=False)}\n\n"


@app.route("/")
def index():
    return app.send_static_file("index.html")


PLACEHOLDER_KEYS = {"your_gemini_api_key_here", "your_openai_api_key_here", "your_anthropic_api_key_here"}


@app.route("/api/status")
def api_status():
    api_key = getattr(provider, "api_key", None)
    configured = api_key is None or (bool(api_key) and api_key not in PLACEHOLDER_KEYS)
    return jsonify({
        "provider": provider.__class__.__name__,
        "model": getattr(provider, "model_name", None),
        "configured": configured,
    })


@app.route("/api/examples")
def api_examples():
    tests = load_test_cases()
    examples = [
        {"id": tc["id"], "question": tc["question"]}
        for tc in tests
        if not tc["question"].strip().startswith("TODO")
    ]
    return jsonify(examples)


@app.route("/api/plan")
def api_plan():
    return jsonify(get_weekly_plan_summary())


@app.route("/api/settings", methods=["POST"])
def api_settings():
    data = request.get_json(silent=True) or {}
    budget = data.get("week_budget_vnd")
    calories = data.get("daily_calorie_target")

    errors = []
    if not isinstance(budget, (int, float)) or not (50_000 <= budget <= 10_000_000):
        errors.append("week_budget_vnd phải là số trong khoảng 50,000 - 10,000,000")
    if not isinstance(calories, (int, float)) or not (800 <= calories <= 5000):
        errors.append("daily_calorie_target phải là số trong khoảng 800 - 5000")
    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    update_weekly_targets(int(budget), int(calories))
    return jsonify(get_weekly_plan_summary())


@app.route("/api/plan/reset", methods=["POST"])
def api_plan_reset():
    reset_weekly_plan()
    return jsonify(get_weekly_plan_summary())


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Endpoint chặn (blocking) — giữ lại để test đơn giản qua curl."""
    data = request.get_json(silent=True) or {}
    query = (data.get("message") or "").strip()
    if not query:
        return jsonify({"error": "Thiếu nội dung câu hỏi ('message')."}), 400

    trace = run_react_agent(query, provider, mcp_server)
    final_entry = next((e for e in reversed(trace) if e.get("action_type") == "FINAL_ANSWER"), None)
    final_answer = final_entry.get("output", "") if final_entry else ""

    return jsonify({"trace": trace, "final_answer": final_answer})


@app.route("/api/chat/stream", methods=["POST"])
def api_chat_stream():
    data = request.get_json(silent=True) or {}
    query = (data.get("message") or "").strip()
    if not query:
        return jsonify({"error": "Thiếu nội dung câu hỏi ('message')."}), 400

    def generate():
        # Stream từng bước thật khi xảy ra (Thought -> Action -> Observation); Final Answer
        # được mô phỏng hiệu ứng gõ chữ trên văn bản đã có đầy đủ (xem trace_eval.md về lý do
        # không stream token thật qua đường tool-calling).
        step_queue = queue.Queue()

        def on_step(entry):
            if entry.get("action_type") == "FINAL_ANSWER":
                step_queue.put(("final_start", {}))
                for token in typewriter_chunks(entry.get("output", "")):
                    step_queue.put(("final_token", {"text": token}))
                    time.sleep(TYPEWRITER_DELAY_SECONDS)
                step_queue.put(("final_end", {"latency_ms": entry.get("latency_ms", 0)}))
            else:
                step_queue.put(("step", entry))

        def worker():
            trace = run_react_agent(query, provider, mcp_server, on_step=on_step)
            used_mock_fallback = any(
                "Mock" in (e.get("output", "") + e.get("thought", "")) for e in trace
            )
            step_queue.put(("done", {"trace": trace, "used_mock_fallback": used_mock_fallback}))

        threading.Thread(target=worker, daemon=True).start()

        while True:
            channel, payload = step_queue.get()
            yield sse_event(channel, payload)
            if channel == "done":
                break

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    print("==========================================================")
    print("🌐 MEAL-PLANNING REACT AGENT — STREAMING CHAT")
    print("==========================================================")
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}")
    print("👉 Mở trình duyệt tại: http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
