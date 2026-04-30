import streamlit as st
import menu_data as md
from discord_utils import send_discord_message
import os
from dotenv import load_dotenv
from PIL import Image

# 1. 설정 불러오기
load_dotenv()

# ==========================================
# 👇 수정된 부분: 비밀번호 가져오기 (try-except 추가)
# ==========================================
PASSWORD = "password" # 기본값

try:
    # 클라우드에 비밀번호가 설정되어 있으면 그걸 씀
    if "PASSWORD" in st.secrets:
        PASSWORD = st.secrets["PASSWORD"]
except FileNotFoundError:
    # 로컬이라서 secrets 파일이 없으면 .env에서 찾음
    PASSWORD = os.getenv("PASSWORD", "password")
except Exception:
    # 그 외 에러나면 .env 사용
    PASSWORD = os.getenv("PASSWORD", "password")

# 이미지 로드 함수 (그대로 유지)
def load_logo(image_path, width=300):
    try:
        img = Image.open(image_path)
        height = int(width * img.height / img.width)
        img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
        return img_resized
    except Exception as e:
        return None

# 2. 페이지 설정
st.set_page_config(page_title="태둥포스 PC방", page_icon="🎮")

# 3. 세션 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'cart' not in st.session_state:
    st.session_state['cart'] = []
if 'total_price' not in st.session_state:
    st.session_state['total_price'] = 0

# 4. 로그인 화면
if not st.session_state['logged_in']:
    if os.path.exists("logo.png"):
        logo_img = load_logo("logo.png", width=300)
        if logo_img:
            st.image(logo_img, use_container_width=False)
    
    st.title("🎮 태둥포스 PC방 입장")
    st.write("태둥❤️쭈리네 전용 주문 시스템입니다.")
    
    input_pass = st.text_input("입장 코드(비밀번호)를 입력하세요", type="password")
    
    if st.button("입장하기"):
        if input_pass == PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다!")
    st.stop()

# 5. 메인 주문 화면
st.title("🎮 태둥포스 PC방 메뉴판")
st.write("원하는 메뉴를 담고 주문 버튼을 눌러주세요!")

# ------------------------------------------
# 👇 [추가됨] 담기 버튼을 눌렀을 때 실행될 함수
# ------------------------------------------
def add_to_cart(key, name, price):
    # 세션 상태에서 현재 입력된 개수를 가져옴
    qty = st.session_state[key]
    
    if qty > 0:
        # 장바구니에 추가
        st.session_state['cart'].append({"name": name, "qty": qty, "price": price})
        # 입력창 숫자를 0으로 초기화 (이게 핵심!)
        st.session_state[key] = 0
        # 성공 메시지를 잠깐 띄움 (토스트 메시지)
        st.toast(f"✅ {name} {qty}개 담기 완료!", icon="🛒")
    else:
        st.toast("⚠️ 개수를 1개 이상 선택해주세요.", icon="❗")

# 메뉴 데이터 확인 및 탭 생성
if hasattr(md, 'menu'):
    menu = md.menu
else:
    st.warning("메뉴 데이터를 불러오지 못했습니다.")
    menu = {}

if menu:
    category_list = list(menu.keys()) 
    tabs = st.tabs(category_list)
    for i, category in enumerate(menu.keys()):
        with tabs[i]:
            st.subheader(f"😋 {category}")
            items = menu[category]
            for item_name, price in items.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                # 고유 키 생성
                key_name = f"{category}_{item_name}"
                
                with col1:
                    st.write(f"**{item_name}** ({price}원)")
                with col2:
                    # 여기서는 값을 받지 않고 위젯만 그려둠 (값은 session_state에서 관리)
                    st.number_input("개수", min_value=0, max_value=10, key=key_name, label_visibility="collapsed")
                with col3:
                    # 👇 [변경됨] 버튼에 'on_click'을 달아서 함수를 연결
                    st.button("담기", 
                              key=f"btn_{key_name}", 
                              on_click=add_to_cart,     # 버튼 누르면 이 함수 실행해!
                              args=(key_name, item_name, price)) # 이 재료들을 가지고!

# 6. 장바구니 및 주문 전송
st.divider()
st.subheader("🛒 장바구니")

# 장바구니에 아이템이 있을 때만 표시
if len(st.session_state['cart']) > 0:
    total_price = 0
    order_text = ""
    
    # 장바구니 목록 출력
    for idx, item in enumerate(st.session_state['cart']):
        item_total = item['price'] * item['qty']
        total_price += item_total
        st.write(f"- {item['name']} x {item['qty']}개 ({item_total}원)")
        order_text += f"{item['name']} {item['qty']}개, "
    
    # 총 금액 저장 및 출력
    st.session_state['total_price'] = total_price
    st.write(f"**💰 총 금액: {total_price}원**")
    
    # 주문 버튼
    if st.button("🚀 주문 전송하기", type="primary"):
        final_order_text = order_text.rstrip(", ")
        
        # 디스코드 메시지 양식
        order_message = (
            f"📢 **[태둥포스 새 주문]**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🧾 **주문 내역**\n"
            f"{final_order_text}\n\n"
            f"💰 **결제 금액: {total_price}원**\n"
            f"━━━━━━━━━━━━━━"
        )
        
        with st.spinner("주방으로 주문 넣는 중..."):
            result = send_discord_message(order_message)
        
        if result == "성공":
            # 1. 풍선 날리기 🎈
            st.balloons()
            
            # 2. 성공 메시지 (녹색 상자)
            st.success("주문이 완료되었습니다! (디스코드 알림 전송됨)")
            
            # 3. 장바구니 데이터는 비우지만, 화면은 바로 새로고침하지 않음
            st.session_state['cart'] = [] 
            
            # ❌ st.rerun() <--- 이 코드를 삭제했습니다! 
            # 이제 풍선과 메시지가 사라지지 않고 계속 보입니다.
            
        else:
            st.error(f"주문 실패: {result}")
            
    # 비우기 버튼 (이건 누르면 바로 지워져야 하니 rerun 유지)
    if st.button("장바구니 비우기"):
        st.session_state['cart'] = []
        st.rerun()

else:
    st.info("아직 담은 메뉴가 없습니다.")