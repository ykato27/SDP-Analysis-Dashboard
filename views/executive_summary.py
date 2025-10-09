import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
            delta=None,
            help="ベンチマーク(日本)との生産性格差による推定損失"
        )
    
    with col2:
        st.metric(
            "💰 必要教育投資", 
            f"¥{total_training_cost:.0f}M",
            delta=f"-{(total_training_cost/total_annual_loss*100):.1f}%",
            delta_color="inverse",
            help="スキルギャップ解消のための必要投資額"
        )
    
    with col3:
        st.metric(
            "📈 期待ROI", 
            f"{avg_roi:.1f}x",
            delta="投資効果",
            help="教育投資に対する年間リターン倍率"
        )
    
    with col4:
        st.metric(
            "⏱️ 投資回収期間", 
            f"{avg_payback:.1f}ヶ月",
            delta="短期回収",
            delta_color="inverse",
            help="投資が回収されるまでの期間"
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
    
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🎯 拠点別 優先順位マトリクス</h2>
        <p class="section-subtitle">損失額とROIに基づく施策実行の優先順位</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # ビジュアル分析
    st.markdown("### 📈 拠点別パフォーマンス分析")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # 損失額とROIの散布図
        fig_scatter = px.scatter(
            df_summary,
            x='年間損失額 (M¥)',
            y='ROI',
            size='従業員数',
            color='優先度',
            hover_data=['拠点', '投資回収期間 (月)'],
            title='年間損失額 vs ROI（バブルサイズ=従業員数）',
            color_discrete_map={
                '🔴 最優先': '#d32f2f',
                '🟡 優先': '#f57c00',
                '🟢 中期対応': '#388e3c'
            }
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_chart2:
        # スキルギャップの棒グラフ
        fig_bar = px.bar(
            df_summary,
            x='拠点',
            y='スキルギャップ',
            color='優先度',
            title='拠点別スキルギャップ（ベンチマーク比）',
            color_discrete_map={
                '🔴 最優先': '#d32f2f',
                '🟡 優先': '#f57c00',
                '🟢 中期対応': '#388e3c'
            }
        )
        fig_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 経営判断のポイント
    top_location = df_summary.iloc[0]
    
    st.info(
        f"💼 **経営判断のポイント**: 最優先拠点（🔴）から教育投資を実行することで、最短{avg_payback:.1f}ヶ月で投資回収が見込まれます。\n\n"
        f"特に**{top_location['拠点']}**は年間損失額が¥{top_location['年間損失額 (M¥)']:.0f}Mと最大で、ROIも{top_location['ROI']:.1f}xと高いため、**即座のアクション推奨**。\n\n"
        f"この拠点への投資は{top_location['投資回収期間 (月)']:.1f}ヶ月で回収可能です。",
        icon="💼"
    )
    
    # 詳細分析への誘導
    st.markdown("---")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🔬 根本原因を分析する", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.session_state.target_location = top_location['拠点']
            st.rerun()
    
    with col_action2:
        if st.button("📋 アクションプランを作成", use_container_width=True):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.session_state.target_location = top_location['拠点']
            st.rerun()
    
    with col_action3:
        if st.button("📈 モニタリングを開始", use_container_width=True):
            st.session_state.selected_menu = "📈 継続モニタリング"
            st.session_state.target_location = top_location['拠点']
            st.rerun()
    
    return df_summary