# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Lương Sỹ Khánh  
> **Mã Sinh Viên / Mã Học viên:** 02715  
> **Chủ đề Lựa chọn:** Đề tài Mở — Trợ lý Lập kế hoạch Ăn uống Cá nhân (Personal Meal-Planning Assistant)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 3 / 5 | Có tổng hợp dữ liệu tra cứu (calories/giá) với ngân sách và calories còn lại — nhưng `run_react_agent` chỉ thực thi 1 tool call mỗi lượt hỏi (không lặp lại LLM sau Observation), nên TC04 chỉ minh họa suy luận đơn bước có cân nhắc, chưa phải chuỗi 2 tool call thực sự. |
| **2. Tool Interaction** | 4 / 5 | Cần cả tra cứu (đọc, `food_lookup`) lẫn ghi nhận kế hoạch (ghi, `add_meal_to_plan`) qua MCP Server — không thể trả lời chỉ bằng kiến thức có sẵn của LLM. |
| **3. Dynamic Decision** | 3 / 5 | Cảnh báo (vượt ngân sách? lặp món trong 3 ngày? vượt calories?) do Python trong `tools.py` tính toán; LLM chỉ chọn Tool và trình bày lại Observation, không tự tái lập kế hoạch sau Observation (TC05 NOT_FOUND chỉ thông báo lại, không gợi ý món thay thế). |
| **4. Long Horizon Goal** | 3 / 5 | Trạng thái ngân sách/calories/đa dạng món (`WEEKLY_PLAN_STATE`) được giữ trong tiến trình cho phạm vi 1 tuần — nhưng không lưu trữ bền vững đa tuần, trace thực tế chỉ minh họa thêm từng bữa đơn lẻ. |
| **TỔNG ĐIỂM AGENTIC FIT** | **13 / 20** | Vượt ngưỡng 12/20 → Bài toán phù hợp triển khai Agentic System ở mức cơ bản (single-step + state theo tuần). |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật (trích từ TC03 — `add_meal_to_plan`, chạy với `GeminiProvider`):

```json
[
  {
    "step": 1,
    "query": "Hãy thêm món Salad ức gà vào bữa trưa Thứ Ba cho tôi.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "add_meal_to_plan",
    "arguments": {
      "meal_slot": "Trưa",
      "food_name": "Salad ức gà",
      "day": "Thứ Ba"
    },
    "observation": {
      "status": "SUCCESS",
      "booking": {
        "day": "Thứ Ba",
        "meal_slot": "Trưa",
        "food_name": "Salad ức gà",
        "calories": 380,
        "price_vnd": 50000
      },
      "week_summary": {
        "total_spent_vnd": 50000,
        "remaining_budget_vnd": 650000,
        "total_calories_today": 380,
        "daily_calorie_target": 2000
      },
      "message": "Đã thêm 'Salad ức gà' vào bữa Trưa ngày Thứ Ba."
    },
    "latency_ms": 3227.07
  },
  {
    "step": 2,
    "query": "Hãy thêm món Salad ức gà vào bữa trưa Thứ Ba cho tôi.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Đã thêm 'Salad ức gà' vào bữa Trưa ngày Thứ Ba. Đã dùng 50000đ trong tuần (còn lại 650000đ), calories hôm đó: 380/2000.",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (TC02, TC03, TC04 gọi `food_lookup`/`add_meal_to_plan`; TC05 gọi `food_lookup` và nhận đúng `NOT_FOUND`; TC01 không cần gọi Tool vì là câu hỏi chung).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
