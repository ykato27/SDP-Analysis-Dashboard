import streamlit as st
from data_loader import generate_dummy_data
from views.welcome import show_welcome_screen
from views.executive_summary import show_executive_summary
from views.root_cause_analysis import show_root_cause_analysis
from views.quality_skill_analysis import show_quality_skill_analysis
from views.action_plan import show_action_plan
from views.monitoring import show_monitoring_dashboard
from views.raw_data import show_raw_data
from utils.styles import apply_custom_styles

# ページ設定（最初に実行）
st.set_page_config(
    layout="wide", 
    page_title="Skillnote - SDP分析", 
    page_icon="✏️",
    initial_sidebar_state="expanded"
)

# カスタムスタイルの適用
apply_custom_styles()

# --------------------------------------------------------------------------------
# セッション状態の初期化
# --------------------------------------------------------------------------------

if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "🏠 ホーム"

if 'target_location' not in st.session_state:
    st.session_state.target_location = None

if 'priority_skill' not in st.session_state:
    st.session_state.priority_skill = None

# --------------------------------------------------------------------------------
# データ読み込み
# --------------------------------------------------------------------------------

@st.cache_data
def load_data():
    """データをキャッシュして読み込み"""
    df_skill, df_daily_prod, skill_hierarchy, all_skills, skill_to_category, skill_categories, processes = generate_dummy_data()
    return df_skill, df_daily_prod, skill_hierarchy, all_skills, skill_to_category, skill_categories, processes

# データをロード
try:
    df_skill, df_daily_prod, skill_hierarchy, all_skills, skill_to_category, skill_categories, processes = load_data()
except Exception as e:
    st.error(f"データロードエラー: {str(e)}")
    st.stop()

# --------------------------------------------------------------------------------
# サイドバー: SDP分析メニュー
# --------------------------------------------------------------------------------

with st.sidebar:
    st.markdown("# ✏️ Skillnote")
    st.markdown("#### スキル・データ・プラットフォーム")
    st.markdown("---")
    
    st.markdown("### 📊 SDP分析メニュー")
    st.markdown("グローバル拠点のスキルギャップ分析と生産性改善")
    
    st.markdown("---")
    
    # メインメニュー
    menu_items = {
        "🏠 ホーム": {
            "description": "ウェルカム画面",
            "icon": "🏠"
        },
        "📊 エグゼクティブサマリー": {
            "description": "経営判断のための全体サマリー",
            "icon": "📊"
        },
        "🔬 根本原因分析": {
            "description": "スキルギャップの詳細分析",
            "icon": "🔬"
        },
        "📈 品質×力量分析": {
            "description": "歩留まりとスキルの時系列分析",
            "icon": "📈"
        },
        "📋 アクションプラン": {
            "description": "具体的な改善施策の提示",
            "icon": "📋"
        },
        "📉 継続モニタリング": {
            "description": "KPI追跡とアラート",
            "icon": "📉"
        },
        "📁 生データ閲覧": {
            "description": "元データの参照・ダウンロード",
            "icon": "📁"
        }
    }
    
    # メニューボタンを生成
    for menu_key, menu_info in menu_items.items():
        if st.button(
            menu_key,
            key=f"menu_{menu_key}",
            use_container_width=True,
            type="primary" if st.session_state.selected_menu == menu_key else "secondary"
        ):
            st.session_state.selected_menu = menu_key
            st.rerun()
    
    st.markdown("---")
    
    # 拠点フィルター（ホーム以外で表示）
    if st.session_state.selected_menu != "🏠 ホーム":
        st.markdown("### 🎯 分析対象設定")
        
        overseas_locations = [loc for loc in df_skill['拠点'].unique() if loc != '日本 (JP)']
        
        selected_location = st.selectbox(
            '詳細分析対象拠点',
            options=overseas_locations,
            index=0 if st.session_state.target_location is None else overseas_locations.index(st.session_state.target_location) if st.session_state.target_location in overseas_locations else 0
        )
        
        if selected_location != st.session_state.target_location:
            st.session_state.target_location = selected_location
    
    st.markdown("---")
    
    # フッター情報
    st.markdown("### ℹ️ システム情報")
    st.info("**システム管理者**\n\nログイン中", icon="👤")
    
    with st.expander("📚 ヘルプ・ガイド"):
        st.markdown("""
        **使い方:**
        1. エグゼクティブサマリーで全体を把握
        2. 根本原因分析で課題を特定
        3. アクションプランで施策を決定
        4. モニタリングで効果を追跡
        """)

# --------------------------------------------------------------------------------
# メインコンテンツエリア
# --------------------------------------------------------------------------------

# 選択されたメニューに応じてビューを表示
if st.session_state.selected_menu == "🏠 ホーム":
    show_welcome_screen()

elif st.session_state.selected_menu == "📊 エグゼクティブサマリー":
    df_summary = show_executive_summary(df_skill, df_daily_prod)
    # サマリー情報をセッション状態に保存
    if df_summary is not None and not df_summary.empty:
        st.session_state.df_summary = df_summary

elif st.session_state.selected_menu == "🔬 根本原因分析":
    if st.session_state.target_location:
        priority_skill = show_root_cause_analysis(
            df_skill, 
            st.session_state.target_location,
            all_skills,
            skill_to_category,
            skill_categories,
            skill_hierarchy,
            processes
        )
        st.session_state.priority_skill = priority_skill
    else:
        st.warning("分析対象拠点を選択してください。", icon="⚠️")

elif st.session_state.selected_menu == "📈 品質×力量分析":
    if st.session_state.target_location:
        show_quality_skill_analysis(
            df_daily_prod,
            df_skill,
            st.session_state.target_location,
            skill_categories,
            skill_hierarchy,
            processes
        )
    else:
        st.warning("分析対象拠点を選択してください。", icon="⚠️")

elif st.session_state.selected_menu == "📋 アクションプラン":
    if st.session_state.target_location:
        priority_skill = st.session_state.priority_skill if st.session_state.priority_skill else "製銑 - 設備操作"
        show_action_plan(
            df_skill, 
            st.session_state.target_location,
            priority_skill
        )
    else:
        st.warning("分析対象拠点を選択してください。", icon="⚠️")

elif st.session_state.selected_menu == "📉 継続モニタリング":
    if st.session_state.target_location:
        show_monitoring_dashboard(
            df_daily_prod,
            st.session_state.target_location
        )
    else:
        st.warning("分析対象拠点を選択してください。", icon="⚠️")

elif st.session_state.selected_menu == "📁 生データ閲覧":
    show_raw_data(df_skill, df_daily_prod)

# フッター
st.markdown("---")
st.caption("© Skillnote SDP Analysis Dashboard | Designed for Strategic Decision Making")