# components/step2_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_step2_analysis(df_filtered, skill_names, skills_info):
    """Step 2: ギャップ分析と対策を表示する."""
    st.header('Step 2: 拠点内/工程間のスキルギャップ詳細分析 🔎 (高度比較)')
    st.markdown("チーム間の平均値だけでなく、**スキルのバラツキ**も考慮し、具体的な教育ターゲットを特定します。")

    # ----------------------------------------------------
    # A. 拠点・チーム・スキル・シフト間 比較分析
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
            # 1. 拠点、チーム、シフト、選択されたスキルで集計
            group_cols = ['拠点', '組織・チーム', 'シフト']
            df_pivot_agg = df_compare.groupby(group_cols)[selected_skills].agg(['mean', 'std', 'size']).reset_index()
            
            # 2. マルチインデックスをフラット化
            df_pivot_agg.columns = ['_'.join(map(str, col)).strip() if col[1] else col[0] for col in df_pivot_agg.columns.values]
            df_pivot_agg = df_pivot_agg.rename(columns={c + '_': c for c in group_cols})
            
            mean_cols = [f'{skill}_mean' for skill in selected_skills]

            # 3. 平均スコアをロングフォーマットに melt
            df_melted_mean = df_pivot_agg.melt(
                id_vars=group_cols,
                value_vars=mean_cols,
                var_name='スキル指標',
                value_name='平均スコア'
            )
            
            # 4. 標準偏差 (バラツキ) とメンバー数も結合
            df_melted_mean['スキル名'] = df_melted_mean['スキル指標'].apply(lambda x: x.split('_')[0])
            
            # 結合キーでバラツキとメンバー数をルックアップ
            df_final = df_melted_mean.copy()
            df_final['バラツキ'] = df_final.apply(
                lambda row: df_pivot_agg.loc[
                    (df_pivot_agg['拠点'] == row['拠点']) & 
                    (df_pivot_agg['組織・チーム'] == row['組織・チーム']) &
                    (df_pivot_agg['シフト'] == row['シフト']),
                    f"{row['スキル名']}_std"
                ].iloc[0], axis=1
            )
            df_final['メンバー数'] = df_final.apply(
                lambda row: df_pivot_agg.loc[
                    (df_pivot_agg['拠点'] == row['拠点']) & 
                    (df_pivot_agg['組織・チーム'] == row['組織・チーム']) &
                    (df_pivot_agg['シフト'] == row['シフト']),
                    f"{row['スキル名']}_size"
                ].iloc[0], axis=1
            )
            df_final = df_final.drop(columns=['スキル指標'])

            # Plotlyで棒グラフを作成 ('シフト'をX軸に組み込むため、'組織・チーム (シフト)'を結合)
            df_final['チーム_シフト'] = df_final['組織・チーム'] + ' (' + df_final['シフト'] + ')'
            
            fig_bar_multi = px.bar(
                df_final, 
                x='チーム_シフト', 
                y='平均スコア', 
                color='スキル名',
                facet_col='拠点',
                title=f'【{", ".join(selected_skills)}】の拠点・チーム・シフト別 平均スコアとバラツキ',
                height=550,
                barmode='group'
            )

            # エラーバーの追加
            facet_locations = df_final['拠点'].unique().tolist()
            num_locations = len(facet_locations)
            
            for trace_idx, trace in enumerate(fig_bar_multi.data):
                skill = trace.name
                facet_col_index = trace_idx // len(selected_skills)
                location = facet_locations[facet_col_index % num_locations]
                
                std_values = []
                trace_teams_shifts = trace.x
                
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
    # B. スキル習熟度別 人数分布
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