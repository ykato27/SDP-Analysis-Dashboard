import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. ダミーデータの生成 (変更なし)
# --------------------------------------------------------------------------------
@st.cache_data
def generate_dummy_data():
    np.random.seed(42)
    num_data = 200

    # 拠点、組織、工程、シフト
    locations = ['日本 (JP)', '拠点A (TH)', '拠点B (US)', '拠点C (MX)']
    teams = ['T1:成形', 'T2:加工', 'T3:組立', 'T4:検査']
    shifts = ['日勤', '夜勤']
    
    # 標準化された共通スキルカテゴリと評価
    skills_info = {
        '成形技術': '成形工程の難易度設定能力',
        'NCプログラム': '加工工程のプログラム作成・修正能力',
        '品質検査': '製品の最終検査基準の遵守と判断能力',
        '設備保全': '日常的な設備点検と簡易修理能力',
        '安全管理': '危険予知・手順遵守能力'
    }
    skill_names = list(skills_info.keys())

    # スキル評価データフレームの生成ロジック
    skill_data = {
        '拠点': np.random.choice(locations, num_data),
        '組織・チーム': np.random.choice(teams, num_data),
        'シフト': np.random.choice(shifts, num_data),
        '従業員ID': [f'EMP_{i+1:03d}' for i in range(num_data)],
    }
    
    for skill_name in skill_names:
        skill_scores = []
        for loc in skill_data['拠点']:
            if loc == '日本 (JP)':
                # 日本はスキル高め (3-5点)
                score = np.random.randint(3, 6)
            elif loc == '拠点A (TH)':
                # タイ拠点は成形・加工スキルに課題あり (1-4点)
                if skill_name in ['成形技術', 'NCプログラム']:
                    score = np.random.randint(1, 4)
                else:
                    score = np.random.randint(2, 5)
            else:
                # その他拠点はバラつきあり (2-4点)
                score = np.random.randint(2, 5)
            skill_scores.append(score)
        skill_data[skill_name] = pd.Series(skill_scores)

    df_skill = pd.DataFrame(skill_data)
    
    # 生産実績データフレームの生成
    df_production = df_skill[['拠点', '組織・チーム', 'シフト', '従業員ID']].copy()
    
    # スキル列を df_production にコピー (総合スキルスコア計算に必要)
    for name in skill_names:
        df_production[name] = df_skill[name]
    
    # 総合スキルスコア (平均)
    df_production['総合スキルスコア'] = df_production[skill_names].mean(axis=1).round(2)
    
    # 生産効率 (Efficiency, KPI): スキルが高いほど高くなる
    df_production['生産効率 (%)'] = (
        60 + 
        df_production['総合スキルスコア'] * 8 + 
        np.random.randn(num_data) * 4 
    ).clip(75, 98).round(1)
    
    # 品質不良率 (Defect Rate, KPI): スキルが高いほど低くなる
    df_production['品質不良率 (%)'] = (
        8 - 
        df_production['総合スキルスコア'] * 1.2 + 
        np.random.randn(num_data) * 1 
    ).clip(0.5, 8).round(1)
    
    # df_productionからKPIと総合スキルスコアのみを抽出
    production_kpi_only = df_production[[
        '拠点', '組織・チーム', 'シフト', '従業員ID', 
        '総合スキルスコア', '生産効率 (%)', '品質不良率 (%)'
    ]].copy()


    return df_skill, production_kpi_only, skills_info, skill_names

# データ生成
df_skill, production_kpi_only, skills_info, skill_names = generate_dummy_data()
df_merged = pd.merge(df_skill, production_kpi_only, on=['拠点', '組織・チーム', 'シフト', '従業員ID'])


# Streamlitアプリケーション本体
# --------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="SDP分析ダッシュボード", page_icon="🏭")

# --- タイトルと説明 ---
st.title('🏭 スキル・データ・プラットフォーム (SDP) 分析ダッシュボード')
st.markdown("##### グローバル拠点における技能職の力量データに基づいた、生産効率・品質改善のためのデータドリブン分析")

# --- サイドバーによるフィルタリング ---
st.sidebar.header('⚙️ データフィルタ')
selected_location = st.sidebar.multiselect(
    '拠点',
    options=df_merged['拠点'].unique(),
    default=df_merged['拠点'].unique()
)
selected_team = st.sidebar.multiselect(
    '組織・チーム',
    options=df_merged['組織・チーム'].unique(),
    default=df_merged['組織・チーム'].unique()
)

df_filtered = df_merged[
    df_merged['拠点'].isin(selected_location) & 
    df_merged['組織・チーム'].isin(selected_team)
]

# --- 全体KPIサマリー (モダンデザイン) ---
total_efficiency = df_filtered['生産効率 (%)'].mean()
total_defect_rate = df_filtered['品質不良率 (%)'].mean()
avg_skill_score = df_filtered['総合スキルスコア'].mean()

st.markdown("---")
st.subheader("📊 主要KPIサマリー (フィルタ適用済み)")

col1, col2, col3, col4 = st.columns(4)

col1.metric("対象従業員数", f"{len(df_filtered)} 名")
col2.metric("平均総合スキルスコア (5点満点)", f"{avg_skill_score:.2f}")
eff_delta = total_efficiency - df_merged['生産効率 (%)'].mean()
col3.metric("平均生産効率", f"{total_efficiency:.1f} %", delta=f"{eff_delta:.1f}")
def_delta = total_defect_rate - df_merged['品質不良率 (%)'].mean()
col4.metric("平均品質不良率", f"{total_defect_rate:.2f} %", delta=f"{def_delta:.2f}", delta_color="inverse")

st.markdown("---")

# --- タブによる分析ステップの表示 ---
tab1, tab2, tab3 = st.tabs(["1. スキルデータ一元管理 (生データ)", "2. ギャップ分析と対策", "3. スキルと生産性 (KPI連携)"])

with tab1:
    st.header('Step 1: スキルデータの一元管理と可視化')
    st.markdown("共通スキルカテゴリと定義に基づき、全拠点のスキルデータを統合します。")
    
    with st.expander("共通スキルカテゴリ定義", expanded=False):
        skill_def_df = pd.DataFrame(skills_info.items(), columns=['スキル名', '定義'])
        st.dataframe(skill_def_df, use_container_width=True)

    st.markdown("##### 📝 従業員別統合スキル評価データ (フィルタ適用済み)")
    st.dataframe(df_filtered.head(20), use_container_width=True, height=500)

with tab2:
    st.header('Step 2: 拠点内/工程間のスキルギャップ詳細分析 🔎')
    st.markdown("グループレベルでの力量のバラつきに加え、**拠点内部のチーム別ギャップ**と**各スキルの習熟度分布**を分析し、具体的な教育ターゲットを特定します。")

    # ----------------------------------------------------
    # A. 拠点別 vs チーム別 スキル平均比較 (ドリルダウン)
    # ----------------------------------------------------
    st.subheader('2.1. 拠点 $\\rightarrow$ 組織・チーム別 スキル平均比較')
    
    # 拠点とチームで集計
    df_pivot = df_filtered.groupby(['拠点', '組織・チーム'])[skill_names].mean().reset_index()
    
    # Plotlyで階層的な棒グラフを作成
    fig_drilldown = px.bar(
        df_pivot, 
        x='組織・チーム', 
        y=skill_names, 
        color='拠点',
        title='組織・チーム別 (工程別) 詳細スキルスコア',
        height=500,
        barmode='group'
    )
    fig_drilldown.update_layout(yaxis_title="平均スキルスコア (5点満点)", legend_title="拠点")
    st.plotly_chart(fig_drilldown, use_container_width=True)
    
    st.info("💡 **分析の深掘り**: 上記チャートで、特定の拠点の特定のチーム（例: **拠点A (TH) の T1:成形**）が、対応するスキル（例: **成形技術**）で他の拠点・チームに比べて低いことが一目で分かります。")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # B. スキル習熟度別 人数分布 (マトリックス分析の準備)
    # ----------------------------------------------------
    st.subheader('2.2. 各スキルカテゴリの習熟度別分布')
    st.markdown("ターゲットとなるチームの、各スキルレベル（1:未習熟 $\\rightarrow$ 5:エキスパート）の**人数構成**を把握します。")
    
    # フィルタリングされたデータに対して、各スキルを習熟度でカウント
    skill_distribution = pd.DataFrame()
    for skill in skill_names:
        count = df_filtered.groupby(skill).size().reset_index(name='人数')
        count['スキル名'] = skill
        skill_distribution = pd.concat([skill_distribution, count])
    
    skill_distribution = skill_distribution.rename(columns={skill_distribution.columns[0]: '習熟度'})
    
    # ヒートマップで可視化
    # 習熟度をカテゴリカルに変換し、順序を確保
    skill_distribution['習熟度'] = skill_distribution['習熟度'].astype(int).astype(str)
    
    fig_heatmap = px.bar(
        skill_distribution,
        x='スキル名',
        y='人数',
        color='習熟度',
        title='全フィルタ対象者のスキル習熟度別人数構成',
        color_discrete_sequence=px.colors.sequential.Viridis_d,
        height=450
    )
    fig_heatmap.update_layout(xaxis_title="スキルカテゴリ", yaxis_title="人数", legend_title="習熟度(1-5)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # ----------------------------------------------------
    # C. 拠点全体のレーダーチャート (旧バージョンから残す)
    # ----------------------------------------------------
    st.subheader('2.3. 拠点全体のスケーラブルレーダーチャート (俯瞰)')
    
    col_c, col_d = st.columns([1, 1.5])

    with col_c:
        # 拠点別詳細スキル平均の集計 (再集計)
        df_skill_pivot = df_filtered.groupby('拠点')[skill_names].mean().reset_index()
        df_skill_pivot['総合平均'] = df_skill_pivot[skill_names].mean(axis=1)
        df_skill_pivot = df_skill_pivot.sort_values('総合平均', ascending=False).set_index('拠点').round(2)
        st.markdown("##### 拠点別 スキル評価スコア比較 (サマリー)")
        st.dataframe(df_skill_pivot, use_container_width=True)

    with col_d:
        st.markdown("##### 拠点別 スキルレーダーチャート (ギャップ可視化)")
        radar_df = df_skill_pivot.drop(columns=['総合平均']).reset_index()
        fig_radar = go.Figure()
        
        for index, row in radar_df.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=row[skill_names].values,
                theta=skill_names,
                fill='toself',
                name=row['拠点']
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
            showlegend=True,
            height=450,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.success(
        "**次なるアクション**: セクション2.1で特定した**課題チーム**と、セクション2.2で特定した**低習熟度スキル**の交点（例: 拠点A-T1:成形チームの成形技術スコア1-2の人）に対し、具体的なトレーニング計画（OJTやe-ラーニング）を策定します。", icon="🎯"
    )

st.markdown("---")

with tab3:
    st.header('Step 3: スキルと生産データを紐づけた分析 (KPI管理)')
    st.markdown("スキルレベルが生産効率や品質に与える影響を分析し、**データ駆動型の工場運営**を実現します。")

    col_kpi1, col_kpi2 = st.columns(2)

    with col_kpi1:
        st.markdown("##### スキル vs 生産効率 (%) - 散布図")
        fig_eff = px.scatter(
            df_filtered,
            x='総合スキルスコア',
            y='生産効率 (%)',
            color='拠点',
            hover_data=['従業員ID', '組織・チーム'],
            trendline='ols',
            title='総合スキルと生産効率の相関'
        )
        st.plotly_chart(fig_eff, use_container_width=True)
        st.info(f"**相関係数 (Eff)**: {df_filtered['総合スキルスコア'].corr(df_filtered['生産効率 (%)']):.3f} (プラス相関) -> スキルが効率に寄与。", icon="✔️")

    with col_kpi2:
        st.markdown("##### スキル vs 品質不良率 (%) - 散布図")
        fig_def = px.scatter(
            df_filtered,
            x='総合スキルスコア',
            y='品質不良率 (%)',
            color='拠点',
            hover_data=['従業員ID', '組織・チーム'],
            trendline='ols',
            title='総合スキルと品質不良率の相関'
        )
        st.plotly_chart(fig_def, use_container_width=True)
        st.info(f"**相関係数 (Def)**: {df_filtered['総合スキルスコア'].corr(df_filtered['品質不良率 (%)']):.3f} (マイナス相関) -> スキルが不良率低下に寄与。", icon="✔️")

    st.markdown("---")
    st.subheader('🎯 最適な配置、教育の実行に向けたKPIとスキルレベルの統合')
    
    kpi_skill_summary = df_filtered.groupby('拠点').agg(
        {'生産効率 (%)': 'mean', '品質不良率 (%)': 'mean', '総合スキルスコア': 'mean'}
    ).reset_index()
    
    fig_bar = px.bar(
        kpi_skill_summary,
        x='拠点',
        y='生産効率 (%)',
        color='総合スキルスコア',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='拠点別 生産効率とスキルレベルの関係'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.success(
        "**次なるアクション**: スキルスコアが低く、かつKPIが低い拠点（例: **拠点A (TH)**）を特定し、その拠点へ「成形技術」の高い日本の技術者を短期派遣するか、またはオンライン教育プログラムを重点的に割り当てるなど、**最適な配置・教育施策**を実行します。",
        icon="🚀"
    )

st.markdown("---")
st.caption("© SDP Simulation Dashboard (Powered by Streamlit)")