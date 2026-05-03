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

if len(st.session_state['cart']) > 0:
    total_price = 0
    order_text = ""
    
    for idx, item in enumerate(st.session_state['cart']):
        item_total = item['price'] * item['qty']
        total_price += item_total
        st.write(f"- {item['name']} x {item['qty']}개 ({item_total}원)")
        order_text += f"{item['name']} {item['qty']}개, "
    
    st.session_state['total_price'] = total_price
    st.write(f"**💰 총 금액: {total_price}원**")
    
    # 👇 [추가 1] 주문 요청사항 입력칸 (1줄짜리)
    request_msg = st.text_input("📝 주문 요청사항 (선택)", placeholder="예: 덜 맵게 해주세요, 얼음 많이 주세요")
    
    if st.button("🚀 주문 전송하기", type="primary"):
        final_order_text = order_text.rstrip(", ")
        
        # 요청사항이 있으면 텍스트 추가, 없으면 빈칸
        req_text_for_discord = f"**📝 요청사항:** {request_msg}\n" if request_msg else ""
        
        order_message = (
            f"📢 **[태둥포스 새 주문]**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🧾 **주문 내역**\n"
            f"{final_order_text}\n\n"
            f"💰 **결제 금액: {total_price}원**\n"
            f"━━━━━━━━━━━━━━\n"
            f"{req_text_for_discord}" # 여기에 요청사항이 들어갑니다
        )
        
        with st.spinner("주방으로 주문 넣는 중..."):
            result = send_discord_message(order_message)
        
        if result == "성공":
            st.balloons()
            st.success("주문이 완료되었습니다! (디스코드 알림 전송됨)")
            st.session_state['cart'] = []
            # st.rerun()은 지웠으므로 장바구니 리셋 후 바로 새로고침되지 않음
        else:
            st.error(f"주문 실패: {result}")
            
    if st.button("장바구니 비우기"):
        st.session_state['cart'] = []
        st.rerun()

else:
    st.info("아직 담은 메뉴가 없습니다.")

# 7. 특별 주문 및 호출
st.divider()
st.subheader("💡 특별 주문 & 호출")
st.write("메뉴에 없는 음식이나, 주방장 호출이 필요할 때 편하게 메시지를 남겨주세요!")

# 👇 [추가 2] 특별 호출용 여러 줄 입력칸
special_request = st.text_area("어떤 것이 필요하신가요?", placeholder="예: 시원한 물 한 잔만 가져다주세요! / 메뉴에 없는 짜파구리 가능한가요?", height=100)

if st.button("🔔 특별 메시지 전송"):
    if special_request.strip() == "":
        st.warning("내용을 입력해주세요.")
    else:
        special_message = (
            f"🔔 **[태둥포스 특별 호출]**\n"
            f"━━━━━━━━━━━━━━\n"
            f"💬 **요청 내용:**\n"
            f"{special_request}\n"
            f"━━━━━━━━━━━━━━"
        )
        with st.spinner("주방에 메시지 전달 중..."):
            result = send_discord_message(special_message)
        
        if result == "성공":
            st.success("✨ 특별 요청이 주방에 전달되었습니다!")
        else:
            st.error(f"전송 실패: {result}")