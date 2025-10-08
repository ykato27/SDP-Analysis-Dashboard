import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

# 外部ファイルからデータ生成関数のみをインポート
try:
    from data_loader import generate_dummy_data
except ModuleNotFoundError:
    st.error("エラー: data_loader.py が見つかりません。app.py と同じフォルダに配置してください。", icon="🔥")
    st.stop()


# ページ設定（最初に実行）
st.set_page_config(
    layout="wide", 
    page_title="Skillnote - SDP管理", 
    page_icon="✏️",
    initial_sidebar_state="expanded"
)

# カスタムCSS（Skillnote風のスタイル）
st.markdown("""
<style>
    /* サイドバーのスタイリング */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #2e7d32;
        font-size: 1.5rem;
        font-weight: 600;
        padding: 0.5rem 0;
    }
    
    /* メインコンテンツエリア */
    .main {
        background-color: #fafafa;
    }
    
    /* ヘッダー部分 */
    .header-container {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* メトリクスカードのスタイリング */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetric"] label {
        font-size: 0.9rem !important;
        color: #666 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* テーブルのスタイリング */
    .dataframe {
        border: none !important;
    }
    
    .dataframe thead tr th {
        background-color: #f5f5f5 !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f9fbe7 !important;
    }
    
    /* タブのスタイリング */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    
    /* ボタンのスタイリング */
    .stButton button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
    }
    
    .stButton button:hover {
        background-color: #1b5e20;
    }
    
    /* ウェルカムカード */
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .welcome-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .welcome-icon {
        font-size: 3rem;
        color: #c8e6c9;
        margin-bottom: 1rem;
    }
    
    .welcome-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .welcome-desc {
        font-size: 0.95rem;
        color: #666;
        line-height: 1.6;
    }
    
    /* アラート・情報ボックス */
    .stAlert {
        border-radius: 10px;
    }
    
    /* エクスパンダー */
    .streamlit-expanderHeader {
        background-color: #f5f5f5;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------------
# エグゼクティブサマリー: 経営判断に必要な情報を凝縮
# --------------------------------------------------------------------------------

def show_executive_summary(df_skill, df_daily_prod):
    """経営層向けエグゼクティブサマリー"""
    
    # ヘッダー
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📊 エグゼクティブサマリー</div>
        <div class="header-subtitle">グローバル製造拠点の生産性格差とスキル起因の損失額</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ベンチマーク拠点（日本）との比較
    jp_efficiency = df_skill[df_skill['拠点'] == '日本 (JP)']['生産効率 (%)'].mean()
    jp_defect = df_skill[df_skill['拠点'] == '日本 (JP)']['品質不良率 (%)'].mean()
    jp_skill = df_skill[df_skill['拠点'] == '日本 (JP)']['総合スキルスコア'].mean()
    
    # 拠点別の損失試算
    location_summary = []
    for loc in df_skill['拠点'].unique():
        if loc == '日本 (JP)':
            continue
        
        df_loc = df_skill[df_skill['拠点'] == loc]
        efficiency_gap = jp_efficiency - df_loc['生産効率 (%)'].mean()
        defect_gap = df_loc['品質不良率 (%)'].mean() - jp_defect
        skill_gap = jp_skill - df_loc['総合スキルスコア'].mean()
        
        # 損失試算（仮定：月間生産額10億円/拠点）
        monthly_production_value = 1000  # 百万円
        efficiency_loss = monthly_production_value * (efficiency_gap / 100)
        defect_loss = monthly_production_value * (defect_gap / 100) * 1.5
        total_loss = efficiency_loss + defect_loss
        annual_loss = total_loss * 12
        
        # 教育投資でのROI試算
        employee_count = len(df_loc)
        training_cost_per_person = 0.5  # 百万円/人
        total_training_cost = employee_count * training_cost_per_person
        roi = (annual_loss / total_training_cost) if total_training_cost > 0 else 0
        payback_months = (total_training_cost / total_loss) if total_loss > 0 else 999
        
        location_summary.append({
            '拠点': loc,
            '従業員数': employee_count,
            'スキルギャップ': skill_gap,
            '効率ギャップ (%)': efficiency_gap,
            '不良率ギャップ (%)': defect_gap,
            '月間損失額 (M¥)': total_loss,
            '年間損失額 (M¥)': annual_loss,
            '教育投資額 (M¥)': total_training_cost,
            'ROI': roi,
            '投資回収期間 (月)': payback_months
        })
    
    df_summary = pd.DataFrame(location_summary)
    
    # 重要指標のハイライト
    total_annual_loss = df_summary['年間損失額 (M¥)'].sum()
    total_training_cost = df_summary['教育投資額 (M¥)'].sum()
    avg_roi = df_summary['ROI'].mean()
    avg_payback = total_training_cost / (total_annual_loss / 12)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🔴 年間推定損失額", 
            f"¥{total_annual_loss:.0f}M",
            help="ベンチマーク(日本)との生産性格差による"
        )
    
    with col2:
        st.metric(
            "💰 必要教育投資", 
            f"¥{total_training_cost:.0f}M",
            help="スキルギャップ解消のための投資額"
        )
    
    with col3:
        st.metric(
            "📈 期待ROI", 
            f"{avg_roi:.1f}x",
            help="教育投資に対するリターン"
        )
    
    with col4:
        st.metric(
            "⏱️ 投資回収期間", 
            f"{avg_payback:.1f}ヶ月",
            help="平均的な投資回収期間"
        )
    
    st.markdown("---")
    
    # 優先度スコアリング
    df_summary['損失額_正規化'] = df_summary['年間損失額 (M¥)'] / df_summary['年間損失額 (M¥)'].max()
    df_summary['ROI_正規化'] = df_summary['ROI'] / df_summary['ROI'].max()
    df_summary['優先度スコア'] = (df_summary['損失額_正規化'] * 0.6 + df_summary['ROI_正規化'] * 0.4) * 100
    
    def get_priority(score):
        if score > 70:
            return '🔴 最優先'
        elif score > 50:
            return '🟡 優先'
        else:
            return '🟢 中期対応'
    
    df_summary['優先度'] = df_summary['優先度スコア'].apply(get_priority)
    df_summary = df_summary.sort_values('優先度スコア', ascending=False)
    
    st.subheader('🎯 拠点別 優先順位マトリクス')
    
    # 表示用にフォーマット
    df_display = df_summary[['優先度', '拠点', '従業員数', 'スキルギャップ', '年間損失額 (M¥)', '教育投資額 (M¥)', 'ROI', '投資回収期間 (月)']].copy()
    df_display['スキルギャップ'] = df_display['スキルギャップ'].apply(lambda x: f"{x:.2f}")
    df_display['年間損失額 (M¥)'] = df_display['年間損失額 (M¥)'].apply(lambda x: f"¥{x:.0f}M")
    df_display['教育投資額 (M¥)'] = df_display['教育投資額 (M¥)'].apply(lambda x: f"¥{x:.1f}M")
    df_display['ROI'] = df_display['ROI'].apply(lambda x: f"{x:.1f}x")
    df_display['投資回収期間 (月)'] = df_display['投資回収期間 (月)'].apply(lambda x: f"{x:.1f}ヶ月")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(
        "💡 **経営判断のポイント**: 最優先拠点（🔴）から教育投資を実行することで、最短6ヶ月で投資回収が見込まれます。"
        f"特に**{df_summary.iloc[0]['拠点']}**は損失額が大きく、ROIも高いため、即座のアクション推奨。",
        icon="💼"
    )
    
    return df_summary


# --------------------------------------------------------------------------------
# ウェルカム画面
# --------------------------------------------------------------------------------

def show_welcome_screen():
    """初期表示のウェルカム画面"""
    
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; color: #333; font-weight: 600; margin-bottom: 0.5rem;">
            メンバーの力量を
        </h1>
        <h1 style="font-size: 2.5rem; color: #333; font-weight: 600; margin-bottom: 3rem;">
            シートで管理してみましょう。
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">🏠</div>
            <div class="welcome-title">プロジェクトを設定</div>
            <div class="welcome-desc">
                企業や工場、部署など、管理したい組織単位でプロジェクトを作成してみましょう。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">📊</div>
            <div class="welcome-title">シートを作成</div>
            <div class="welcome-desc">
                メンバーの力量マップや育成計画、個人力量を管理するシートを作成できます。運用にそってシートを使い分けてみてください。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">✏️</div>
            <div class="welcome-title">運用開始</div>
            <div class="welcome-desc">
                シートを作成したらメンバーにスキルや教育・資格を登録したり、育成計画の記録をつけてみましょう。
            </div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------------------------------------
# 根本原因分析
# --------------------------------------------------------------------------------

def show_root_cause_analysis(df_skill, target_location):
    """特定拠点の根本原因分析"""
    
    st.markdown(f"## 🔬 根本原因分析: {target_location}")
    st.markdown("##### スキルギャップの具体的な原因と、ボトルネックとなっている従業員・シフト・スキル項目を特定")
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    df_benchmark = df_skill[df_skill['拠点'] == '日本 (JP)'].copy()
    
    skill_names = ['成形技術', 'NCプログラム', '品質検査', '設備保全', '安全管理']
    
    # スキル別ギャップ分析
    st.markdown("### 📉 スキルカテゴリ別ギャップ分析")
    
    skill_gap_data = []
    for skill in skill_names:
        target_mean = df_target[skill].mean()
        benchmark_mean = df_benchmark[skill].mean()
        gap = benchmark_mean - target_mean
        impact_weight = {
            '成形技術': 1.5,
            'NCプログラム': 1.3,
            '品質検査': 1.4,
            '設備保全': 1.2,
            '安全管理': 1.0
        }
        weighted_gap = gap * impact_weight.get(skill, 1.0)
        
        priority = '🔴 最優先' if weighted_gap > 0.8 else ('🟡 優先' if weighted_gap > 0.5 else '🟢 中')
        
        skill_gap_data.append({
            'スキル': skill,
            '当拠点平均': f"{target_mean:.2f}",
            'ベンチマーク': f"{benchmark_mean:.2f}",
            'ギャップ': f"{gap:.2f}",
            '影響度加味': f"{weighted_gap:.2f}",
            '改善優先度': priority
        })
    
    df_skill_gap = pd.DataFrame(skill_gap_data)
    st.dataframe(df_skill_gap, use_container_width=True, hide_index=True)
    
    # 最も課題のあるスキルを特定
    priority_skill_row = df_skill_gap.iloc[0]
    priority_skill = priority_skill_row['スキル']
    
    st.markdown(f"### 🎯 最優先改善スキル: **{priority_skill}**")
    
    # 習熟度分布比較
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {target_location} の分布")
        target_dist = df_target[priority_skill].value_counts().sort_index()
        fig_target = px.bar(
            x=target_dist.index,
            y=target_dist.values,
            labels={'x': '習熟度', 'y': '人数'},
            title=f'{priority_skill} 習熟度分布',
            color=target_dist.values,
            color_continuous_scale='Reds'
        )
        fig_target.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_target, use_container_width=True)
        
        low_skill_count = df_target[df_target[priority_skill] <= 2].shape[0]
        st.error(f"⚠️ レベル2以下: **{low_skill_count}名** ({low_skill_count/len(df_target)*100:.1f}%)", icon="🚨")
    
    with col2:
        st.markdown("#### ベンチマーク (日本) の分布")
        bench_dist = df_benchmark[priority_skill].value_counts().sort_index()
        fig_bench = px.bar(
            x=bench_dist.index,
            y=bench_dist.values,
            labels={'x': '習熟度', 'y': '人数'},
            title=f'{priority_skill} 習熟度分布',
            color=bench_dist.values,
            color_continuous_scale='Greens'
        )
        fig_bench.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_bench, use_container_width=True)
        
        bench_low = df_benchmark[df_benchmark[priority_skill] <= 2].shape[0]
        st.success(f"✅ レベル2以下: **{bench_low}名** ({bench_low/len(df_benchmark)*100:.1f}%)", icon="✨")
    
    return priority_skill


# --------------------------------------------------------------------------------
# アクションプラン
# --------------------------------------------------------------------------------

def show_action_plan(df_skill, target_location, priority_skill):
    """具体的なアクションプランの提示"""
    
    st.markdown("## 📋 アクションプラン: 実行可能な施策")
    st.markdown(f"##### {target_location} における {priority_skill} スキル改善の具体的施策")
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    
    st.markdown("### 💡 推奨施策パッケージ（優先順位順）")
    
    action_plans = [
        {
            '施策': '🎯 即効施策',
            '内容': '日本からの技術者短期派遣',
            '対象': '最優先ボトルネックチーム',
            '期間': '2週間 x 2回',
            'コスト': '¥3.0M',
            '効果': 'スキル +0.8pt, 効率 +5%pt',
            '実施時期': '即時 (来月から)',
            'KPI': '3ヶ月後に生産効率85%達成'
        },
        {
            '施策': '📚 中期施策',
            '内容': 'オンライン教育プログラム展開',
            '対象': f'{priority_skill}がレベル2以下の全従業員',
            '期間': '3ヶ月間 (週2時間)',
            'コスト': '¥5.0M',
            '効果': 'スキル +1.2pt, 効率 +8%pt',
            '実施時期': '2ヶ月後開始',
            'KPI': '6ヶ月後にスキル平均3.5達成'
        },
        {
            '施策': '👥 構造施策',
            '内容': 'ベテラン-若手ペアリング制度',
            '対象': '全チーム',
            '期間': '継続的',
            'コスト': '¥1.0M',
            '効果': 'スキルバラツキ -30%',
            '実施時期': '3ヶ月後',
            'KPI': '1年後にスキルバラツキ<0.5達成'
        },
        {
            '施策': '🔄 リスク対応',
            '内容': 'シフト間ローテーション',
            '対象': '低スキル者',
            '期間': '3ヶ月トライアル',
            'コスト': '¥0.5M',
            '効果': 'シフト間格差 -40%',
            '実施時期': '即時可能',
            'KPI': 'シフト間効率差<3%pt'
        }
    ]
    
    df_actions = pd.DataFrame(action_plans)
    st.dataframe(df_actions, use_container_width=True, hide_index=True)
    
    # 投資対効果シミュレーション
    st.markdown("### 📊 投資対効果シミュレーション")
    
    total_cost = 3.0 + 5.0 + 1.0 + 0.5
    expected_efficiency_gain = 5 + 8
    monthly_production = 1000
    monthly_benefit = monthly_production * (expected_efficiency_gain / 100)
    payback = total_cost / monthly_benefit
    
    col1, col2, col3 = st.columns(3)
    col1.metric("総投資額", f"¥{total_cost:.1f}M")
    col2.metric("月間効果額", f"¥{monthly_benefit:.1f}M")
    col3.metric("投資回収期間", f"{payback:.1f}ヶ月")
    
    st.success(
        "✅ **実行承認の判断材料**: 全施策を実行した場合、約3.5ヶ月で投資回収が完了し、"
        "年間で約¥100M以上の利益改善が見込まれます。即時実行を推奨。",
        icon="💼"
    )


# --------------------------------------------------------------------------------
# メインアプリケーション
# --------------------------------------------------------------------------------

def main():
    # データ生成
    df_skill, df_daily_prod, skills_info, skill_names = generate_dummy_data()
    
    # サイドバーメニュー
    with st.sidebar:
        st.markdown("# ✏️ Skillnote")
        st.markdown("---")
        
        # メニュー選択
        menu_option = st.radio(
            "📋 メニュー",
            [
                "🏠 ホーム",
                "📊 力量管理",
                "👤 個人力量",
                "📈 人員計画",
                "💾 データ管理",
                "⚙️ 設定"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 力量管理のサブメニュー
        if menu_option == "📊 力量管理":
            st.markdown("### 📂 力量管理")
            
            with st.expander("▼ 01_製造部", expanded=True):
                sub_menu = st.radio(
                    "製造部メニュー",
                    [
                        "力量マップ",
                        "資格マップ",
                        "社内認定資格",
                        "全社研修マップ",
                        "育成計画リスト",
                        "個人力量リスト",
                        "キャリア管理"
                    ],
                    label_visibility="collapsed"
                )
            
            with st.expander("▼ 01_加工課"):
                st.write("・力量マップ")
                st.write("・資格マップ")
            
            with st.expander("▼ 02_組立課"):
                st.write("・スキルマップ")
                st.write("・資格マップ")
        
        st.markdown("---")
        st.markdown("### 🔍 ガイド")
        st.markdown("### 👤 Myページ")
        
        st.markdown("---")
        st.info("**システム管理者**", icon="👤")
    
    # メインコンテンツ
    if menu_option == "🏠 ホーム":
        show_welcome_screen()
    
    elif menu_option == "📊 力量管理":
        if 'sub_menu' in locals() and sub_menu == "力量マップ":
            # タブ構成
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 エグゼクティブサマリー",
                "🔬 根本原因分析",
                "📋 アクションプラン",
                "📁 生データ"
            ])
            
            with tab1:
                df_summary = show_executive_summary(df_skill, df_daily_prod)
            
            with tab2:
                # 拠点選択
                overseas_locations = [loc for loc in df_skill['拠点'].unique() if loc != '日本 (JP)']
                target_location = st.selectbox(
                    '🎯 詳細分析対象拠点',
                    options=overseas_locations,
                    index=0
                )
                priority_skill = show_root_cause_analysis(df_skill, target_location)
            
            with tab3:
                if 'target_location' not in locals():
                    target_location = overseas_locations[0]
                if 'priority_skill' not in locals():
                    priority_skill = '成形技術'
                show_action_plan(df_skill, target_location, priority_skill)
            
            with tab4:
                st.markdown("## 📁 生データ閲覧")
                
                data_type = st.radio("表示データ", ["従業員スキルデータ", "日次生産データ"], horizontal=True)
                
                if data_type == "従業員スキルデータ":
                    st.dataframe(df_skill, use_container_width=True, height=600)
                else:
                    st.dataframe(df_daily_prod, use_container_width=True, height=600)
        else:
            st.info(f"**{sub_menu}** 機能は開発中です。", icon="🚧")
    
    else:
        st.info(f"**{menu_option}** 機能は開発中です。", icon="🚧")
    
    # フッター
    st.markdown("---")
    st.caption("© Skillnote SDP Dashboard | Designed for Strategic Decision Making")


if __name__ == "__main__":
    main()