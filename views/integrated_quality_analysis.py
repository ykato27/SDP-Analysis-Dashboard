import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def show_integrated_quality_analysis(df_daily_prod, df_skill, target_location, skill_categories, skill_hierarchy, processes):
    """統合的な品質×力量分析 - 4つの新しい可視化手法"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🎯 統合品質×力量分析: {target_location}</div>
        <div class="header-subtitle">時系列・シフト・組織のスキルが品質に与える影響を多角的に分析</div>
    </div>
    """, unsafe_allow_html=True)
    
    # データフィルタリング
    df_filtered = df_daily_prod[df_daily_prod['拠点'] == target_location].copy()
    
    # 日付列をdatetime型に変換
    if not pd.api.types.is_datetime64_any_dtype(df_filtered['日付']):
        df_filtered['日付'] = pd.to_datetime(df_filtered['日付'])
    
    if df_filtered.empty:
        st.warning(f"{target_location}のデータが存在しません。", icon="⚠️")
        return
    
    # 日付でソート
    df_filtered = df_filtered.sort_values('日付')
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_yield = df_filtered['歩留まり (%)'].mean()
        st.metric("平均歩留まり", f"{avg_yield:.1f}%")
    
    with col2:
        avg_skill = df_filtered['平均スキル予測値'].mean()
        st.metric("平均スキルスコア", f"{avg_skill:.2f}")
    
    with col3:
        day_yield = df_filtered[df_filtered['シフト'] == '日勤']['歩留まり (%)'].mean()
        night_yield = df_filtered[df_filtered['シフト'] == '夜勤']['歩留まり (%)'].mean()
        yield_diff = day_yield - night_yield
        st.metric("日勤vs夜勤 歩留まり差", f"{yield_diff:+.2f}%")
    
    with col4:
        data_days = df_filtered['日付'].nunique()
        st.metric("データ期間", f"{data_days}日間")
    
    st.markdown("---")
    
    # 分析設定
    st.markdown("### 🔍 分析対象選択")
    col_setting1, col_setting2 = st.columns(2)
    
    with col_setting1:
        selected_process = st.selectbox(
            '分析対象の工程',
            options=processes,
            index=0,
            key='integrated_process'
        )
    
    with col_setting2:
        selected_category = st.selectbox(
            '分析対象のスキルカテゴリ',
            options=skill_categories,
            index=0,
            key='integrated_category'
        )
    
    # 選択した工程のデータ
    df_process = df_filtered[df_filtered['工程'] == selected_process].copy()
    
    if df_process.empty:
        st.warning(f"{selected_process}のデータが存在しません。", icon="⚠️")
        return
    
    st.markdown("---")
    
    # =============================================================================
    # 1. 複合時系列グラフ（1つのグラフに2軸表示：スキル×品質）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析① 複合時系列グラフ（2軸）</h2>
        <p class="section-subtitle">チーム×シフトで層別したスキルと品質の関係を1つのグラフで把握</p>
    </div>
    """, unsafe_allow_html=True)
    
    skill_col = f'{selected_category}_平均'
    
    # チーム別にデータを準備
    teams = sorted(df_process['チーム'].unique())
    
    # 2軸グラフを作成
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # カラーマップ（チーム×シフトの組み合わせ）
    team_shift_colors = {
        ('Aチーム', '日勤'): '#1f77b4',
        ('Aチーム', '夜勤'): '#5da5da',
        ('Bチーム', '日勤'): '#ff7f0e',
        ('Bチーム', '夜勤'): '#ffb366',
        ('Cチーム', '日勤'): '#2ca02c',
        ('Cチーム', '夜勤'): '#5dd05d'
    }
    
    # チーム×シフトごとにプロット
    for team in teams:
        for shift in ['日勤', '夜勤']:
            df_team_shift = df_process[(df_process['チーム'] == team) & (df_process['シフト'] == shift)].sort_values('日付')
            
            if df_team_shift.empty:
                continue
            
            color = team_shift_colors.get((team, shift), '#888888')
            line_style = 'solid' if shift == '日勤' else 'dash'
            
            # スキルスコア（左軸）
            if skill_col in df_team_shift.columns:
                fig1.add_trace(
                    go.Scatter(
                        x=df_team_shift['日付'],
                        y=df_team_shift[skill_col],
                        name=f'{team}-{shift} スキル',
                        line=dict(color=color, width=2.5, dash=line_style),
                        mode='lines+markers',
                        marker=dict(size=6),
                        legendgroup=f'{team}_{shift}',
                        hovertemplate=f'<b>{team} - {shift}</b><br>日付: %{{x}}<br>スキル: %{{y:.2f}}<extra></extra>'
                    ),
                    secondary_y=False
                )
            
            # 品質不良率（右軸）- 細い点線で表示
            fig1.add_trace(
                go.Scatter(
                    x=df_team_shift['日付'],
                    y=df_team_shift['品質不良率 (%)'],
                    name=f'{team}-{shift} 不良率',
                    line=dict(color=color, width=1.5, dash='dot'),
                    mode='lines+markers',
                    marker=dict(size=4, symbol='diamond'),
                    legendgroup=f'{team}_{shift}',
                    showlegend=False,
                    hovertemplate=f'<b>{team} - {shift}</b><br>日付: %{{x}}<br>不良率: %{{y:.2f}}%<extra></extra>'
                ),
                secondary_y=True
            )
    
    # 軸設定
    fig1.update_xaxes(title_text="日付")
    fig1.update_yaxes(title_text=f"{selected_category}スキルスコア", range=[1, 5], secondary_y=False)
    fig1.update_yaxes(title_text="品質不良率 (%)", secondary_y=True)
    
    fig1.update_layout(
        title=f"{selected_process} - スキル×品質推移（太線=スキル、細点線=不良率、実線=日勤、破線=夜勤）",
        hovermode='x unified',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # インサイト
    col_insight1, col_insight2, col_insight3 = st.columns(3)
    
    with col_insight1:
        if skill_col in df_process.columns:
            avg_skill = df_process[skill_col].mean()
            st.metric("平均スキル", f"{avg_skill:.2f}")
    
    with col_insight2:
        avg_defect = df_process['品質不良率 (%)'].mean()
        st.metric("平均不良率", f"{avg_defect:.2f}%")
    
    with col_insight3:
        # シフト別の不良率差
        df_day = df_process[df_process['シフト'] == '日勤']
        df_night = df_process[df_process['シフト'] == '夜勤']
        if not df_day.empty and not df_night.empty:
            day_defect = df_day['品質不良率 (%)'].mean()
            night_defect = df_night['品質不良率 (%)'].mean()
            diff = night_defect - day_defect
            st.metric("夜勤 - 日勤 不良率差", f"{diff:+.2f}%", delta_color="inverse")
    
    st.markdown("---")
    
    # =============================================================================
    # 2. 箱ひげ図（日勤 vs 夜勤の分布比較）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析② 箱ひげ図（日勤 vs 夜勤）</h2>
        <p class="section-subtitle">スキルと品質の分布を箱ひげ図で比較（平均・バラツキ・外れ値を把握）</p>
    </div>
    """, unsafe_allow_html=True)
    
    if skill_col in df_process.columns:
        # 2列のサブプロット（左:スキル、右:品質）
        fig2 = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                f'{selected_category}スキル分布',
                '品質不良率分布'
            ],
            horizontal_spacing=0.15
        )
        
        df_day = df_process[df_process['シフト'] == '日勤']
        df_night = df_process[df_process['シフト'] == '夜勤']
        
        # スキルの箱ひげ図（左側）
        if not df_day.empty:
            fig2.add_trace(
                go.Box(
                    y=df_day[skill_col],
                    name='日勤',
                    marker_color='#2E86DE',
                    boxmean='sd',  # 平均と標準偏差を表示
                    showlegend=True
                ),
                row=1, col=1
            )
        
        if not df_night.empty:
            fig2.add_trace(
                go.Box(
                    y=df_night[skill_col],
                    name='夜勤',
                    marker_color='#5F27CD',
                    boxmean='sd',
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # 品質不良率の箱ひげ図（右側）
        if not df_day.empty:
            fig2.add_trace(
                go.Box(
                    y=df_day['品質不良率 (%)'],
                    name='日勤',
                    marker_color='#FF6348',
                    boxmean='sd',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        if not df_night.empty:
            fig2.add_trace(
                go.Box(
                    y=df_night['品質不良率 (%)'],
                    name='夜勤',
                    marker_color='#EE5A6F',
                    boxmean='sd',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # 軸設定
        fig2.update_xaxes(title_text="シフト", row=1, col=1)
        fig2.update_xaxes(title_text="シフト", row=1, col=2)
        fig2.update_yaxes(title_text="スキルスコア", row=1, col=1)
        fig2.update_yaxes(title_text="品質不良率 (%)", row=1, col=2)
        
        fig2.update_layout(
            title=f"{selected_process} - シフト別分布比較（箱=四分位範囲、線=中央値、◇=平均、ひげ=1.5×IQR）",
            height=500
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # 統計比較テーブル
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.markdown("#### 📊 スキル統計比較")
            
            if not df_day.empty and not df_night.empty:
                stat_data = {
                    '指標': ['平均', '中央値', '標準偏差', '第1四分位', '第3四分位'],
                    '日勤': [
                        f"{df_day[skill_col].mean():.2f}",
                        f"{df_day[skill_col].median():.2f}",
                        f"{df_day[skill_col].std():.2f}",
                        f"{df_day[skill_col].quantile(0.25):.2f}",
                        f"{df_day[skill_col].quantile(0.75):.2f}"
                    ],
                    '夜勤': [
                        f"{df_night[skill_col].mean():.2f}",
                        f"{df_night[skill_col].median():.2f}",
                        f"{df_night[skill_col].std():.2f}",
                        f"{df_night[skill_col].quantile(0.25):.2f}",
                        f"{df_night[skill_col].quantile(0.75):.2f}"
                    ]
                }
                
                st.dataframe(pd.DataFrame(stat_data), use_container_width=True, hide_index=True)
        
        with col_stat2:
            st.markdown("#### 📊 品質統計比較")
            
            if not df_day.empty and not df_night.empty:
                stat_data = {
                    '指標': ['平均', '中央値', '標準偏差', '第1四分位', '第3四分位'],
                    '日勤': [
                        f"{df_day['品質不良率 (%)'].mean():.2f}%",
                        f"{df_day['品質不良率 (%)'].median():.2f}%",
                        f"{df_day['品質不良率 (%)'].std():.2f}%",
                        f"{df_day['品質不良率 (%)'].quantile(0.25):.2f}%",
                        f"{df_day['品質不良率 (%)'].quantile(0.75):.2f}%"
                    ],
                    '夜勤': [
                        f"{df_night['品質不良率 (%)'].mean():.2f}%",
                        f"{df_night['品質不良率 (%)'].median():.2f}%",
                        f"{df_night['品質不良率 (%)'].std():.2f}%",
                        f"{df_night['品質不良率 (%)'].quantile(0.25):.2f}%",
                        f"{df_night['品質不良率 (%)'].quantile(0.75):.2f}%"
                    ]
                }
                
                st.dataframe(pd.DataFrame(stat_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # =============================================================================
    # 3. ファセットグラフ（Small Multiples）- チームフィルター付き
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析③ ファセットグラフ（Small Multiples）</h2>
        <p class="section-subtitle">シフト間の差を同じ形式のグラフで並べて比較（チームフィルター機能付き）</p>
    </div>
    """, unsafe_allow_html=True)
    
    # チーム選択フィルター
    teams_available = sorted(df_process['チーム'].unique())
    
    col_filter1, col_filter2 = st.columns([2, 1])
    
    with col_filter1:
        selected_teams = st.multiselect(
            '表示するチーム（A, B, C）を選択',
            options=teams_available,
            default=teams_available,
            key='facet_team_filter'
        )
    
    with col_filter2:
        st.markdown("##### フィルターオプション")
        show_avg_lines = st.checkbox('平均値ラインを表示', value=True, key='show_avg_lines')
    
    if not selected_teams:
        st.warning("チームを1つ以上選択してください", icon="⚠️")
    else:
        # 選択されたチームのデータのみフィルタリング
        df_filtered_teams = df_process[df_process['チーム'].isin(selected_teams)].copy()
        
        if skill_col in df_filtered_teams.columns:
            # 2行1列のサブプロット（上段=日勤、下段=夜勤）
            fig3 = make_subplots(
                rows=2, cols=1,
                subplot_titles=['☀️ 日勤シフト - スキル×品質推移', '🌙 夜勤シフト - スキル×品質推移'],
                specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                vertical_spacing=0.15
            )
            
            team_colors = {
                'Aチーム': '#1f77b4',
                'Bチーム': '#ff7f0e',
                'Cチーム': '#2ca02c'
            }
            
            shifts = [('日勤', 1), ('夜勤', 2)]
            
            for shift_name, row in shifts:
                df_shift = df_filtered_teams[df_filtered_teams['シフト'] == shift_name]
                
                if not df_shift.empty:
                    # チーム別にプロット
                    for team in selected_teams:
                        df_team_shift = df_shift[df_shift['チーム'] == team]
                        
                        if not df_team_shift.empty:
                            # スキルスコア
                            fig3.add_trace(
                                go.Scatter(
                                    x=df_team_shift['日付'],
                                    y=df_team_shift[skill_col],
                                    name=f'{team}',
                                    line=dict(color=team_colors.get(team, '#888888'), width=2.5),
                                    mode='lines+markers',
                                    marker=dict(size=6),
                                    legendgroup=f'{shift_name}_{team}',
                                    showlegend=(row == 1),
                                    hovertemplate=f'<b>{shift_name} - {team}</b><br>日付: %{{x}}<br>スキル: %{{y:.2f}}<extra></extra>'
                                ),
                                row=row, col=1,
                                secondary_y=False
                            )
                            
                            # 品質不良率
                            fig3.add_trace(
                                go.Scatter(
                                    x=df_team_shift['日付'],
                                    y=df_team_shift['品質不良率 (%)'],
                                    name=f'{team} (不良率)',
                                    line=dict(color=team_colors.get(team, '#888888'), width=2, dash='dash'),
                                    mode='lines+markers',
                                    marker=dict(size=5),
                                    legendgroup=f'{shift_name}_{team}',
                                    showlegend=False,
                                    hovertemplate=f'<b>{shift_name} - {team}</b><br>日付: %{{x}}<br>不良率: %{{y:.2f}}%<extra></extra>'
                                ),
                                row=row, col=1,
                                secondary_y=True
                            )
                    
                    # 平均線を追加（オプション）
                    if show_avg_lines:
                        skill_mean = df_shift[skill_col].mean()
                        defect_mean = df_shift['品質不良率 (%)'].mean()
                        
                        fig3.add_hline(
                            y=skill_mean,
                            line=dict(color='blue', dash='dot', width=2),
                            row=row, col=1,
                            secondary_y=False,
                            annotation_text=f"平均スキル: {skill_mean:.2f}",
                            annotation_position="right"
                        )
                        
                        fig3.add_hline(
                            y=defect_mean,
                            line=dict(color='red', dash='dot', width=2),
                            row=row, col=1,
                            secondary_y=True,
                            annotation_text=f"平均不良率: {defect_mean:.2f}%",
                            annotation_position="left"
                        )
            
            # 軸設定
            fig3.update_xaxes(title_text="日付", row=2, col=1)
            fig3.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=1, col=1, secondary_y=False)
            fig3.update_yaxes(title_text="不良率 (%)", row=1, col=1, secondary_y=True)
            fig3.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=2, col=1, secondary_y=False)
            fig3.update_yaxes(title_text="不良率 (%)", row=2, col=1, secondary_y=True)
            
            fig3.update_layout(
                title=f"{selected_process} - シフト別比較（実線=スキル、破線=不良率、点線=平均値）",
                hovermode='x unified',
                height=800,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.08,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            # チーム別統計サマリー（簡潔版）
            st.markdown("#### 📊 チーム別統計サマリー")
            
            summary_data = []
            
            for team in selected_teams:
                df_team = df_filtered_teams[df_filtered_teams['チーム'] == team]
                
                for shift in ['日勤', '夜勤']:
                    df_team_shift = df_team[df_team['シフト'] == shift]
                    
                    if not df_team_shift.empty and skill_col in df_team_shift.columns:
                        summary_data.append({
                            'チーム': team,
                            'シフト': shift,
                            '平均スキル': f"{df_team_shift[skill_col].mean():.2f}",
                            '平均不良率': f"{df_team_shift['品質不良率 (%)'].mean():.2f}%",
                            'データ数': len(df_team_shift)
                        })
            
            if summary_data:
                df_summary_table = pd.DataFrame(summary_data)
                st.dataframe(df_summary_table, use_container_width=True, hide_index=True)
            else:
                st.info("選択されたチームのデータがありません", icon="ℹ️")
    
    # 次のステップ
    st.markdown("---")
    
    col_next1, col_next2, col_next3 = st.columns(3)
    
    with col_next1:
        if st.button("🔬 根本原因分析へ", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.rerun()
    
    with col_next2:
        if st.button("📋 アクションプラン作成", use_container_width=True):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.rerun()
    
    with col_next3:
        if st.button("📈 従来の分析へ", use_container_width=True):
            st.session_state.selected_menu = "📈 品質×力量分析"
            st.rerun()