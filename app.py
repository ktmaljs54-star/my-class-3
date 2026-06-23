import streamlit as st
import uuid
from typing import List, Dict, Any

# --- 상단 상수 정의 (매직 넘버 및 고정 스타일 분리) ---
PAGE_TITLE: str = "프리미엄 할 일 플래너"
PAGE_ICON: str = "🎯"
LAYOUT_TYPE: str = "centered"

# UI 컬럼 비율 상수
UI_COL_RATIOS: List[int] = [1, 8, 1]
INPUT_COL_RATIOS: List[int] = [8, 2]

# 커스텀 CSS 스타일 정의
CUSTOM_CSS: str = """
<style>
/* 전체 배경 및 폰트 스타일 개선 */
.main .block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 650px;
}

/* 카드 디자인 */
.todo-card {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s ease;
    border-left: 5px solid #4F46E5;
}

.todo-card.completed {
    background-color: #f3f4f6;
    border-left: 5px solid #10B981;
    opacity: 0.7;
}

/* 텍스트 효과 */
.todo-text {
    font-size: 16px;
    color: #1F2937;
    font-weight: 500;
}

.todo-text.completed {
    text-decoration: line-through;
    color: #9CA3AF;
}

/* 메트릭 카드 컨테이너 */
.metric-container {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
    color: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 30px;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
    text-align: center;
}

/* 버튼 스타일 조정 */
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
"""

# --- 페이지 초기 설정 및 스타일 주입 ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT_TYPE,
    initial_sidebar_state="collapsed"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if "todos" not in st.session_state:
    st.session_state.todos = []

# --- 핵심 비즈니스 로직 (UI와 분리하여 타입 힌트와 함께 정의) ---

def add_todo() -> None:
    """세션 상태의 입력값을 읽어 새로운 할 일을 추가합니다."""
    task_text: str = st.session_state.get("new_todo_input", "").strip()
    if task_text:
        new_item: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "task": task_text,
            "done": False
        }
        st.session_state.todos.append(new_item)
        st.session_state.new_todo_input = ""

def delete_todo(todo_id: str) -> None:
    """지정된 ID의 할 일을 목록에서 삭제합니다."""
    st.session_state.todos = [t for t in st.session_state.todos if t["id"] != todo_id]

def toggle_todo(todo_id: str) -> None:
    """지정된 ID의 할 일 완료 여부를 토글합니다."""
    for todo in st.session_state.todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            break

# --- UI 렌더링 헬퍼 함수 ---

def render_todo_item(todo: Dict[str, Any], prefix: str) -> None:
    """개별 할 일 항목을 렌더링합니다. 탭 충돌을 피하기 위해 prefix를 키에 사용합니다."""
    todo_id: str = todo["id"]
    col_check, col_text, col_btn = st.columns(UI_COL_RATIOS)
    
    # 1. 완료 여부 토글 체크박스 (prefix를 사용하여 키 중복 방지)
    with col_check:
        st.checkbox(
            "선택", 
            value=todo["done"], 
            key=f"check_{prefix}_{todo_id}", 
            label_visibility="collapsed",
            on_change=toggle_todo,
            args=(todo_id,)
        )
    
    # 2. 할 일 텍스트 표시 (완료 시 취소선 스타일)
    with col_text:
        if todo["done"]:
            st.markdown(f"<p class='todo-text completed'>{todo['task']}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='todo-text'>{todo['task']}</p>", unsafe_allow_html=True)
            
    # 3. 삭제 버튼 (prefix를 사용하여 키 중복 방지)
    with col_btn:
        st.button(
            "❌", 
            key=f"del_{prefix}_{todo_id}", 
            on_click=delete_todo, 
            args=(todo_id,),
            help="이 할 일 삭제"
        )

def render_todo_list(filtered_todos: List[Dict[str, Any]], prefix: str) -> None:
    """필터링된 할 일 목록 전체를 렌더링합니다."""
    if not filtered_todos:
        st.info("해당하는 할 일이 없습니다.")
        return
        
    for todo in filtered_todos:
        render_todo_item(todo, prefix)

# --- 메인 UI 페이지 구성 ---

st.title("🎯 Premium 할 일 플래너")
st.caption("하루의 목표를 계획하고 체계적으로 완료 상태를 기록하세요.")
st.write("---")

# 요약 정보 계산
total_count: int = len(st.session_state.todos)
completed_count: int = sum(1 for t in st.session_state.todos if t["done"])
pending_count: int = total_count - completed_count

# 요약 대시보드 렌더링
if total_count > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="총 할 일", value=total_count)
    with col2:
        completion_rate: str = f"{completed_count / total_count * 100:.0f}%" if total_count > 0 else "0%"
        st.metric(label="완료됨 ✅", value=completed_count, delta=completion_rate)
    with col3:
        st.metric(label="미완료 ⏳", value=pending_count)
else:
    # 할 일이 없는 초기 상태 환영 메시지
    st.markdown("""
        <div class="metric-container">
            <div style="font-size: 20px; font-weight: 600; margin-bottom: 8px;">할 일 목록이 아직 비어 있습니다!</div>
            <div style="font-size: 14px; opacity: 0.9;">아래 입력창에 첫 번째 목표를 추가하여 플래너를 채워보세요.</div>
        </div>
    """, unsafe_allow_html=True)

# 새로운 할 일 추가 입력 창
st.subheader("➕ 새로운 할 일 추가")
st.text_input(
    "할 일 입력 필드",
    key="new_todo_input",
    placeholder="예: 오늘 진행할 업무 작성하기...",
    label_visibility="collapsed",
    on_change=add_todo
)

# 추가 버튼
btn_col1, btn_col2 = st.columns(INPUT_COL_RATIOS)
with btn_col2:
    st.button("추가", on_click=add_todo, use_container_width=True, type="primary")

st.write("")

# 할 일 목록 및 필터링 탭 구성
st.subheader("📝 할 일 목록")

if total_count == 0:
    st.info("등록된 할 일이 없습니다.")
else:
    tab_all, tab_pending, tab_completed = st.tabs(["전체 보기", "미완료 ⏳", "완료됨 ✅"])
    
    with tab_all:
        render_todo_list(st.session_state.todos, "all")
        
    with tab_pending:
        pending_list: List[Dict[str, Any]] = [t for t in st.session_state.todos if not t["done"]]
        render_todo_list(pending_list, "pending")
        
    with tab_completed:
        completed_list: List[Dict[str, Any]] = [t for t in st.session_state.todos if t["done"]]
        render_todo_list(completed_list, "completed")
