import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_root_cause_analysis(df_skill, target_location, all_skills, skill_to_category, skill_categories, skill_hierarchy, processes):
    """特定拠点の根本原因分析"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🔬 根本原因分析: {target_location}</div>
        <div class="header-subtitle">工程×スキルカテゴリ別のギャップ分析とボトルネック特定</div>
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
    
    # 工程×スキルカテゴリ分析
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📉 工程×スキルカテゴリ別ギャップ分析</h2>
        <p class="section-subtitle">各工程におけるスキルカテゴリの平均値とバラツキを日本と比較</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 工程×スキルカテゴリのヒートマップデータを作成
    heatmap_data = []
    
    for process in processes:
        for category in skill_categories:
            # 対象拠点のデータ
            target_process_data = df_target[df_target['工程'] == process]
            category_skills = skill_hierarchy[category]['skills']
            target_mean = target_process_data[category_skills].mean().mean()
            target_std = target_process_data[category_skills].std().mean()
            
            # ベンチマークのデータ
            benchmark_process_data = df_benchmark[df_benchmark['工程'] == process]
            benchmark_mean = benchmark_process_data[category_skills].mean().mean()
            benchmark_std = benchmark_process_data[category_skills].std().mean()
            
            gap = benchmark_mean - target_mean if not pd.isna(target_mean) else 0
            
            heatmap_data.append({
                '工程': process,
                'スキルカテゴリ': category,
                '対象拠点_平均': target_mean,
                '対象拠点_バラツキ': target_std,
                'ベンチマーク_平均': benchmark_mean,
                'ベンチマーク_バラツキ': benchmark_std,
                'ギャップ': gap,
                '人数': len(target_process_data)
            })
    
    df_heatmap = pd.DataFrame(heatmap_data)
    
    # ヒートマップ表示（クリック可能）
    st.markdown("### 🔥 工程×スキルカテゴリ ギャップヒートマップ")
    st.markdown("**クリック可能**: 各セルをクリックすると、下部に詳細な分布が表示されます")
    
    # ピボットテーブル作成
    pivot_table = df_heatmap.pivot(index='工程', columns='スキルカテゴリ', values='ギャップ')
    
    # ヒートマップ描画
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='RdYlGn_r',  # 赤（大きいギャップ）→黄→緑（小さいギャップ）
        text=pivot_table.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="ギャップ")
    ))
    
    fig_heatmap.update_layout(
        title='スキルギャップ（ベンチマーク - 対象拠点）',
        xaxis_title='スキルカテゴリ',
        yaxis_title='工程',
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # インタラクティブな詳細表示
    st.markdown("---")
    st.markdown("### 📊 詳細分析: スキルカテゴリ別の分布比較")
    
    col_select1, col_select2 = st.columns(2)
    
    with col_select1:
        selected_process = st.selectbox(
            '分析対象の工程を選択',
            options=processes,
            index=0
        )
    
    with col_select2:
        selected_category = st.selectbox(
            '分析対象のスキルカテゴリを選択',
            options=skill_categories,
            index=0
        )
    
    # 選択された工程×スキルカテゴリのデータを抽出
    selected_data = df_heatmap[
        (df_heatmap['工程'] == selected_process) & 
        (df_heatmap['スキルカテゴリ'] == selected_category)
    ].iloc[0]
    
    # サマリー表示
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    
    with col_sum1:
        st.metric(
            f"{target_location} 平均",
            f"{selected_data['対象拠点_平均']:.2f}",
            help="5段階評価の平均"
        )
    
    with col_sum2:
        st.metric(
            "ベンチマーク(日本) 平均",
            f"{selected_data['ベンチマーク_平均']:.2f}",
            help="5段階評価の平均"
        )
    
    with col_sum3:
        st.metric(
            "ギャップ",
            f"{selected_data['ギャップ']:.2f}",
            delta=f"{'要改善' if selected_data['ギャップ'] > 0.5 else '良好'}",
            delta_color="inverse" if selected_data['ギャップ'] > 0.5 else "normal"
        )
    
    with col_sum4:
        st.metric(
            "対象人数",
            f"{int(selected_data['人数'])}名",
            help="この工程に配置されている従業員数"
        )
    
    # スキルカテゴリ内の個別スキル分布
    st.markdown(f"#### 【{selected_category}】内の個別スキル分布")
    
    category_skills = skill_hierarchy[selected_category]['skills']
    
    # 対象拠点とベンチマークのデータを抽出
    target_process_filtered = df_target[df_target['工程'] == selected_process]
    benchmark_process_filtered = df_benchmark[df_benchmark['工程'] == selected_process]
    
    # 各スキルの平均を計算
    skill_comparison = []
    for skill in category_skills:
        target_skill_mean = target_process_filtered[skill].mean()
        benchmark_skill_mean = benchmark_process_filtered[skill].mean()
        gap = benchmark_skill_mean - target_skill_mean
        
        skill_comparison.append({
            'スキル': skill,
            f'{target_location}': target_skill_mean,
            '日本': benchmark_skill_mean,
            'ギャップ': gap
        })
    
    df_skill_comp = pd.DataFrame(skill_comparison)
    
    # 棒グラフで比較
    fig_compare = go.Figure()
    
    fig_compare.add_trace(go.Bar(
        name=target_location,
        x=df_skill_comp['スキル'],
        y=df_skill_comp[target_location],
        marker_color='#ff7f0e'
    ))
    
    fig_compare.add_trace(go.Bar(
        name='日本 (ベンチマーク)',
        x=df_skill_comp['スキル'],
        y=df_skill_comp['日本'],
        marker_color='#2ca02c'
    ))
    
    fig_compare.update_layout(
        title=f'{selected_process} - {selected_category}: 個別スキル比較',
        xaxis_title='スキル',
        yaxis_title='平均スコア',
        barmode='group',
        height=400,
        yaxis=dict(range=[1, 5])
    ))
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # 分布の詳細（ヒストグラム）
    st.markdown(f"#### 分布の詳細: {selected_process} - {selected_category}")
    
    col_hist1, col_hist2 = st.columns(2)
    
    with col_hist1:
        st.markdown(f"**{target_location} の分布**")
        
        # カテゴリ内の全スキルのスコアを集計
        target_category_scores = []
        for skill in category_skills:
            target_category_scores.extend(target_process_filtered[skill].dropna().tolist())
        
        if target_category_scores:
            fig_target_hist = px.histogram(
                x=target_category_scores,
                nbins=5,
                title=f'{selected_category} スコア分布',
                labels={'x': 'スコア', 'y': '人数'},
                color_discrete_sequence=['#ff7f0e']
            )
            fig_target_hist.update_layout(showlegend=False, height=300)
            fig_target_hist.update_xaxes(range=[0.5, 5.5], dtick=1)
            st.plotly_chart(fig_target_hist, use_container_width=True)
            
            low_skill_count = sum(1 for s in target_category_scores if s <= 2)
            st.error(
                f"⚠️ **レベル2以下**: {low_skill_count}件 ({low_skill_count/len(target_category_scores)*100:.1f}%)",
                icon="🚨"
            )
        else:
            st.warning("データが不足しています")
    
    with col_hist2:
        st.markdown("**日本 (ベンチマーク) の分布**")
        
        # カテゴリ内の全スキルのスコアを集計
        benchmark_category_scores = []
        for skill in category_skills:
            benchmark_category_scores.extend(benchmark_process_filtered[skill].dropna().tolist())
        
        if benchmark_category_scores:
            fig_bench_hist = px.histogram(
                x=benchmark_category_scores,
                nbins=5,
                title=f'{selected_category} スコア分布',
                labels={'x': 'スコア', 'y': '人数'},
                color_discrete_sequence=['#2ca02c']
            )
            fig_bench_hist.update_layout(showlegend=False, height=300)
            fig_bench_hist.update_xaxes(range=[0.5, 5.5], dtick=1)
            st.plotly_chart(fig_bench_hist, use_container_width=True)
            
            bench_low_count = sum(1 for s in benchmark_category_scores if s <= 2)
            st.success(
                f"✅ **レベル2以下**: {bench_low_count}件 ({bench_low_count/len(benchmark_category_scores)*100:.1f}%)",
                icon="✨"
            )
        else:
            st.warning("データが不足しています")
    
    st.markdown("---")
    
    # ボトルネック特定（シフト別）
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔍 ボトルネック特定: 工程×シフト×スキルカテゴリ</h2>
        <p class="section-subtitle">最も課題のある組織単位を特定し、集中的な対策を実施</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 最もギャップが大きい工程×スキルカテゴリを特定
    top_gap_row = df_heatmap.sort_values('ギャップ', ascending=False).iloc[0]
    priority_process = top_gap_row['工程']
    priority_category = top_gap_row['スキルカテゴリ']
    
    st.info(
        f"💡 **最優先改善対象**: {priority_process} - {priority_category}\n\n"
        f"ギャップ: {top_gap_row['ギャップ']:.2f} / 対象人数: {int(top_gap_row['人数'])}名",
        icon="🎯"
    )
    
    # シフト別のボトルネック分析
    bottleneck_analysis = []
    
    for process in processes:
        for shift in ['日勤', '夜勤']:
            process_shift_data = df_target[(df_target['工程'] == process) & (df_target['シフト'] == shift)]
            
            if len(process_shift_data) > 0:
                for category in skill_categories:
                    category_skills = skill_hierarchy[category]['skills']
                    avg_score = process_shift_data[category_skills].mean().mean()
                    std_score = process_shift_data[category_skills].std().mean()
                    
                    # リスクスコア計算
                    risk_score = (5 - avg_score) * 0.5 + std_score * 0.5
                    
                    bottleneck_analysis.append({
                        '工程': process,
                        'シフト': shift,
                        'スキルカテゴリ': category,
                        '平均スコア': avg_score,
                        'バラツキ': std_score,
                        '人数': len(process_shift_data),
                        'リスクスコア': risk_score
                    })
    
    df_bottleneck = pd.DataFrame(bottleneck_analysis)
    df_bottleneck = df_bottleneck.sort_values('リスクスコア', ascending=False).head(10)
    
    def get_priority_label(score):
        if score > df_bottleneck['リスクスコア'].quantile(0.7):
            return '🔴 即時対応'
        else:
            return '🟡 計画対応'
    
    df_bottleneck['対策優先度'] = df_bottleneck['リスクスコア'].apply(get_priority_label)
    
    # フォーマット
    df_bottleneck_display = df_bottleneck.copy()
    df_bottleneck_display['平均スコア'] = df_bottleneck_display['平均スコア'].apply(lambda x: f"{x:.2f}")
    df_bottleneck_display['バラツキ'] = df_bottleneck_display['バラツキ'].apply(lambda x: f"{x:.2f}")
    df_bottleneck_display['リスクスコア'] = df_bottleneck_display['リスクスコア'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        df_bottleneck_display[['対策優先度', '工程', 'シフト', 'スキルカテゴリ', '平均スコア', 'バラツキ', '人数', 'リスクスコア']],
        use_container_width=True,
        hide_index=True
    )
    
    # 最優先対応
    if not df_bottleneck.empty:
        top_bottleneck = df_bottleneck.iloc[0]
        
        st.error(
            f"🚨 **即時対応が必要な組織**: {top_bottleneck['工程']} - {top_bottleneck['シフト']} - {top_bottleneck['スキルカテゴリ']}\n\n"
            f"- 平均スコア: {top_bottleneck['平均スコア']:.2f}（目標: 3.5以上）\n"
            f"- バラツキ: {top_bottleneck['バラツキ']:.2f}\n"
            f"- 対象人数: {int(top_bottleneck['人数'])}名\n\n"
            f"**推奨アクション**: この組織への集中的な教育プログラムを最優先で実施",
            icon="⚠️"
        )
    
    # 次のステップへの誘導
    st.markdown("---")
    
    col_next1, col_next2 = st.columns(2)
    
    with col_next1:
        if st.button(f"📋 {target_location} のアクションプランを作成", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.session_state.priority_skill = f"{priority_process} - {priority_category}"
            st.rerun()
    
    with col_next2:
        if st.button("📊 エグゼクティブサマリーに戻る", use_container_width=True):
            st.session_state.selected_menu = "📊 エグゼクティブサマリー"
            st.rerun()
    
    return f"{priority_process} - {priority_category}"