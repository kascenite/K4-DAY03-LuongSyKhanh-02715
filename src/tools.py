"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Chủ đề: Trợ lý Lập kế hoạch Ăn uống Cá nhân (Personal Meal-Planning Assistant).
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "food_lookup",
        "description": "Tra cứu thông tin dinh dưỡng (calories, protein, carbs, fat) và giá của một món ăn theo tên.",
        "parameters": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "Tên món ăn cần tra cứu (ví dụ: 'Phở bò tái')"
                }
            },
            "required": ["food_name"]
        }
    },
    {
        "name": "add_meal_to_plan",
        "description": "Thêm một món ăn đã chọn vào kế hoạch ăn uống tuần tại một ngày và bữa cụ thể, đồng thời cập nhật tổng calories/chi phí đã dùng trong tuần.",
        "parameters": {
            "type": "object",
            "properties": {
                "day": {
                    "type": "string",
                    "description": "Ngày trong tuần cần lên kế hoạch (ví dụ: 'Thứ Hai', 'Thứ Ba', ..., 'Chủ Nhật')"
                },
                "meal_slot": {
                    "type": "string",
                    "description": "Bữa ăn trong ngày: 'Sáng', 'Trưa', hoặc 'Tối'"
                },
                "food_name": {
                    "type": "string",
                    "description": "Tên món ăn đã chọn để thêm vào kế hoạch (ví dụ: 'Cơm gà xối mỡ')"
                }
            },
            "required": ["day", "meal_slot", "food_name"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "Phở bò tái": {"calories": 480, "protein_g": 25, "carbs_g": 55, "fat_g": 12, "price_vnd": 45000, "meal_type": "Sáng/Trưa"},
    "Cơm gà xối mỡ": {"calories": 650, "protein_g": 30, "carbs_g": 70, "fat_g": 25, "price_vnd": 35000, "meal_type": "Trưa/Tối"},
    "Bún chả": {"calories": 550, "protein_g": 22, "carbs_g": 60, "fat_g": 20, "price_vnd": 40000, "meal_type": "Trưa"},
    "Salad ức gà": {"calories": 380, "protein_g": 32, "carbs_g": 18, "fat_g": 16, "price_vnd": 50000, "meal_type": "Trưa/Tối"},
    "Bánh mì trứng": {"calories": 400, "protein_g": 15, "carbs_g": 45, "fat_g": 18, "price_vnd": 20000, "meal_type": "Sáng"},
    "Cơm tấm sườn": {"calories": 700, "protein_g": 28, "carbs_g": 75, "fat_g": 28, "price_vnd": 38000, "meal_type": "Trưa/Tối"},
    "Xôi mặn": {"calories": 450, "protein_g": 12, "carbs_g": 65, "fat_g": 14, "price_vnd": 18000, "meal_type": "Sáng"},
    "Canh chua cá kèm cơm": {"calories": 500, "protein_g": 24, "carbs_g": 55, "fat_g": 15, "price_vnd": 42000, "meal_type": "Tối"},
    "Cháo gà": {"calories": 350, "protein_g": 18, "carbs_g": 45, "fat_g": 10, "price_vnd": 25000, "meal_type": "Sáng"},
    "Bún bò Huế": {"calories": 600, "protein_g": 26, "carbs_g": 65, "fat_g": 22, "price_vnd": 45000, "meal_type": "Sáng/Trưa"},
    "Mì Quảng": {"calories": 580, "protein_g": 24, "carbs_g": 68, "fat_g": 20, "price_vnd": 40000, "meal_type": "Trưa/Tối"},
    "Gỏi cuốn tôm thịt": {"calories": 300, "protein_g": 18, "carbs_g": 35, "fat_g": 8, "price_vnd": 35000, "meal_type": "Trưa/Tối"},
    "Cơm chay đậu hũ": {"calories": 420, "protein_g": 16, "carbs_g": 60, "fat_g": 12, "price_vnd": 30000, "meal_type": "Trưa/Tối"},
    "Bánh cuốn": {"calories": 380, "protein_g": 14, "carbs_g": 55, "fat_g": 10, "price_vnd": 25000, "meal_type": "Sáng"},
    "Hủ tiếu Nam Vang": {"calories": 520, "protein_g": 22, "carbs_g": 60, "fat_g": 16, "price_vnd": 38000, "meal_type": "Sáng/Trưa"},
}

# Trạng thái kế hoạch ăn uống tuần (mock, lưu trong bộ nhớ trong suốt vòng đời tiến trình)
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

WEEKLY_PLAN_STATE = {
    "entries": [],  # danh sách {"day", "meal_slot", "food_name", "calories", "price_vnd"}
    "week_budget_vnd": 700000,
    "daily_calorie_target": 2000,
}


def execute_food_lookup(food_name: str) -> str:
    """Thực thi tra cứu thông tin dinh dưỡng/giá theo tên món ăn"""
    lookup = {name.strip().lower(): (name, data) for name, data in MOCK_DATABASE.items()}
    match = lookup.get(food_name.strip().lower())
    if match:
        real_name, data = match
        return json.dumps({
            "status": "SUCCESS",
            "food_name": real_name,
            "data": data
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu dinh dưỡng cho món '{food_name}'"
        }, ensure_ascii=False)


def execute_add_meal_to_plan(day: str, meal_slot: str, food_name: str) -> str:
    """Thực thi thêm món ăn vào kế hoạch tuần, kiểm tra đa dạng món trong 3 ngày liên tiếp và cập nhật tổng ngân sách/calories"""
    lookup = {name.strip().lower(): (name, data) for name, data in MOCK_DATABASE.items()}
    match = lookup.get(food_name.strip().lower())
    if not match:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không thể thêm vào kế hoạch vì không tìm thấy món '{food_name}' trong dữ liệu."
        }, ensure_ascii=False)

    real_name, data = match

    try:
        day_idx = WEEKDAYS.index(day.strip())
    except ValueError:
        return json.dumps({
            "status": "INVALID_DAY",
            "message": f"Ngày '{day}' không hợp lệ. Vui lòng dùng một trong: {', '.join(WEEKDAYS)}"
        }, ensure_ascii=False)

    # Kiểm tra đa dạng món ăn: không lặp lại cùng món trong 3 ngày liên tiếp
    variation_warning = None
    for entry in WEEKLY_PLAN_STATE["entries"]:
        if entry["food_name"] == real_name:
            try:
                other_idx = WEEKDAYS.index(entry["day"])
            except ValueError:
                continue
            if abs(other_idx - day_idx) <= 2:
                variation_warning = f"Món '{real_name}' đã được lên kế hoạch vào {entry['day']} (gần {day}), nên đa dạng hóa thực đơn."
                break

    entry = {
        "day": day,
        "meal_slot": meal_slot,
        "food_name": real_name,
        "calories": data["calories"],
        "price_vnd": data["price_vnd"],
    }
    WEEKLY_PLAN_STATE["entries"].append(entry)

    total_spent_vnd = sum(e["price_vnd"] for e in WEEKLY_PLAN_STATE["entries"])
    total_calories_today = sum(e["calories"] for e in WEEKLY_PLAN_STATE["entries"] if e["day"] == day)

    result = {
        "status": "SUCCESS",
        "booking": entry,
        "week_summary": {
            "total_spent_vnd": total_spent_vnd,
            "remaining_budget_vnd": WEEKLY_PLAN_STATE["week_budget_vnd"] - total_spent_vnd,
            "total_calories_today": total_calories_today,
            "daily_calorie_target": WEEKLY_PLAN_STATE["daily_calorie_target"],
        },
        "message": f"Đã thêm '{real_name}' vào bữa {meal_slot} ngày {day}."
    }
    if variation_warning:
        result["variation_warning"] = variation_warning

    return json.dumps(result, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "food_lookup": execute_food_lookup,
    "add_meal_to_plan": execute_add_meal_to_plan
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
