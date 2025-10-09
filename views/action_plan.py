import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_action_plan(df_skill, target_location, priority_skill):
    """具体的なアクションプランの提示"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">📋 アクションプラン: {target_location}</div>
        <div class="header-subtitle">{priority_skill} スキル改善の具体的施策と投資対効果</div>
    </div>
    """, unsafe_allow_html=True)
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    low_skill_count = df_target[df_target[priority_skill] <= 2].shape[0]
    
    # 施策パッケージ
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">💡 推奨施策パッケージ（優先順位順）</h2>
        <p class="section-subtitle">即効性・投資効果・実現可能性を考慮した4つの施策</p>
    </div>
    """, unsafe_allow_html=True)
    
    action_plans = [
        {
            '施策': '🎯 即効施策',
            '内容': '日本からの技術者短期派遣',
            '対象': f'最優先ボトルネックチーム',
            '期間': '2週間 x 2回',
            'コスト': '¥3.0M',
            '効果': 'スキル +0.8pt, 効率 +5%pt',
            '実施時期': '即時 (来月から)',
            'KPI': '3ヶ月後に生産効率85%達成',
            'リスク': '低（実績あり）'
        },
        {
            '施策': '📚 中期施策',
            '内容': 'オンライン教育プログラム展開',
            '対象': f'{priority_skill}がレベル2以下の全従業員（約{low_skill_count}名）',
            '期間': '3ヶ月間 (週2時間)',
            'コスト': '¥5.0M',
            '効果': 'スキル +1.2pt, 効率 +8%pt',
            '実施時期': '2ヶ月後開始',
            'KPI': '6ヶ月後にスキル平均3.5達成',
            'リスク': '中（コンテンツ制作必要）'
        },
        {
            '施策': '👥 構造施策',
            '内容': 'ベテラン-若手ペアリング制度',
            '対象': '全チーム',
            '期間': '継続的',
            'コスト': '¥1.0M',
            '効果': 'スキルバラツキ -30%',
            '実施時期': '3ヶ月後',
            'KPI': '1年後にスキルバラツキ<0.5達成',
            'リスク': '低（運用に依存）'
        },
        {
            '施策': '🔄 リスク対応',
            '内容': 'シフト間ローテーション',
            '対象': f'低スキル者（{low_skill_count}名）',
            '期間': '3ヶ月トライアル',
            'コスト': '¥0.5M',
            '効果': 'シフト間格差 -40%',
            '実施時期': '即時可能',
            'KPI': 'シフト間効率差<3%pt',
            'リスク': '中（生産調整必要）'
        }
    ]
    
    df_actions = pd.DataFrame(action_plans)
    st.dataframe(df_actions, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 投資対効果シミュレーション
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 投資対効果シミュレーション</h2>
        <p class="section-subtitle">全施策実行時の投資額・効果・回収期間</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_cost = 3.0 + 5.0 + 1.0 + 0.5  # 百万円
    expected_efficiency_gain = 5 + 8  # %pt
    monthly_production = 1000  # 百万円
    monthly_benefit = monthly_production * (expected_efficiency_gain / 100)
    payback = total_cost / monthly_benefit
    annual_benefit = monthly_benefit * 12
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総投資額", f"¥{total_cost:.1f}M", help="4施策の合計投資額")
    
    with col2:
        st.metric("月間効果額", f"¥{monthly_benefit:.1f}M", delta="+効率改善", help="生産効率改善による月間利益増")
    
    with col3:
        st.metric("投資回収期間", f"{payback:.1f}ヶ月", delta="短期回収", delta_color="inverse", help="投資が回収されるまでの期間")
    
    with col4:
        st.metric("年間利益改善", f"¥{annual_benefit:.0f}M", delta=f"+{(annual_benefit/monthly_production/12*100):.1f}%", help="1年間の累積利益改善額")
    
    # タイムライン
    st.markdown("### 📅 実行タイムライン（今後12ヶ月）")
    
    months = list(range(1, 13))
    immediate_action = [3 if i in [1, 3] else 0 for i in months]
    mid_term_action = [0, 0] + [5/10]*10
    structural_action = [0, 0, 0] + [1/9]*9
    risk_action = [0.5]*12
    cumulative_effect = [monthly_benefit * min(i*0.3, 1) for i in months]
    
    fig_timeline = go.Figure()
    
    # 投資額の積み上げ棒グラフ
    fig_timeline.add_trace(go.Bar(
        x=months,
        y=immediate_action,
        name='即効施策',
        marker_color='#d32f2f'
    ))
    
    fig_timeline.add_trace(go.Bar(
        x=months,
        y=mid_term_action,
        name='中期施策',
        marker_color='#1976d2'
    ))
    
    fig_timeline.add_trace(go.Bar(
        x=months,
        y=structural_action,
        name='構造施策',
        marker_color='#388e3c'
    ))
    
    fig_timeline.add_trace(go.Bar(
        x=months,
        y=risk_action,
        name='リスク対応',
        marker_color='#f57c00'
    ))
    
    # 累積効果のライン
    fig_timeline.add_trace(go.Scatter(
        x=months,
        y=cumulative_effect,
        name='累積効果',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#7b1fa2', width=3),
        marker=dict(size=8)
    ))
    
    fig_timeline.update_layout(
        title='施策実行タイムラインと累積効果',
        xaxis=dict(title='月', tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title='投資額 (百万円)', range=[0, 10]),
        yaxis2=dict(
            title='累積効果 (百万円/月)', 
            overlaying='y', 
            side='right',
            range=[0, max(cumulative_effect) * 1.2]
        ),
        barmode='stack',
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # 承認判断
    st.success(
        f"✅ **実行承認の判断材料**:\n\n"
        f"- **投資回収期間**: 約{payback:.1f}ヶ月で投資が完全回収\n"
        f"- **年間利益改善**: ¥{annual_benefit:.0f}M（投資額の{(annual_benefit/total_cost):.1f}倍）\n"
        f"- **ROI**: {(annual_benefit/total_cost):.1f}x（業界平均3-5xを大きく上回る）\n\n"
        f"**結論**: 即時実行を強く推奨。特に即効施策は来月から開始可能。",
        icon="💼"
    )
    
    st.markdown("---")
    
    # 施策別詳細
    with st.expander("🎯 即効施策の詳細", expanded=False):
        st.markdown(f"""
        ### 日本からの技術者短期派遣
        
        **実施内容**:
        - 日本の{priority_skill}エキスパート2名を2週間派遣（2回実施）
        - 現場での実技指導（OJT形式）
        - ボトルネックチームへの集中トレーニング
        
        **期待効果**:
        - {priority_skill}スキル: 平均+0.8ポイント向上
        - 生産効率: +5%pt改善
        - 即座に効果が現れる（1ヶ月以内）
        
        **実施スケジュール**:
        - 第1回: 来月（Week 1-2）
        - 第2回: 3ヶ月後（Week 1-2）
        
        **投資内訳**:
        - 人件費: ¥1.5M
        - 渡航費: ¥0.8M
        - 宿泊費: ¥0.5M
        - 諸経費: ¥0.2M
        - **合計: ¥3.0M**
        """)
    
    with st.expander("📚 中期施策の詳細", expanded=False):
        st.markdown(f"""
        ### オンライン教育プログラム展開
        
        **実施内容**:
        - {priority_skill}に特化したeラーニングコンテンツ開発
        - レベル2以下の{low_skill_count}名を対象
        - 週2時間 x 12週間のカリキュラム
        - 理解度テスト + 実技評価
        
        **期待効果**:
        - {priority_skill}スキル: 平均+1.2ポイント向上
        - 生産効率: +8%pt改善
        - 6ヶ月後にスキル平均3.5達成
        
        **実施スケジュール**:
        - Month 1-2: コンテンツ制作
        - Month 3-5: 教育プログラム実施
        - Month 6: 効果測定
        
        **投資内訳**:
        - コンテンツ制作: ¥3.0M
        - プラットフォーム: ¥1.5M
        - 運用費: ¥0.5M
        - **合計: ¥5.0M**
        """)
    
    # 次のステップ
    st.markdown("---")
    
    col_final1, col_final2, col_final3 = st.columns(3)
    
    with col_final1:
        if st.button("📈 モニタリング設定", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📈 継続モニタリング"
            st.rerun()
    
    with col_final2:
        if st.button("🔬 根本原因分析に戻る", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.rerun()
    
    with col_final3:
        if st.button("📊 サマリーに戻る", use_container_width=True):
            st.session_state.selected_menu = "📊 エグゼクティブサマリー"
            st.rerun()