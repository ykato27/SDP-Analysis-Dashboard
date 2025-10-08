import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# 1. ダミーデータの生成 (変更あり: 日次データとランダムな評価日を追加)
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
        # 評価日を過去半年間でランダムに設定
        '評価日': [date.today() - timedelta(days=np.random.randint(1, 180)) for _ in range(num_data)]
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
    
    # ----------------------------------------------------
    # 日次生産実績データ (新たに生成)
    # ----------------------------------------------------
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    
    production_records = []
    
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        for loc in locations:
            for shift in shifts:
                # 日次データにスキルレベルを反映
                avg_skill_for_day = df_skill.loc[
                    (df_skill['拠点'] == loc) & (df_skill['シフト'] == shift), 
                    skill_names
                ].mean().mean() # その日、その拠点のシフトにいる人の平均スキルレベルをシミュレート
                
                if pd.isna(avg_skill_for_day):
                    avg_skill_for_day = 3.0

                # KPIにスキルレベルを反映
                efficiency = (75 + avg_skill_for_day * 4 + np.random.randn() * 3).clip(75, 98).round(1)
                defect_rate = (6 - avg_skill_for_day * 0.8 + np.random.randn() * 0.8).clip(0.5, 6).round(2)
                
                production_records.append({
                    '日付': single_date,
                    '拠点': loc,
                    'シフト': shift,
                    '日次生産量 (Unit)': np.random.randint(1000, 5000) * (1 + (avg_skill_for_day - 3.5) / 5), # スキルが高いと生産量も高い
                    '生産効率 (%)': efficiency,
                    '品質不良率 (%)': defect_rate,
                    '平均スキル予測値': avg_skill_for_day.round(2)
                })

    df_daily_prod = pd.DataFrame(production_records)
    
    # スキルデータに総合スコアとKPIを加える
    df_skill['総合スキルスコア'] = df_skill[skill_names].mean(axis=1).round(2)
    
    # このダッシュボードの分析のため、個人KPIはランダムに生成し直す
    df_skill['生産効率 (%)'] = (60 + df_skill['総合スキルスコア'] * 8 + np.random.randn(num_data) * 4).clip(75, 98).round(1)
    df_skill['品質不良率 (%)'] = (8 - df_skill['総合スキルスコア'] * 1.2 + np.random.randn(num_data) * 1).clip(0.5, 8).round(1)
    
    return df_skill, df_daily_prod, skills_info, skill_names

# データ生成
df_skill, df_daily_prod, skills_info, skill_names = generate_dummy_data()

# --------------------------------------------------------------------------------
# Streamlitアプリケーション本体
# --------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="SDP分析ダッシュボード", page_icon="🏭")

st.title('🏭 スキル・データ・プラットフォーム (SDP) 分析ダッシュボード')
st.markdown("##### グローバル拠点における技能職の力量データに基づいた、生産効率・品質改善のためのデータドリブン分析")

# --- サイドバーによるフィルタリング ---
st.sidebar.header('⚙️ データフィルタ (大枠)')
selected_location = st.sidebar.multiselect('拠点', options=df_skill['拠点'].unique(), default=df_skill['拠点'].unique())
selected_team = st.sidebar.multiselect('組織・チーム', options=df_skill['組織・チーム'].unique(), default=df_skill['組織・チーム'].unique())
selected_shift = st.sidebar.multiselect('シフト', options=df_skill['シフト'].unique(), default=df_skill['シフト'].unique()) # シフトフィルタを追加

df_filtered = df_skill[
    df_skill['拠点'].isin(selected_location) & 
    df_skill['組織・チーム'].isin(selected_team) &
    df_skill['シフト'].isin(selected_shift) # シフトでフィルタ
].copy()

# --- KPIサマリー (省略) ---
total_efficiency = df_filtered['生産効率 (%)'].mean()
total_defect_rate = df_filtered['品質不良率 (%)'].mean()
avg_skill_score = df_filtered['総合スキルスコア'].mean()

st.markdown("---")
st.subheader("📊 主要KPIサマリー (フィルタ適用済み)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("対象従業員数", f"{len(df_filtered)} 名")
col2.metric("平均総合スキルスコア (5点満点)", f"{avg_skill_score:.2f}")
eff_delta = total_efficiency - df_skill['生産効率 (%)'].mean()
col3.metric("平均生産効率", f"{total_efficiency:.1f} %", delta=f"{eff_delta:.1f}")
def_delta = total_defect_rate - df_skill['品質不良率 (%)'].mean()
col4.metric("平均品質不良率", f"{total_defect_rate:.2f} %", delta=f"{def_delta:.2f}", delta_color="inverse")
st.markdown("---")


# --- タブによる分析ステップの表示 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "1. スキルデータ一元管理 (生データ)", 
    "2. ギャップ分析と対策", 
    "3. スキルと生産性 (KPI連携)",
    "4. 日次傾向分析" # 新規タブ追加
])

# --- Step 1 (変更なし) ---
with tab1:
    st.header('Step 1: スキルデータの一元管理と可視化')
    st.markdown("共通スキルカテゴリと定義に基づき、全拠点のスキルデータを統合します。")
    with st.expander("共通スキルカテゴリ定義", expanded=False):
        skill_def_df = pd.DataFrame(skills_info.items(), columns=['スキル名', '定義'])
        st.dataframe(skill_def_df, use_container_width=True)
    st.markdown("##### 📝 従業員別統合スキル評価データ (フィルタ適用済み)")
    st.dataframe(df_filtered.head(20), use_container_width=True, height=500)

# --- Step 2 (変更あり: シフト軸の追加) ---
with tab2:
    st.header('Step 2: 拠点内/工程間のスキルギャップ詳細分析 🔎 (高度比較)')
    st.markdown("チーム間の平均値だけでなく、**スキルのバラツキ**も考慮し、具体的な教育ターゲットを特定します。")

    # ----------------------------------------------------
    # A. 拠点・チーム・スキル単位での比較（複数スキル選択対応）
    # ----------------------------------------------------
    st.subheader('2.1. 複数スキル・拠点・チーム・**シフト**間 比較分析')
    
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
        # ★★★ 新たにシフトを追加 ★★★
        compare_shifts = st.multiselect(
            '比較対象のシフト',
            options=df_filtered['シフト'].unique().tolist(),
            default=df_filtered['シフト'].unique().tolist()
        )
        
    df_compare = df_filtered[
        df_filtered['拠点'].isin(compare_locations) & 
        df_filtered['組織・チーム'].isin(compare_teams) &
        df_filtered['シフト'].isin(compare_shifts)
    ].copy()
    
    with col_chart:
        if not selected_skills or df_compare.empty:
            st.warning("比較対象のスキル、拠点、チーム、またはシフトを選択してください。", icon="⚠️")
        else:
            # 1. 拠点、チーム、シフト、選択されたスキルで集計 (集計軸に 'シフト' を追加)
            group_cols = ['拠点', '組織・チーム', 'シフト']
            df_pivot_agg = df_compare.groupby(group_cols)[selected_skills].agg(['mean', 'std', 'size']).reset_index()
            
            # 2. マルチインデックスをフラット化
            df_pivot_agg.columns = ['_'.join(map(str, col)).strip() if col[1] else col[0] for col in df_pivot_agg.columns.values]
            # 集計軸の名前を修正
            df_pivot_agg = df_pivot_agg.rename(columns={c + '_': c for c in group_cols})
            
            mean_cols = [f'{skill}_mean' for skill in selected_skills]

            # 3. 平均スコアをロングフォーマットに melt
            df_melted_mean = df_pivot_agg.melt(
                id_vars=group_cols,
                value_vars=mean_cols,
                var_name='スキル指標',
                value_name='平均スコア'
            )
            
            # 4. 標準偏差 (バラツキ) とメンバー数も melt し、平均値と結合
            df_melted_mean['スキル名'] = df_melted_mean['スキル指標'].apply(lambda x: x.split('_')[0])
            
            df_pivot_agg['merge_key'] = df_pivot_agg['拠点'] + '_' + df_pivot_agg['組織・チーム'] + '_' + df_pivot_agg['シフト']
            
            df_melted_mean['バラツキ'] = df_melted_mean.apply(
                lambda row: df_pivot_agg.loc[
                    (df_pivot_agg['拠点'] == row['拠点']) & 
                    (df_pivot_agg['組織・チーム'] == row['組織・チーム']) &
                    (df_pivot_agg['シフト'] == row['シフト']),
                    f"{row['スキル名']}_std"
                ].iloc[0], axis=1
            )
            df_melted_mean['メンバー数'] = df_melted_mean.apply(
                lambda row: df_pivot_agg.loc[
                    (df_pivot_agg['拠点'] == row['拠点']) & 
                    (df_pivot_agg['組織・チーム'] == row['組織・チーム']) &
                    (df_pivot_agg['シフト'] == row['シフト']),
                    f"{row['スキル名']}_size"
                ].iloc[0], axis=1
            )
            df_final = df_melted_mean.drop(columns=['スキル指標'])

            # Plotlyで棒グラフを作成 ('シフト'をX軸に組み込むため、'組織・チーム (シフト)'を結合)
            df_final['チーム_シフト'] = df_final['組織・チーム'] + ' (' + df_final['シフト'] + ')'
            
            fig_bar_multi = px.bar(
                df_final, 
                x='チーム_シフト', # 新しい複合軸
                y='平均スコア', 
                color='スキル名',
                facet_col='拠点',
                title=f'【{", ".join(selected_skills)}】の拠点・チーム・シフト別 平均スコアとバラツキ',
                height=550,
                barmode='group'
            )

            # エラーバーの追加
            facet_locations = df_final['拠点'].unique().tolist()
            num_teams_shifts = len(df_final['チーム_シフト'].unique())
            
            for trace_idx, trace in enumerate(fig_bar_multi.data):
                skill = trace.name
                
                # トレースのX軸の順序（チーム_シフト）に基づいてバラツキを検索
                trace_teams_shifts = trace.x
                
                # 現在のトレースが属する拠点 (ファセット列の情報を利用して推定)
                # Plotly Expressはトレースを 'スキル名' → '拠点' の順に描画することが多いため、
                # トレースインデックスから現在の拠点名を推定
                
                # アノテーションから拠点名を抽出するロジックを使用
                # 拠点名は facet_col の数だけアノテーションに格納される
                num_locations = len(facet_locations)
                
                # 描画されている拠点のアノテーションインデックスを計算
                # 1つの拠点あたりのトレース数 = len(selected_skills) * len(df_final['組織・チーム'].unique()) * len(df_final['シフト'].unique()) / len(facet_locations)
                # → 実際には、Plotlyが持つトレースの数は、(選択スキル数) * (拠点数) になる
                # トレースインデックスをスキル数で割った結果を拠点のインデックスとして使用
                facet_col_index = trace_idx // len(selected_skills)
                
                location = facet_locations[facet_col_index % num_locations]
                
                std_values = []
                for team_shift in trace_teams_shifts:
                    team, shift = team_shift.split(' (')
                    shift = shift.replace(')', '')
                    
                    try:
                        std_val = df_final.loc[
                            (df_final['拠点'] == location) & 
                            (df_final['スキル名'] == skill) & 
                            (df_final['組織・チーム'] == team) &
                            (df_final['シフト'] == shift), 'バラツキ'
                        ].iloc[0]
                        std_values.append(std_val)
                    except IndexError:
                        std_values.append(0)

                trace.error_y = dict(
                    type='data', 
                    symmetric=False, 
                    array=std_values,
                    arrayminus=std_values
                )
                
            fig_bar_multi.update_layout(
                yaxis=dict(title='平均スコア (±1σ)', range=[1, 5.5]),
                xaxis_title="組織・チーム (シフト)",
                legend_title="スキル",
                bargap=0.1
            )
            
            st.plotly_chart(fig_bar_multi, use_container_width=True)

    st.info("💡 **分析のポイント**: シフト別で比較することで、**日勤・夜勤のオペレーター間のスキル平準化**の課題が見えます。夜勤のバラツキが大きい場合、夜勤の監督・指導体制の強化が必要です。", icon="🎯")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # B. スキル習熟度別 人数分布 (変更なし)
    # ----------------------------------------------------
    st.subheader('2.2. 各スキルカテゴリの習熟度別分布')
    st.markdown("サイドバーで選択された**拠点・チーム・シフト**に絞り込んだ、各スキルレベル（1:未習熟 $\\rightarrow$ 5:エキスパート）の**人数構成**を把握します。")
    
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
        "**次なるアクション**: セクション2.1で特定した**課題スキルとバラツキの大きいチーム・シフト**に対し、具体的なトレーニング計画を策定します。", icon="🚀"
    )

# --- Step 3 (変更なし) ---
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
            hover_data=['従業員ID', '組織・チーム', 'シフト'],
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
            hover_data=['従業員ID', '組織・チーム', 'シフト'],
            trendline='ols',
            title='総合スキルと品質不良率の相関'
        )
        st.plotly_chart(fig_def, use_container_width=True)
        st.info(f"**相関係数 (Def)**: {df_filtered['総合スキルスコア'].corr(df_filtered['品質不良率 (%)']):.3f} (マイナス相関) -> スキルが不良率低下に寄与。", icon="✔️")

    st.markdown("---")
    st.subheader('🎯 最適な配置、教育の実行に向けたKPIとスキルレベルの統合')
    
    # シフトを考慮した集計
    kpi_skill_summary = df_filtered.groupby(['拠点', 'シフト']).agg(
        {'生産効率 (%)': 'mean', '品質不良率 (%)': 'mean', '総合スキルスコア': 'mean'}
    ).reset_index()
    
    fig_bar = px.bar(
        kpi_skill_summary,
        x='拠点',
        y='生産効率 (%)',
        color='総合スキルスコア',
        facet_col='シフト',
        color_continuous_scale=px.colors.sequential.Viridis,
        title='拠点・シフト別 生産効率とスキルレベルの関係'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.success(
        "**次なるアクション**: スキルスコアが低く、かつKPIが低い拠点・シフト（例: **拠点A (TH) の夜勤**）を特定し、その拠点へ「成形技術」の高い日本の技術者を短期派遣するか、またはオンライン教育プログラムを重点的に割り当てるなど、**最適な配置・教育施策**を実行します。",
        icon="🚀"
    )

# --- Step 4 (新規追加) ---
with tab4:
    st.header('Step 4: 日次生産データとの傾向分析')
    st.markdown("直近の日次生産データと、それに影響を与えたと推測される**平均スキルレベルの変動**を比較分析します。")

    df_daily_filtered = df_daily_prod[
        df_daily_prod['拠点'].isin(selected_location) & 
        df_daily_prod['シフト'].isin(selected_shift)
    ].copy()

    # 拠点とシフトの選択肢をフィルタリング
    selected_analysis_locations = st.multiselect('分析対象の拠点 (日次)', options=df_daily_filtered['拠点'].unique().tolist(), default=df_daily_filtered['拠点'].unique().tolist())
    selected_analysis_shifts = st.multiselect('分析対象のシフト (日次)', options=df_daily_filtered['シフト'].unique().tolist(), default=df_daily_filtered['シフト'].unique().tolist())

    df_analysis = df_daily_filtered[
        df_daily_filtered['拠点'].isin(selected_analysis_locations) & 
        df_daily_filtered['シフト'].isin(selected_analysis_shifts)
    ].groupby('日付').mean(numeric_only=True).reset_index()

    if df_analysis.empty:
        st.warning("日次分析対象のデータが存在しません。", icon="⚠️")
    else:
        
        # 2軸グラフの作成 (生産効率 vs 平均スキル予測値)
        fig_time_series = go.Figure()

        # 1. 生産効率 (左軸)
        fig_time_series.add_trace(go.Scatter(
            x=df_analysis['日付'], 
            y=df_analysis['生産効率 (%)'], 
            name='平均生産効率 (%)',
            yaxis='y1',
            mode='lines+markers',
            marker=dict(color='#1f77b4')
        ))

        # 2. 平均スキル予測値 (右軸)
        fig_time_series.add_trace(go.Scatter(
            x=df_analysis['日付'], 
            y=df_analysis['平均スキル予測値'], 
            name='平均スキル予測値',
            yaxis='y2',
            mode='lines+markers',
            marker=dict(color='#ff7f0e')
        ))

        fig_time_series.update_layout(
            title='日次 生産効率と平均スキル予測値の推移 (過去30日間)',
            xaxis=dict(title='日付'),
            yaxis=dict(
                title='生産効率 (%)',
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4'),
                range=[df_analysis['生産効率 (%)'].min() * 0.98, df_analysis['生産効率 (%)'].max() * 1.02]
            ),
            yaxis2=dict(
                title='平均スキル予測値 (5点満点)',
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e'),
                overlaying='y',
                side='right',
                range=[2.5, 4.5] # スキルスコアのレンジに合わせる
            ),
            legend=dict(x=0.1, y=1.1, orientation="h")
        )

        st.plotly_chart(fig_time_series, use_container_width=True)
        
        st.info(
            "**分析の洞察**: 生産効率の低下と**平均スキル予測値の低下**が同期している場合、その期間のシフトメンバーのスキルが不足していた可能性が高いです。特に、**夜勤で生産効率が急落している場合**、夜勤メンバーのスキルレベルや、夜間特有の設備トラブルへの対応スキルが課題である可能性があります。", icon="📈"
        )
    
    st.markdown("---")
    st.success(
        "**次なるアクション**: 日次データから特定された**スキルが低い特定日**のメンバー構成（従業員ID）をドリルダウンし、そのメンバーに集中的なフォローアップ教育を実施します。",
        icon="🚀"
    )

st.markdown("---")
st.caption("© SDP Simulation Dashboard (Powered by Streamlit)")