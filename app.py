import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. ダミーデータの生成 (変更なし)
# ... (generate_dummy_data 関数はそのまま使用)
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
            
            score = np.random.randint(2, 4)
            
            if skill_name == '成形技術' and team == 'T1:成形':
                score += np.random.randint(1, 3)
            
            elif skill_name == 'NCプログラム' and team in ['T1:成形', 'T2:加工']:
                score += np.random.randint(1, 2)
            
            elif skill_name in ['品質検査', '設備保全', '安全管理'] and team in ['T1:成形', 'T2:加工', 'T3:組立']:
                score += np.random.randint(0, 2)
                
            if loc == '日本 (JP)':
                score += 1 
            elif loc == '拠点A (TH)' and score > 2:
                score -= 1

            scores.append(np.clip(score + np.random.randint(-1, 2), 1, 5))
        
        skill_data[skill_name] = pd.Series(scores).astype(int)

    df_skill = pd.DataFrame(skill_data)
    
    df_production = df_skill[['拠点', '組織・チーム', 'シフト', '従業員ID']].copy()
    for name in skill_names:
        df_production[name] = df_skill[name]
    
    df_production['総合スキルスコア'] = df_production[skill_names].mean(axis=1).round(2)
    # スコア計算で使用する列名を修正
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

# --- タイトルと説明 (省略) ---
st.title('🏭 スキル・データ・プラットフォーム (SDP) 分析ダッシュボード')
st.markdown("##### グローバル拠点における技能職の力量データに基づいた、生産効率・品質改善のためのデータドリブン分析")

# --- サイドバーによるフィルタリング (省略) ---
st.sidebar.header('⚙️ データフィルタ (大枠)')
selected_location = st.sidebar.multiselect('拠点', options=df_merged['拠点'].unique(), default=df_merged['拠点'].unique())
selected_team = st.sidebar.multiselect('組織・チーム', options=df_merged['組織・チーム'].unique(), default=df_merged['組織・チーム'].unique())

df_filtered = df_merged[df_merged['拠点'].isin(selected_location) & df_merged['組織・チーム'].isin(selected_team)]

# --- KPIサマリー (省略) ---
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
    # ... (Step 1のコード省略) ...
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
        selected_skills = st.multiselect(
            '比較対象のスキルを選択',
            options=skill_names,
            default=['成形技術', 'NCプログラム']
        )
        st.markdown('---')
        compare_locations = st.multiselect(
            '比較対象の拠点',
            options=df_filtered['拠点'].unique().tolist(),
            default=df_filtered['拠点'].unique().tolist()
        )
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
            # 1. 拠点、チーム、選択されたスキルで集計
            df_pivot_agg = df_compare.groupby(['拠点', '組織・チーム'])[selected_skills].agg(['mean', 'std', 'size']).reset_index()
            
            # 2. マルチインデックスをフラット化
            df_pivot_agg.columns = ['_'.join(map(str, col)).strip() if col[1] else col[0] for col in df_pivot_agg.columns.values]
            df_pivot_agg = df_pivot_agg.rename(columns={'拠点_': '拠点', '組織・チーム_': '組織・チーム'})
            
            # 3. 平均値、標準偏差、メンバー数の各列を特定
            mean_cols = [f'{skill}_mean' for skill in selected_skills]
            std_cols = [f'{skill}_std' for skill in selected_skills]
            size_cols = [f'{skill}_size' for skill in selected_skills]

            # 4. 平均スコアをロングフォーマットに melt
            df_melted_mean = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=mean_cols,
                var_name='スキル指標',
                value_name='平均スコア'
            )
            
            # 5. 標準偏差 (バラツキ) もロングフォーマットに melt
            df_melted_std = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=std_cols,
                var_name='スキル指標_std',
                value_name='バラツキ'
            )

            # 6. メンバー数をロングフォーマットに melt
            df_melted_size = df_pivot_agg.melt(
                id_vars=['拠点', '組織・チーム'],
                value_vars=size_cols,
                var_name='スキル指標_size',
                value_name='メンバー数'
            )

            # 7. すべての melt されたデータフレームを結合 (IndexError回避のため、キー結合を使用)
            # スキル名抽出用の中間列を作成
            df_melted_mean['スキル名'] = df_melted_mean['スキル指標'].apply(lambda x: x.split('_')[0])
            df_melted_std['スキル名'] = df_melted_std['スキル指標_std'].apply(lambda x: x.split('_')[0])
            df_melted_size['スキル名'] = df_melted_size['スキル指標_size'].apply(lambda x: x.split('_')[0])

            # 結合キーを設定
            merge_keys = ['拠点', '組織・チーム', 'スキル名']
            
            # 結合の実行
            df_final = pd.merge(df_melted_mean, df_melted_std[['拠点', '組織・チーム', 'スキル名', 'バラツキ']], on=merge_keys, how='left')
            df_final = pd.merge(df_final, df_melted_size[['拠点', '組織・チーム', 'スキル名', 'メンバー数']], on=merge_keys, how='left')
            
            # Plotlyで棒グラフを作成
            fig_bar_multi = px.bar(
                df_final, 
                x='組織・チーム', 
                y='平均スコア', 
                color='スキル名',
                facet_col='拠点',
                title=f'【{", ".join(selected_skills)}】の拠点・チーム別 平均スコアとバラツキ',
                height=550,
                barmode='group'
            )

            # エラーバーの追加
            for trace_idx, trace in enumerate(fig_bar_multi.data):
                skill = trace.name
                
                # Plotlyの内部的なソートとフィルタリングに対応するため、元のデータフレームからエラーバー用のデータを抽出
                # trace.customdata は Plotly の内部構造に依存するため、ここではより確実な結合データフレームを使用
                
                # 該当するスキルと拠点のデータをフィルタリング
                # Plotlyのfacet_colを使うと、トレースは '組織・チーム' でソートされるため、その順序でバラツキを渡す必要がある
                
                # Plotlyのグループ順序を取得
                unique_teams_in_facet = df_final.loc[df_final['スキル名'] == skill, '組織・チーム'].unique()
                
                # トレースの拠点名を取得 (facetのタイトルから取得)
                location_text = fig_bar_multi.layout['annotations'][trace_idx // len(fig_bar_multi.data) * len(df_final['拠点'].unique()) if 'annotations' in fig_bar_multi.layout else 0]['text'].replace('拠点=', '')
                
                # 該当する拠点、スキル、チームの順にバラツキを抽出
                # (ここでは、すべてのfacetを一度に処理するため、facet_colに対応したよりシンプルで堅牢な方法に切り替えます)

                # traceの軸データ（X軸）の順番に合わせてバラツキデータを抽出
                # 拠点とスキルのフィルタリング
                mask = (df_final['スキル名'] == skill) & (df_final['拠点'] == trace.customdata[0][0])
                
                # トレースのX軸の順序（組織・チーム）に合わせて、バラツキを抽出
                trace_teams = trace.x
                std_values = []
                for team in trace_teams:
                    # 該当する行を検索し、バラツキの値を取得
                    std_val = df_final.loc[(df_final['拠点'] == trace.customdata[0][0]) & (df_final['スキル名'] == skill) & (df_final['組織・チーム'] == team), 'バラツキ'].iloc[0]
                    std_values.append(std_val)

                trace.error_y = dict(
                    type='data', 
                    symmetric=False, 
                    array=std_values,
                    arrayminus=std_values
                )
                
            fig_bar_multi.update_layout(
                yaxis=dict(title='平均スコア (±1σ)', range=[1, 5.5]),
                xaxis_title="組織・チーム",
                legend_title="スキル",
                bargap=0.1
            )
            
            st.plotly_chart(fig_bar_multi, use_container_width=True)

    st.info("💡 **分析のポイント**: エラーバー（黒い縦線）が長いほど、**チーム内のメンバー間でスキルのバラツキが大きい**ことを示します。また、複数のスキルを同時に比較することで、特定のチームがどのスキルで相対的に弱いか（例: T1は成形技術は高いがNCプログラムはT2より劣る）を詳細に把握できます。", icon="🎯")
    
    st.markdown("---")
    
    # ... (Step 2.2、Step 3 のコードは省略) ...
    # ----------------------------------------------------
    # B. スキル習熟度別 人数分布
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