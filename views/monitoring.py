import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def show_monitoring_dashboard(df_daily_prod, target_location):
    """施策実行後のモニタリング"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">📈 継続モニタリングダッシュボード: {target_location}</div>
        <div class="header-subtitle">施策実行後のKPI追跡と早期警告システム</div>
    </div>
    """, unsafe_allow_html=True)
    
    df_target_daily = df_daily_prod[df_daily_prod['拠点'] == target_location].copy()
    df_target_daily = df_target_daily.groupby('日付').mean(numeric_only=True).reset_index()
    
    if df_target_daily.empty:
        st.warning(f"{target_location}の日次データが存在しません。", icon="⚠️")
        return
    
    # 現在の健全性スコア計算
    target_efficiency = 85
    target_skill = 3.5
    target_defect = 3.0
    
    latest_data = df_target_daily.iloc[-1]
    latest_health = (
        (latest_data['生産効率 (%)'] / target_efficiency * 40) +
        (latest_data['平均スキル予測値'] / target_skill * 30) +
        ((10 - latest_data['品質不良率 (%)']) / 7 * 30)
    )
    latest_health = min(max(latest_health, 0), 100)
    
    # KPIサマリー
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_efficiency = latest_data['生産効率 (%)']
        st.metric(
            "現在の生産効率",
            f"{current_efficiency:.1f}%",
            delta=f"{current_efficiency - target_efficiency:.1f}%",
            delta_color="normal",
            help=f"目標: {target_efficiency}%"
        )
    
    with col2:
        current_skill = latest_data['平均スキル予測値']
        st.metric(
            "現在のスキルスコア",
            f"{current_skill:.2f}",
            delta=f"{current_skill - target_skill:.2f}",
            delta_color="normal",
            help=f"目標: {target_skill}"
        )
    
    with col3:
        current_defect = latest_data['品質不良率 (%)']
        st.metric(
            "現在の品質不良率",
            f"{current_defect:.2f}%",
            delta=f"{current_defect - target_defect:.2f}%",
            delta_color="inverse",
            help=f"目標: {target_defect}%以下"
        )
    
    with col4:
        health_color = "normal" if latest_health >= 80 else "inverse"
        st.metric(
            "総合健全性スコア",
            f"{latest_health:.1f}",
            delta="健全" if latest_health >= 80 else "要注意",
            delta_color=health_color,
            help="0-100スコア（80以上が健全）"
        )
    
    # アラート表示
    if latest_health < 70:
        st.error(
            f"🚨 **緊急アラート**: 健全性スコアが{latest_health:.1f}に低下しています。\n\n"
            f"**即座の介入が必要**:\n"
            f"- 生産効率: {current_efficiency:.1f}% (目標: {target_efficiency}%)\n"
            f"- スキルスコア: {current_skill:.2f} (目標: {target_skill})\n"
            f"- 品質不良率: {current_defect:.2f}% (目標: {target_defect}%以下)\n\n"
            f"推奨アクション: 緊急ミーティングの開催、現場ヒアリングの実施",
            icon="⚠️"
        )
    elif latest_health < 80:
        st.warning(
            f"⚠️ **注意**: 健全性スコアが{latest_health:.1f}です。\n\n"
            f"モニタリングを強化し、改善施策の効果を確認してください。",
            icon="👀"
        )
    else:
        st.success(
            f"✅ **良好**: 健全性スコア{latest_health:.1f}。目標達成に向けて順調です。\n\n"
            f"現在の施策を継続し、定期的なモニタリングを実施してください。",
            icon="🎯"
        )
    
    st.markdown("---")
    
    # KPIトレンドグラフ
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 KPIトレンド（過去30日間）</h2>
        <p class="section-subtitle">各指標の推移と目標達成状況を可視化</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 健全性スコアの計算（全期間）
    df_target_daily['健全性スコア'] = (
        (df_target_daily['生産効率 (%)'] / target_efficiency * 40) +
        (df_target_daily['平均スキル予測値'] / target_skill * 30) +
        ((10 - df_target_daily['品質不良率 (%)']) / 7 * 30)
    ).clip(0, 100)
    
    # 4つのサブプロット
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '生産効率トレンド',
            'スキルスコアトレンド',
            '品質不良率トレンド',
            '総合健全性スコア'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. 生産効率
    fig.add_trace(
        go.Scatter(
            x=df_target_daily['日付'],
            y=df_target_daily['生産効率 (%)'],
            name='生産効率',
            line=dict(color='#1976d2', width=2),
            mode='lines+markers'
        ),
        row=1, col=1
    )
    fig.add_hline(
        y=target_efficiency,
        line_dash="dash",
        line_color="green",
        annotation_text="目標",
        row=1, col=1
    )
    
    # 2. スキルスコア
    fig.add_trace(
        go.Scatter(
            x=df_target_daily['日付'],
            y=df_target_daily['平均スキル予測値'],
            name='スキルスコア',
            line=dict(color='#f57c00', width=2),
            mode='lines+markers'
        ),
        row=1, col=2
    )
    fig.add_hline(
        y=target_skill,
        line_dash="dash",
        line_color="green",
        annotation_text="目標",
        row=1, col=2
    )
    
    # 3. 品質不良率
    fig.add_trace(
        go.Scatter(
            x=df_target_daily['日付'],
            y=df_target_daily['品質不良率 (%)'],
            name='品質不良率',
            line=dict(color='#d32f2f', width=2),
            mode='lines+markers'
        ),
        row=2, col=1
    )
    fig.add_hline(
        y=target_defect,
        line_dash="dash",
        line_color="green",
        annotation_text="目標",
        row=2, col=1
    )
    
    # 4. 健全性スコア
    fig.add_trace(
        go.Scatter(
            x=df_target_daily['日付'],
            y=df_target_daily['健全性スコア'],
            name='健全性',
            line=dict(color='#7b1fa2', width=2),
            fill='tozeroy',
            mode='lines+markers'
        ),
        row=2, col=2
    )
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="green",
        annotation_text="健全ライン",
        row=2, col=2
    )
    
    # レイアウト設定
    fig.update_xaxes(title_text="日付", row=1, col=1)
    fig.update_xaxes(title_text="日付", row=1, col=2)
    fig.update_xaxes(title_text="日付", row=2, col=1)
    fig.update_xaxes(title_text="日付", row=2, col=2)
    
    fig.update_yaxes(title_text="効率 (%)", row=1, col=1)
    fig.update_yaxes(title_text="スコア", row=1, col=2)
    fig.update_yaxes(title_text="不良率 (%)", row=2, col=1)
    fig.update_yaxes(title_text="スコア (0-100)", row=2, col=2)
    
    fig.update_layout(
        height=700,
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # トレンド分析
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📈 トレンド分析と洞察</h2>
        <p class="section-subtitle">過去7日間 vs 過去30日間の比較</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 過去7日と過去30日の平均を計算
    recent_7days = df_target_daily.tail(7)
    full_period = df_target_daily
    
    col_trend1, col_trend2, col_trend3 = st.columns(3)
    
    with col_trend1:
        efficiency_7d = recent_7days['生産効率 (%)'].mean()
        efficiency_30d = full_period['生産効率 (%)'].mean()
        efficiency_trend = efficiency_7d - efficiency_30d
        
        st.metric(
            "生産効率（直近7日平均）",
            f"{efficiency_7d:.1f}%",
            delta=f"{efficiency_trend:.1f}%",
            delta_color="normal",
            help="過去30日平均との比較"
        )
        
        if efficiency_trend > 0:
            st.success("✅ 改善トレンド", icon="📈")
        else:
            st.error("⚠️ 悪化トレンド", icon="📉")
    
    with col_trend2:
        skill_7d = recent_7days['平均スキル予測値'].mean()
        skill_30d = full_period['平均スキル予測値'].mean()
        skill_trend = skill_7d - skill_30d
        
        st.metric(
            "スキルスコア（直近7日平均）",
            f"{skill_7d:.2f}",
            delta=f"{skill_trend:.2f}",
            delta_color="normal",
            help="過去30日平均との比較"
        )
        
        if skill_trend > 0:
            st.success("✅ 向上トレンド", icon="📈")
        else:
            st.error("⚠️ 低下トレンド", icon="📉")
    
    with col_trend3:
        defect_7d = recent_7days['品質不良率 (%)'].mean()
        defect_30d = full_period['品質不良率 (%)'].mean()
        defect_trend = defect_7d - defect_30d
        
        st.metric(
            "品質不良率（直近7日平均）",
            f"{defect_7d:.2f}%",
            delta=f"{defect_trend:.2f}%",
            delta_color="inverse",
            help="過去30日平均との比較"
        )
        
        if defect_trend < 0:
            st.success("✅ 改善トレンド", icon="📈")
        else:
            st.error("⚠️ 悪化トレンド", icon="📉")
    
    # 分析コメント
    st.info(
        "💡 **分析の洞察**:\n\n"
        f"生産効率の{'改善' if efficiency_trend > 0 else '低下'}と平均スキル予測値の{'向上' if skill_trend > 0 else '低下'}が"
        f"{'同期' if (efficiency_trend > 0) == (skill_trend > 0) else '非同期'}しています。\n\n"
        f"{'スキル改善施策が効果を発揮している可能性があります。' if skill_trend > 0 else 'スキル向上施策の強化が必要です。'}\n\n"
        f"特に、{'夜勤' if latest_data.get('シフト') == '夜勤' else '日勤'}での"
        f"{'生産効率が急落している場合、そのシフトメンバーのスキルレベルや設備トラブルへの対応能力が課題である可能性があります。' if efficiency_trend < 0 else '生産が安定しています。'}",
        icon="📊"
    )
    
    st.markdown("---")
    
    # アクション推奨
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📋 改善施策を確認", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.rerun()
    
    with col_action2:
        if st.button("🔬 詳細分析を実施", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.rerun()
    
    with col_action3:
        if st.button("📁 生データを確認", use_container_width=True):
            st.session_state.selected_menu = "📁 生データ閲覧"
            st.rerun()