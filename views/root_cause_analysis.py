import streamlit as st
import pandas as pd
import plotly.express as px

def show_root_cause_analysis(df_skill, target_location, skill_names):
    """特定拠点の根本原因分析"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🔬 根本原因分析: {target_location}</div>
        <div class="header-subtitle">スキルギャップの具体的な原因と、ボトルネックとなっている従業員・シフト・スキル項目を特定</div>
    </div>
    """, unsafe_allow_html=True)
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    df_benchmark = df_skill[df_skill['拠点'] == '日本 (JP)'].copy()
    
    # 基本統計情報
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("対象従業員数", f"{len(df_target)}名")
    
    with col_stat2:
        avg_skill = df_target['総合スキルスコア'].mean()
        benchmark_skill = df_benchmark['総合スキルスコア'].mean()
        st.metric(
            "平均スキルスコア", 
            f"{avg_skill:.2f}",
            delta=f"{avg_skill - benchmark_skill:.2f}",
            delta_color="normal"
        )
    
    with col_stat3:
        avg_efficiency = df_target['生産効率 (%)'].mean()
        benchmark_efficiency = df_benchmark['生産効率 (%)'].mean()
        st.metric(
            "平均生産効率", 
            f"{avg_efficiency:.1f}%",
            delta=f"{avg_efficiency - benchmark_efficiency:.1f}%",
            delta_color="normal"
        )
    
    with col_stat4:
        avg_defect = df_target['品質不良率 (%)'].mean()
        benchmark_defect = df_benchmark['品質不良率 (%)'].mean()
        st.metric(
            "平均品質不良率", 
            f"{avg_defect:.2f}%",
            delta=f"{avg_defect - benchmark_defect:.2f}%",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # スキル別ギャップ分析
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📉 スキルカテゴリ別ギャップ分析</h2>
        <p class="section-subtitle">各スキルの習熟度とベンチマークとの差異（影響度加味）</p>
    </div>
    """, unsafe_allow_html=True)
    
    skill_gap_data = []
    impact_weights = {
        '成形技術': 1.5,
        'NCプログラム': 1.3,
        '品質検査': 1.4,
        '設備保全': 1.2,
        '安全管理': 1.0
    }
    
    for skill in skill_names:
        target_mean = df_target[skill].mean()
        benchmark_mean = df_benchmark[skill].mean()
        gap = benchmark_mean - target_mean
        weighted_gap = gap * impact_weights.get(skill, 1.0)
        
        priority = '🔴 最優先' if weighted_gap > 0.8 else ('🟡 優先' if weighted_gap > 0.5 else '🟢 中')
        
        skill_gap_data.append({
            'スキル': skill,
            '当拠点平均': f"{target_mean:.2f}",
            'ベンチマーク': f"{benchmark_mean:.2f}",
            'ギャップ': f"{gap:.2f}",
            '影響度係数': impact_weights.get(skill, 1.0),
            '影響度加味': f"{weighted_gap:.2f}",
            '改善優先度': priority,
            '_weighted_gap_value': weighted_gap
        })
    
    df_skill_gap = pd.DataFrame(skill_gap_data)
    df_skill_gap_sorted = df_skill_gap.sort_values('_weighted_gap_value', ascending=False)
    
    # 表示用データ（_weighted_gap_value列を除外）
    df_display = df_skill_gap_sorted.drop(columns=['_weighted_gap_value'])
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # 最も課題のあるスキルを特定
    priority_skill = df_skill_gap_sorted.iloc[0]['スキル']
    priority_weighted_gap = df_skill_gap_sorted.iloc[0]['_weighted_gap_value']
    
    st.success(
        f"🎯 **最優先改善スキル**: {priority_skill}（影響度加味ギャップ: {priority_weighted_gap:.2f}）",
        icon="🎯"
    )
    
    st.markdown("---")
    
    # 習熟度分布比較
    st.markdown(f"### 🎯 最優先スキル【{priority_skill}】の習熟度分布")
    
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
        low_skill_ratio = low_skill_count / len(df_target) * 100
        st.error(
            f"⚠️ **レベル2以下**: {low_skill_count}名 ({low_skill_ratio:.1f}%)\n\n"
            f"この{low_skill_count}名が最優先教育対象です。",
            icon="🚨"
        )
    
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
        bench_low_ratio = bench_low / len(df_benchmark) * 100
        st.success(
            f"✅ **レベル2以下**: {bench_low}名 ({bench_low_ratio:.1f}%)\n\n"
            f"目標: この水準まで改善",
            icon="✨"
        )
    
    st.markdown("---")
    
    # シフト別・チーム別のボトルネック特定
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔍 ボトルネック特定: シフト×チーム×スキル</h2>
        <p class="section-subtitle">最も課題のある組織単位を特定し、集中的な対策を実施</p>
    </div>
    """, unsafe_allow_html=True)
    
    bottleneck_analysis = df_target.groupby(['シフト', '組織・チーム']).agg({
        priority_skill: ['mean', 'std', 'count'],
        '生産効率 (%)': 'mean',
        '品質不良率 (%)': 'mean'
    }).reset_index()
    
    bottleneck_analysis.columns = ['シフト', 'チーム', 'スキル平均', 'スキルバラツキ', '人数', '生産効率', '不良率']
    
    # リスクスコアの計算
    bottleneck_analysis['リスクスコア'] = (
        (5 - bottleneck_analysis['スキル平均']) * 0.4 + 
        bottleneck_analysis['スキルバラツキ'] * 0.3 +
        bottleneck_analysis['不良率'] * 0.3
    )
    
    bottleneck_analysis = bottleneck_analysis.sort_values('リスクスコア', ascending=False)
    
    def get_action_priority(score):
        threshold_70 = bottleneck_analysis['リスクスコア'].quantile(0.7)
        return '🔴 即時対応' if score > threshold_70 else '🟡 計画対応'
    
    bottleneck_analysis['対策優先度'] = bottleneck_analysis['リスクスコア'].apply(get_action_priority)
    
    # 数値のフォーマット
    df_bottleneck_display = bottleneck_analysis.copy()
    df_bottleneck_display['スキル平均'] = df_bottleneck_display['スキル平均'].apply(lambda x: f"{x:.2f}")
    df_bottleneck_display['スキルバラツキ'] = df_bottleneck_display['スキルバラツキ'].apply(lambda x: f"{x:.2f}")
    df_bottleneck_display['人数'] = df_bottleneck_display['人数'].astype(int)
    df_bottleneck_display['生産効率'] = df_bottleneck_display['生産効率'].apply(lambda x: f"{x:.1f}%")
    df_bottleneck_display['不良率'] = df_bottleneck_display['不良率'].apply(lambda x: f"{x:.2f}%")
    df_bottleneck_display['リスクスコア'] = df_bottleneck_display['リスクスコア'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        df_bottleneck_display[['対策優先度', 'シフト', 'チーム', 'スキル平均', 'スキルバラツキ', '人数', '生産効率', '不良率', 'リスクスコア']],
        use_container_width=True,
        hide_index=True
    )
    
    # 最優先対応チーム
    top_bottleneck = bottleneck_analysis.iloc[0]
    
    st.error(
        f"🚨 **即時対応が必要な組織**: {top_bottleneck['シフト']} - {top_bottleneck['チーム']}\n\n"
        f"- スキル平均: {top_bottleneck['スキル平均']:.2f}（目標: 3.5以上）\n"
        f"- 対象人数: {int(top_bottleneck['人数'])}名\n"
        f"- 生産効率: {top_bottleneck['生産効率']:.1f}%\n"
        f"- 品質不良率: {top_bottleneck['不良率']:.2f}%\n\n"
        f"**推奨アクション**: この組織への集中的な教育プログラムを最優先で実施",
        icon="⚠️"
    )
    
    # 次のステップへの誘導
    st.markdown("---")
    
    col_next1, col_next2 = st.columns(2)
    
    with col_next1:
        if st.button(f"📋 {target_location} のアクションプランを作成", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.session_state.priority_skill = priority_skill
            st.rerun()
    
    with col_next2:
        if st.button("📊 エグゼクティブサマリーに戻る", use_container_width=True):
            st.session_state.selected_menu = "📊 エグゼクティブサマリー"
            st.rerun()
    
    return priority_skill