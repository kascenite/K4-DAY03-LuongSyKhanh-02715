"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Chủ đề: Trợ lý Lập kế hoạch Ăn uống Cá nhân (Personal Meal-Planning Assistant).
Dữ liệu món ăn và kế hoạch tuần được lưu trong SQLite (data/meal_planner.db) thay vì dict
trong bộ nhớ — dữ liệu seed vẫn nằm trong mã nguồn (FOOD_SEED_DATA) để dễ đọc/mở rộng,
còn file .db chỉ là nơi lưu trữ khi chạy (được tạo tự động, không commit vào git).
"""

import json
import os
import sqlite3
from typing import Any, Dict, List

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
# 2. DỮ LIỆU MÓN ĂN (SEED) & LƯU TRỮ SQLITE (EXECUTION LAYER)
# ==============================================================================

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "meal_planner.db")

DEFAULT_WEEK_BUDGET_VND = 700000
DEFAULT_DAILY_CALORIE_TARGET = 2000

# (name, calories, protein_g, carbs_g, fat_g, price_vnd, meal_type)
FOOD_SEED_DATA = [
    ("Phở bò tái", 480, 25, 55, 12, 45000, "Sáng/Trưa"),
    ("Cơm gà xối mỡ", 650, 30, 70, 25, 35000, "Trưa/Tối"),
    ("Bún chả", 550, 22, 60, 20, 40000, "Trưa"),
    ("Salad ức gà", 380, 32, 18, 16, 50000, "Trưa/Tối"),
    ("Bánh mì trứng", 400, 15, 45, 18, 20000, "Sáng"),
    ("Cơm tấm sườn", 700, 28, 75, 28, 38000, "Trưa/Tối"),
    ("Xôi mặn", 450, 12, 65, 14, 18000, "Sáng"),
    ("Canh chua cá kèm cơm", 500, 24, 55, 15, 42000, "Tối"),
    ("Cháo gà", 350, 18, 45, 10, 25000, "Sáng"),
    ("Bún bò Huế", 600, 26, 65, 22, 45000, "Sáng/Trưa"),
    ("Mì Quảng", 580, 24, 68, 20, 40000, "Trưa/Tối"),
    ("Gỏi cuốn tôm thịt", 300, 18, 35, 8, 35000, "Trưa/Tối"),
    ("Cơm chay đậu hũ", 420, 16, 60, 12, 30000, "Trưa/Tối"),
    ("Bánh cuốn", 380, 14, 55, 10, 25000, "Sáng"),
    ("Hủ tiếu Nam Vang", 520, 22, 60, 16, 38000, "Sáng/Trưa"),
    ("Phở gà", 420, 24, 50, 10, 40000, "Sáng/Trưa"),
    ("Bánh xèo", 480, 18, 55, 20, 35000, "Trưa/Tối"),
    ("Cơm chiên dương châu", 550, 20, 70, 18, 32000, "Trưa/Tối"),
    ("Bún riêu cua", 460, 20, 55, 16, 35000, "Sáng/Trưa"),
    ("Bánh bao", 250, 10, 35, 8, 12000, "Sáng"),
    ("Cháo lòng", 400, 22, 45, 14, 30000, "Sáng"),
    ("Cá kho tộ kèm cơm", 620, 30, 65, 22, 45000, "Trưa/Tối"),
    ("Thịt kho trứng kèm cơm", 680, 28, 70, 28, 40000, "Trưa/Tối"),
    ("Rau muống xào tỏi kèm cơm", 380, 10, 60, 10, 20000, "Trưa/Tối"),
    ("Đậu hũ sốt cà chua kèm cơm", 420, 14, 60, 12, 25000, "Trưa/Tối"),
    ("Ức gà áp chảo salad", 350, 35, 15, 12, 55000, "Trưa/Tối"),
    ("Yến mạch trái cây", 300, 10, 50, 8, 28000, "Sáng"),
    ("Bánh mì chảo", 550, 25, 50, 28, 35000, "Sáng"),
    ("Cơm cháy chà bông", 500, 15, 65, 18, 30000, "Trưa/Tối"),
    ("Súp cua", 220, 12, 20, 8, 35000, "Tối"),
    ("Nem nướng cuốn bánh tráng", 470, 22, 45, 20, 40000, "Trưa/Tối"),
    ("Bún đậu mắm tôm", 600, 20, 60, 30, 45000, "Trưa"),
    ("Chè đậu xanh", 200, 5, 40, 3, 15000, "Tối"),
]


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _get_settings(conn: sqlite3.Connection) -> Dict[str, int]:
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


def _init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                name TEXT PRIMARY KEY COLLATE NOCASE,
                calories INTEGER NOT NULL,
                protein_g INTEGER NOT NULL,
                carbs_g INTEGER NOT NULL,
                fat_g INTEGER NOT NULL,
                price_vnd INTEGER NOT NULL,
                meal_type TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plan_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                meal_slot TEXT NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                price_vnd INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )
        """)

        food_count = conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
        if food_count == 0:
            conn.executemany(
                "INSERT INTO foods (name, calories, protein_g, carbs_g, fat_g, price_vnd, meal_type) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                FOOD_SEED_DATA
            )

        for key, default_value in (
            ("week_budget_vnd", DEFAULT_WEEK_BUDGET_VND),
            ("daily_calorie_target", DEFAULT_DAILY_CALORIE_TARGET),
        ):
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, default_value))

        conn.commit()
    finally:
        conn.close()


_init_db()


def get_all_food_names() -> List[str]:
    """Trả về danh sách tên món ăn hiện có (dùng cho heuristic nhận diện của Mock Provider)."""
    conn = _get_connection()
    try:
        rows = conn.execute("SELECT name FROM foods ORDER BY name").fetchall()
        return [row["name"] for row in rows]
    finally:
        conn.close()


def get_weekly_plan_summary() -> Dict[str, Any]:
    """Trả về trạng thái kế hoạch tuần hiện tại (dùng cho web UI: /api/plan)."""
    conn = _get_connection()
    try:
        settings = _get_settings(conn)
        entries = [dict(row) for row in conn.execute(
            "SELECT day, meal_slot, food_name, calories, price_vnd FROM plan_entries ORDER BY id"
        ).fetchall()]
        total_spent_vnd = sum(e["price_vnd"] for e in entries)
        return {
            "week_budget_vnd": settings["week_budget_vnd"],
            "daily_calorie_target": settings["daily_calorie_target"],
            "entries": entries,
            "total_spent_vnd": total_spent_vnd,
            "remaining_budget_vnd": settings["week_budget_vnd"] - total_spent_vnd,
        }
    finally:
        conn.close()


def update_weekly_targets(week_budget_vnd: int, daily_calorie_target: int) -> None:
    """Cập nhật ngân sách tuần / mục tiêu calories (dùng cho web UI: POST /api/settings)."""
    conn = _get_connection()
    try:
        conn.execute("UPDATE settings SET value = ? WHERE key = 'week_budget_vnd'", (week_budget_vnd,))
        conn.execute("UPDATE settings SET value = ? WHERE key = 'daily_calorie_target'", (daily_calorie_target,))
        conn.commit()
    finally:
        conn.close()


def reset_weekly_plan() -> None:
    """Xóa toàn bộ các bữa ăn đã lên kế hoạch trong tuần (dùng cho web UI: POST /api/plan/reset)."""
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM plan_entries")
        conn.commit()
    finally:
        conn.close()


def execute_food_lookup(food_name: str) -> str:
    """Thực thi tra cứu thông tin dinh dưỡng/giá theo tên món ăn"""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT name, calories, protein_g, carbs_g, fat_g, price_vnd, meal_type FROM foods WHERE name = ?",
            (food_name.strip(),)
        ).fetchone()
    finally:
        conn.close()

    if row:
        return json.dumps({
            "status": "SUCCESS",
            "food_name": row["name"],
            "data": {
                "calories": row["calories"],
                "protein_g": row["protein_g"],
                "carbs_g": row["carbs_g"],
                "fat_g": row["fat_g"],
                "price_vnd": row["price_vnd"],
                "meal_type": row["meal_type"],
            }
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu dinh dưỡng cho món '{food_name}'"
        }, ensure_ascii=False)


def execute_add_meal_to_plan(day: str, meal_slot: str, food_name: str) -> str:
    """Thực thi thêm món ăn vào kế hoạch tuần, kiểm tra đa dạng món trong 3 ngày liên tiếp và cập nhật tổng ngân sách/calories"""
    try:
        day_idx = WEEKDAYS.index(day.strip())
    except ValueError:
        return json.dumps({
            "status": "INVALID_DAY",
            "message": f"Ngày '{day}' không hợp lệ. Vui lòng dùng một trong: {', '.join(WEEKDAYS)}"
        }, ensure_ascii=False)

    conn = _get_connection()
    try:
        food_row = conn.execute(
            "SELECT name, calories, price_vnd FROM foods WHERE name = ?", (food_name.strip(),)
        ).fetchone()
        if not food_row:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Không thể thêm vào kế hoạch vì không tìm thấy món '{food_name}' trong dữ liệu."
            }, ensure_ascii=False)

        real_name = food_row["name"]

        # Kiểm tra đa dạng món ăn: không lặp lại cùng món trong 3 ngày liên tiếp
        variation_warning = None
        existing_days = conn.execute(
            "SELECT DISTINCT day FROM plan_entries WHERE food_name = ?", (real_name,)
        ).fetchall()
        for row in existing_days:
            try:
                other_idx = WEEKDAYS.index(row["day"])
            except ValueError:
                continue
            if abs(other_idx - day_idx) <= 2:
                variation_warning = f"Món '{real_name}' đã được lên kế hoạch vào {row['day']} (gần {day}), nên đa dạng hóa thực đơn."
                break

        conn.execute(
            "INSERT INTO plan_entries (day, meal_slot, food_name, calories, price_vnd) VALUES (?, ?, ?, ?, ?)",
            (day, meal_slot, real_name, food_row["calories"], food_row["price_vnd"])
        )
        conn.commit()

        settings = _get_settings(conn)
        total_spent_vnd = conn.execute("SELECT COALESCE(SUM(price_vnd), 0) FROM plan_entries").fetchone()[0]
        total_calories_today = conn.execute(
            "SELECT COALESCE(SUM(calories), 0) FROM plan_entries WHERE day = ?", (day,)
        ).fetchone()[0]
    finally:
        conn.close()

    result = {
        "status": "SUCCESS",
        "booking": {
            "day": day,
            "meal_slot": meal_slot,
            "food_name": real_name,
            "calories": food_row["calories"],
            "price_vnd": food_row["price_vnd"],
        },
        "week_summary": {
            "total_spent_vnd": total_spent_vnd,
            "remaining_budget_vnd": settings["week_budget_vnd"] - total_spent_vnd,
            "total_calories_today": total_calories_today,
            "daily_calorie_target": settings["daily_calorie_target"],
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
