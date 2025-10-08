import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. ダミーデータの生成 (スキルとチームの関連性を複雑化)
# --------------------------------------------------------------------------------
@st.cache_data
def generate_dummy_data():
    np.random.seed(42)
    num_data = 200

    locations = ['日本 (JP)', '拠点A (TH)', '拠点B (US)', '拠点C (MX)']
    teams = ['T1:成形', 'T2:加工', 'T3:組立', 'T4:検査']
    shifts = ['日勤', '夜勤']
    
    skills_info = {
        '成形技術': '成形工程の難易度設定能力',
        'NCプログラム': '加工工程のプログラム作成・修正能力',
        '品質検査': '製品の最終検査基準の遵守と判断能力',
        '設備保全': '日常的な設備点検と簡易修理能力',
        '安全管理': '危険予知・手順遵守能力'
    }
    skill_names = list(skills_info.keys())

    skill_data = {
        '拠点': np.random.choice(locations, num_data),
        '組織・チーム': np.random.choice(teams, num_data),
        'シフト': np.random.choice(shifts, num_data),
        '従業員ID': [f'EMP_{i+1:03d}' for i in range(num_data)],
    }
    
    df_temp = pd.DataFrame(skill_data)

    for skill_name in skill_names:
        scores = []
        for index, row in df_temp.iterrows():
            loc = row['拠点']
            team = row['組織・チーム']
            
            # チームとスキルの関連性に基づいたスコア調整
            score = np.random.randint(2, 4) # ベーススコア (2-3)
            
            if skill_name == '成形技術' and team == 'T1:成形':
                score += np.random.randint(1, 3) # T1の成形技術は高い
            
            elif skill_name == 'NCプログラム' and team in ['T1:成形', 'T2:加工']:
                score += np.random.randint(1, 2) # T1, T2はNCプログラムが高い
            
            elif skill_name in ['品質検査', '設備保全', '安全管理'] and team in ['T1:成形', 'T2:加工', 'T3:組立']:
                score += np.random.randint(0, 2) # 共通スキルはT1-T3で平均的
                
            # 拠点による調整
            if loc == '日本 (JP)':
                score += 1 
            elif loc == '拠点A (TH)' and score > 2:
                score -= 1 # 課題拠点のスコアを意図的に下げる

            scores.append(np.clip(score + np.random.randint(-1, 2), 1, 5)) # スコアを1-5にクリップし、ランダムなばらつきを追加
        
        skill_data[skill_name] = pd.Series(scores).astype(int)

    df_skill = pd.DataFrame(skill_data)
    
    # 生産実績データフレームの生成 (総合スキルスコアの計算にすべてのスキルを使用)
    df_production = df_skill[['拠点', '組織・チーム', 'シフト', '従業員ID']].copy()
    for name in skill_names:
        df_production[name] = df_skill[name]
    
    df_production['総合スキルスコア'] = df_production[skill_names].mean(axis=1).round(2)
    df_production['生産効率 (%)'] = (60 + df_production['総合スキルスコア'] * 8 + np.random.randn(num_data) * 4).clip(75, 98).round(1)
    df_production['品質不良率 (%)'] = (8 - df_production['総合スキルスコア'] * 1.2 + np.random.randn(num_data) * 1).clip(0.5, 8).round(1)
    
    production_kpi_only = df_production[['拠点', '組織・チーム', 'シフト', '従業員ID', '総合スキルスコア', '生産効率 (%)', '品質不良率 (%)']].copy()

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
st.sidebar.header('⚙️ データフィルタ (大枠)')
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

# --- KPIサマリー ---
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
    st.header('Step 2: 拠点内/工程間のスキルギャップ詳細分析 🔎 (高度比較)')
    st.markdown("チーム間の平均値だけでなく、**スキルのバラツキ**も考慮し、具体的な教育ターゲットを特定します。")

    # ----------------------------------------------------
    # A. 拠点・チーム・スキル単位での比較（複数スキル選択対応）
    # ----------------------------------------------------
    st.subheader('2.1. 複数スキル・拠点・チーム間 比較分析')
    
    col_select, col_chart = st.columns([1, 3])
    
    with col_select:
        # 1. 比較対象のスキルを選択 (複数選択可能に修正)
        selected_skills = st.multiselect(
            '比較対象のスキルを選択',
            options=skill_names,
            default=['成形技術', 'NCプログラム'] # 初期値として主要スキルを設定
        )
        
        st.markdown('---')
        
        # 2. 比較対象の拠点を選択 (複数選択可能)
        compare_locations = st.multiselect(
            '比較対象の拠点',
            options=df_filtered['拠点'].unique().tolist(),
            default=df_filtered['拠点'].unique().tolist()
        )
        
        # 3. 比較対象のチームを選択 (複数選択可能)
        compare_teams = st.multiselect(
            '比較対象の組織・チーム',
            options=df_filtered['組織・チーム'].unique().tolist(),
            default=['T1:成形', 'T2:加工']
        )
        
    df_compare = df_filtered[
        df_filtered['拠点'].isin(compare_locations) & 
        df_filtered['組織・チーム'].isin(compare_teams)
    ].copy()
    
    with col_chart:
        if not selected_skills or df_compare.empty:
            st.warning("比較対象のスキル、拠点、またはチームを選択してください。", icon="⚠️")
        else:
            # 拠点、チーム、選択されたスキルで集計し、平均値と標準偏差を計算
            df_pivot_agg = df_compare.groupby(['拠点', '組織・チーム'])[selected_skills].agg(['mean', 'std', 'size']).reset_index()
            
            # DataFrameをPlotlyに適した形（ロングフォーマット）に変換
            # 'mean'と'std'の列を縦に展開
            df_melted = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=[(skill, 'mean') for skill in selected_skills],
                var_name=['スキル名', '指標'],
                value_name='平均スコア'
            )
            
            # 標準偏差(バラツキ)のデータを結合
            df_std = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=[(skill, 'std') for skill in selected_skills],
                value_name='バラツキ'
            )
            df_melted['バラツキ'] = df_std['バラツキ']
            
            # メンバー数を取得 (sizeの列は複数回存在するため、最初のものを使用)
            df_size = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=[(skill, 'size') for skill in selected_skills],
                value_name='メンバー数'
            ).drop_duplicates(subset=['拠点', '組織・チーム'])
            
            # スキル名のタプルを文字列に変換 ('成形技術', 'mean') -> '成形技術'
            df_melted['スキル名'] = df_melted['スキル名'].apply(lambda x: x[0])
            
            # メンバー数の列をメインのデータフレームに結合
            df_melted = pd.merge(df_melted, df_size[['拠点', '組織・チーム', 'メンバー数']], on=['拠点', '組織・チーム'])
            
            # Plotlyで棒グラフを作成 (グループ化の軸を「チーム」と「スキル」にする)
            fig_bar_multi = px.bar(
                df_melted, 
                x='組織・チーム', 
                y='平均スコア', 
                color='スキル名',
                facet_col='拠点', # 拠点ごとにグラフを分ける
                title=f'【{", ".join(selected_skills)}】の拠点・チーム別 平均スコアとバラツキ',
                height=550,
                barmode='group'
            )

            # エラーバーの追加（facet_colとgroupmodeに対応）
            for trace in fig_bar_multi.data:
                skill = trace.name
                location = trace.customdata[0] if trace.customdata is not None and len(trace.customdata) > 0 else '全拠点'

                # 該当するデータ行をフィルタリング
                mask = (df_melted['スキル名'] == skill) & (df_melted['拠点'] == location)
                
                trace.error_y = dict(
                    type='data', 
                    symmetric=False, 
                    array=df_melted.loc[mask, 'バラツキ'], 
                    arrayminus=df_melted.loc[mask, 'バラツキ']
                )
                
            fig_bar_multi.update_layout(
                yaxis=dict(title='平均スコア (±1σ)', range=[1, 5.5]),
                xaxis_title="組織・チーム",
                legend_title="スキル",
                bargap=0.1 # バー間のギャップを調整
            )
            
            # 各バーにメンバー数を注釈として追加 (少し複雑なため、ここでは省略し、ホバーで確認推奨とします)
            st.plotly_chart(fig_bar_multi, use_container_width=True)

    st.info("💡 **分析のポイント**: エラーバー（黒い縦線）が長いほど、**チーム内のメンバー間でスキルのバラツキが大きい**ことを示します。また、複数のスキルを同時に比較することで、特定のチームがどのスキルで相対的に弱いか（例: T1は成形技術は高いがNCプログラムはT2より劣る）を詳細に把握できます。", icon="🎯")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # B. スキル習熟度別 人数分布 (変更なし)
    # ----------------------------------------------------
    st.subheader('2.2. 各スキルカテゴリの習熟度別分布')
    st.markdown("サイドバーで選択された**拠点・チーム**に絞り込んだ、各スキルレベル（1:未習熟 $\\rightarrow$ 5:エキスパート）の**人数構成**を把握します。")
    
    skill_distribution = pd.DataFrame()
    for skill in skill_names:
        count = df_filtered.groupby(skill).size().reset_index(name='人数')
        count['スキル名'] = skill
        skill_distribution = pd.concat([skill_distribution, count])
    
    skill_distribution = skill_distribution.rename(columns={skill_distribution.columns[0]: '習熟度'})
    skill_distribution['習熟度'] = skill_distribution['習熟度'].astype(str)
    
    fig_heatmap = px.bar(
        skill_distribution,
        x='スキル名',
        y='人数',
        color='習熟度',
        title=f'スキル習熟度別人数構成（対象人数: {len(df_filtered)}名）',
        color_discrete_sequence=px.colors.sequential.Viridis,
        category_orders={"習熟度": ["1", "2", "3", "4", "5"]}, 
        height=450
    )
    fig_heatmap.update_layout(xaxis_title="スキルカテゴリ", yaxis_title="人数", legend_title="習熟度(1-5)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")
    st.success(
        "**次なるアクション**: セクション2.1で特定した**課題スキルとバラツキの大きいチーム**に対し、具体的なトレーニング計画を策定します。", icon="🚀"
    )

st.markdown("---")

with tab3:
    st.header('Step 3: スキルと生産データを紐づけた分析 (KPI連携)')
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