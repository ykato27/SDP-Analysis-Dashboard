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
    # 1. 複合時系列グラフ（スキルと品質を2つのグラフに分割、シフト稼働状況を背景色で表示）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析① 複合時系列グラフ</h2>
        <p class="section-subtitle">スキルと品質の時系列推移（背景色でシフト稼働状況を表示）</p>
    </div>
    """, unsafe_allow_html=True)
    
    skill_col = f'{selected_category}_平均'
    
    # チーム別にデータを準備（シフト稼働状況を把握するため）
    teams = sorted(df_process['チーム'].unique())
    
    # 2つのサブプロット作成（上:スキル、下:品質）
    fig1 = make_subplots(
        rows=2, cols=1,
        subplot_titles=[
            f'{selected_category}スキル推移（チーム別）',
            '品質不良率推移（チーム別）'
        ],
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )
    
    # カラーマップ
    team_colors = {
        'Aチーム': '#1f77b4',
        'Bチーム': '#ff7f0e', 
        'Cチーム': '#2ca02c'
    }
    
    shift_backgrounds = {
        '日勤': 'rgba(255, 235, 153, 0.3)',  # 薄い黄色
        '夜勤': 'rgba(100, 100, 150, 0.2)'   # 薄い青
    }
    
    # 各チームのデータをプロット
    for team in teams:
        df_team = df_process[df_process['チーム'] == team].sort_values('日付')
        
        if df_team.empty:
            continue
        
        # スキルスコア（上段）
        if skill_col in df_team.columns:
            fig1.add_trace(
                go.Scatter(
                    x=df_team['日付'],
                    y=df_team[skill_col],
                    name=f'{team}',
                    line=dict(color=team_colors.get(team, '#888888'), width=2.5),
                    mode='lines+markers',
                    marker=dict(size=5),
                    legendgroup=team,
                    hovertemplate=f'<b>{team}</b><br>日付: %{{x}}<br>シフト: %{{text}}<br>スキル: %{{y:.2f}}<extra></extra>',
                    text=df_team['シフト']
                ),
                row=1, col=1
            )
        
        # 品質不良率（下段）
        fig1.add_trace(
            go.Scatter(
                x=df_team['日付'],
                y=df_team['品質不良率 (%)'],
                name=f'{team}',
                line=dict(color=team_colors.get(team, '#888888'), width=2.5),
                mode='lines+markers',
                marker=dict(size=5),
                legendgroup=team,
                showlegend=False,
                hovertemplate=f'<b>{team}</b><br>日付: %{{x}}<br>シフト: %{{text}}<br>不良率: %{{y:.2f}}%<extra></extra>',
                text=df_team['シフト']
            ),
            row=2, col=1
        )
    
    # シフト稼働状況を背景色で表示
    # 各日付のシフト状況を取得
    date_shift_map = {}
    for date in df_process['日付'].unique():
        shifts_on_date = df_process[df_process['日付'] == date]['シフト'].unique()
        if len(shifts_on_date) == 1:
            date_shift_map[date] = shifts_on_date[0]
        else:
            date_shift_map[date] = '混合'
    
    # 連続した同じシフトの期間を背景色で塗る
    current_shift = None
    start_date = None
    
    sorted_dates = sorted(date_shift_map.keys())
    
    for i, date in enumerate(sorted_dates):
        shift = date_shift_map[date]
        
        if shift != current_shift:
            # 前の期間を描画
            if current_shift and current_shift != '混合' and start_date:
                for row in [1, 2]:
                    fig1.add_vrect(
                        x0=start_date,
                        x1=date,
                        fillcolor=shift_backgrounds.get(current_shift, 'rgba(200,200,200,0.1)'),
                        layer="below",
                        line_width=0,
                        row=row, col=1
                    )
            
            # 新しい期間開始
            current_shift = shift
            start_date = date
    
    # 最後の期間を描画
    if current_shift and current_shift != '混合' and start_date:
        end_date = sorted_dates[-1] + pd.Timedelta(days=1)
        for row in [1, 2]:
            fig1.add_vrect(
                x0=start_date,
                x1=end_date,
                fillcolor=shift_backgrounds.get(current_shift, 'rgba(200,200,200,0.1)'),
                layer="below",
                line_width=0,
                row=row, col=1
            )
    
    # 軸設定
    fig1.update_xaxes(title_text="日付", row=2, col=1)
    fig1.update_yaxes(title_text="スキルスコア", range=[1, 5], row=1, col=1)
    fig1.update_yaxes(title_text="品質不良率 (%)", row=2, col=1)
    
    fig1.update_layout(
        title=f"{selected_process} - スキル・品質推移（背景色: 黄=日勤、青=夜勤）",
        hovermode='x unified',
        height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
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
    # 2. 相関分析（ヒストグラム比較：日勤 vs 夜勤）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析② ヒストグラム比較（日勤 vs 夜勤）</h2>
        <p class="section-subtitle">スキルと品質の分布をシフト別に比較</p>
    </div>
    """, unsafe_allow_html=True)
    
    if skill_col in df_process.columns:
        # 2x2のサブプロット（左上:日勤スキル、右上:夜勤スキル、左下:日勤品質、右下:夜勤品質）
        fig2 = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '☀️ 日勤 - スキル分布',
                '🌙 夜勤 - スキル分布',
                '☀️ 日勤 - 品質不良率分布',
                '🌙 夜勤 - 品質不良率分布'
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        df_day = df_process[df_process['シフト'] == '日勤']
        df_night = df_process[df_process['シフト'] == '夜勤']
        
        # 日勤スキル
        if not df_day.empty:
            fig2.add_trace(
                go.Histogram(
                    x=df_day[skill_col],
                    name='日勤 スキル',
                    marker_color='#2E86DE',
                    opacity=0.7,
                    nbinsx=15,
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # 平均線
            mean_val = df_day[skill_col].mean()
            fig2.add_vline(
                x=mean_val,
                line=dict(color='red', dash='dash', width=2),
                row=1, col=1,
                annotation_text=f"平均: {mean_val:.2f}",
                annotation_position="top"
            )
        
        # 夜勤スキル
        if not df_night.empty:
            fig2.add_trace(
                go.Histogram(
                    x=df_night[skill_col],
                    name='夜勤 スキル',
                    marker_color='#5F27CD',
                    opacity=0.7,
                    nbinsx=15,
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # 平均線
            mean_val = df_night[skill_col].mean()
            fig2.add_vline(
                x=mean_val,
                line=dict(color='red', dash='dash', width=2),
                row=1, col=2,
                annotation_text=f"平均: {mean_val:.2f}",
                annotation_position="top"
            )
        
        # 日勤品質
        if not df_day.empty:
            fig2.add_trace(
                go.Histogram(
                    x=df_day['品質不良率 (%)'],
                    name='日勤 不良率',
                    marker_color='#FF6348',
                    opacity=0.7,
                    nbinsx=15,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # 平均線
            mean_val = df_day['品質不良率 (%)'].mean()
            fig2.add_vline(
                x=mean_val,
                line=dict(color='red', dash='dash', width=2),
                row=2, col=1,
                annotation_text=f"平均: {mean_val:.2f}%",
                annotation_position="top"
            )
        
        # 夜勤品質
        if not df_night.empty:
            fig2.add_trace(
                go.Histogram(
                    x=df_night['品質不良率 (%)'],
                    name='夜勤 不良率',
                    marker_color='#EE5A6F',
                    opacity=0.7,
                    nbinsx=15,
                    showlegend=False
                ),
                row=2, col=2
            )
            
            # 平均線
            mean_val = df_night['品質不良率 (%)'].mean()
            fig2.add_vline(
                x=mean_val,
                line=dict(color='red', dash='dash', width=2),
                row=2, col=2,
                annotation_text=f"平均: {mean_val:.2f}%",
                annotation_position="top"
            )
        
        # 軸設定
        fig2.update_xaxes(title_text="スキルスコア", row=1, col=1)
        fig2.update_xaxes(title_text="スキルスコア", row=1, col=2)
        fig2.update_xaxes(title_text="品質不良率 (%)", row=2, col=1)
        fig2.update_xaxes(title_text="品質不良率 (%)", row=2, col=2)
        
        fig2.update_yaxes(title_text="頻度", row=1, col=1)
        fig2.update_yaxes(title_text="頻度", row=1, col=2)
        fig2.update_yaxes(title_text="頻度", row=2, col=1)
        fig2.update_yaxes(title_text="頻度", row=2, col=2)
        
        fig2.update_layout(
            title=f"{selected_process} - シフト別 スキル・品質分布（赤線=平均値）",
            height=700
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # 統計比較テーブル
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.markdown("#### 📊 スキル統計比較")
            
            if not df_day.empty and not df_night.empty:
                stat_data = {
                    '指標': ['平均', '中央値', '標準偏差', '最小値', '最大値'],
                    '日勤': [
                        f"{df_day[skill_col].mean():.2f}",
                        f"{df_day[skill_col].median():.2f}",
                        f"{df_day[skill_col].std():.2f}",
                        f"{df_day[skill_col].min():.2f}",
                        f"{df_day[skill_col].max():.2f}"
                    ],
                    '夜勤': [
                        f"{df_night[skill_col].mean():.2f}",
                        f"{df_night[skill_col].median():.2f}",
                        f"{df_night[skill_col].std():.2f}",
                        f"{df_night[skill_col].min():.2f}",
                        f"{df_night[skill_col].max():.2f}"
                    ],
                    '差分': [
                        f"{df_night[skill_col].mean() - df_day[skill_col].mean():+.2f}",
                        f"{df_night[skill_col].median() - df_day[skill_col].median():+.2f}",
                        f"{df_night[skill_col].std() - df_day[skill_col].std():+.2f}",
                        "-",
                        "-"
                    ]
                }
                
                st.dataframe(pd.DataFrame(stat_data), use_container_width=True, hide_index=True)
        
        with col_stat2:
            st.markdown("#### 📊 品質統計比較")
            
            if not df_day.empty and not df_night.empty:
                stat_data = {
                    '指標': ['平均', '中央値', '標準偏差', '最小値', '最大値'],
                    '日勤': [
                        f"{df_day['品質不良率 (%)'].mean():.2f}%",
                        f"{df_day['品質不良率 (%)'].median():.2f}%",
                        f"{df_day['品質不良率 (%)'].std():.2f}%",
                        f"{df_day['品質不良率 (%)'].min():.2f}%",
                        f"{df_day['品質不良率 (%)'].max():.2f}%"
                    ],
                    '夜勤': [
                        f"{df_night['品質不良率 (%)'].mean():.2f}%",
                        f"{df_night['品質不良率 (%)'].median():.2f}%",
                        f"{df_night['品質不良率 (%)'].std():.2f}%",
                        f"{df_night['品質不良率 (%)'].min():.2f}%",
                        f"{df_night['品質不良率 (%)'].max():.2f}%"
                    ],
                    '差分': [
                        f"{df_night['品質不良率 (%)'].mean() - df_day['品質不良率 (%)'].mean():+.2f}%",
                        f"{df_night['品質不良率 (%)'].median() - df_day['品質不良率 (%)'].median():+.2f}%",
                        f"{df_night['品質不良率 (%)'].std() - df_day['品質不良率 (%)'].std():+.2f}%",
                        "-",
                        "-"
                    ]
                }
                
                st.dataframe(pd.DataFrame(stat_data), use_container_width=True, hide_index=True)
        
        # インサイト
        if not df_day.empty and not df_night.empty:
            skill_diff = df_night[skill_col].mean() - df_day[skill_col].mean()
            defect_diff = df_night['品質不良率 (%)'].mean() - df_day['品質不良率 (%)'].mean()
            
            if abs(skill_diff) > 0.2 or abs(defect_diff) > 0.5:
                st.warning(
                    f"⚠️ **シフト間で有意な差が検出されました**\n\n"
                    f"• スキル差: {skill_diff:+.2f}\n\n"
                    f"• 品質差: {defect_diff:+.2f}%\n\n"
                    f"→ {'夜勤' if defect_diff > 0 else '日勤'}シフトの改善施策を優先してください",
                    icon="🔍"
                )
            else:
                st.success(
                    f"✅ **シフト間のパフォーマンスは均等です**\n\n"
                    f"• スキル差: {skill_diff:+.2f} (小さい)\n\n"
                    f"• 品質差: {defect_diff:+.2f}% (小さい)\n\n"
                    f"→ 現在のシフト運用を継続してください",
                    icon="👍"
                )
    
    st.markdown("---")
    
    # =============================================================================
    # 3. 散布図（スキル vs 品質の相関）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🎯 分析③ 相関散布図</h2>
        <p class="section-subtitle">スキルと品質の関係を可視化</p>
    </div>
    """, unsafe_allow_html=True)
    
    if skill_col in df_process.columns:
        fig3 = go.Figure()
        
        # シフト別のプロット
        for shift in ['日勤', '夜勤']:
            df_shift = df_process[df_process['シフト'] == shift]
            
            fig3.add_trace(go.Scatter(
                x=df_shift[skill_col],
                y=df_shift['品質不良率 (%)'],
                mode='markers',
                marker=dict(
                    size=8,
                    color='#2E86DE' if shift == '日勤' else '#5F27CD',
                    opacity=0.6,
                    line=dict(width=1, color='white')
                ),
                name=shift,
                text=df_shift['日付'].dt.strftime('%Y-%m-%d'),
                hovertemplate=(
                    '<b>%{text}</b><br>'
                    f'{shift}<br>'
                    f'スキル: %{{x:.2f}}<br>'
                    f'不良率: %{{y:.2f}}%<br>'
                    '<extra></extra>'
                )
            ))
        
        # トレンドライン
        try:
            from scipy import stats
            x_data = df_process[skill_col].dropna()
            y_data = df_process.loc[x_data.index, '品質不良率 (%)']
            
            if len(x_data) > 2:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                line_x = np.linspace(x_data.min(), x_data.max(), 100)
                line_y = slope * line_x + intercept
                
                fig3.add_trace(go.Scatter(
                    x=line_x,
                    y=line_y,
                    mode='lines',
                    name=f'トレンド (R²={r_value**2:.3f})',
                    line=dict(color='red', dash='dash', width=3)
                ))
                
                # 相関係数を表示
                col_corr1, col_corr2, col_corr3 = st.columns(3)
                
                with col_corr1:
                    st.metric("相関係数 (R)", f"{r_value:.3f}")
                
                with col_corr2:
                    st.metric("決定係数 (R²)", f"{r_value**2:.3f}")
                
                with col_corr3:
                    corr_strength = "強" if abs(r_value) > 0.7 else ("中" if abs(r_value) > 0.4 else "弱")
                    st.metric("相関強度", corr_strength)
        except ImportError:
            st.warning("scipyがインストールされていないため、トレンドラインを表示できません。", icon="⚠️")
        
        fig3.update_layout(
            title=f"{selected_process} - スキル vs 品質不良率",
            xaxis_title=f"{selected_category}スキル スコア",
            yaxis_title="品質不良率 (%)",
            height=500
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # =============================================================================
    # 4. ファセットグラフ（Small Multiples）- チームフィルター付き
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析④ ファセットグラフ（Small Multiples）</h2>
        <p class="section-subtitle">シフト間の差を同じ形式のグラフで並べて比較（チームフィルター機能付き）</p>
    </div>
    """, unsafe_allow_html=True)
    
    # チーム選択フィルター
    teams_available = sorted(df_process['チーム'].unique())
    
    col_filter1, col_filter2 = st.columns([2, 1])
    
    with col_filter1:
        selected_teams = st.multiselect(
            '表示するチームを選択',
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
            fig4 = make_subplots(
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
                            fig4.add_trace(
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
                            fig4.add_trace(
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
                        
                        fig4.add_hline(
                            y=skill_mean,
                            line=dict(color='blue', dash='dot', width=2),
                            row=row, col=1,
                            secondary_y=False,
                            annotation_text=f"平均スキル: {skill_mean:.2f}",
                            annotation_position="right"
                        )
                        
                        fig4.add_hline(
                            y=defect_mean,
                            line=dict(color='red', dash='dot', width=2),
                            row=row, col=1,
                            secondary_y=True,
                            annotation_text=f"平均不良率: {defect_mean:.2f}%",
                            annotation_position="left"
                        )
            
            # 軸設定
            fig4.update_xaxes(title_text="日付", row=2, col=1)
            fig4.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=1, col=1, secondary_y=False)
            fig4.update_yaxes(title_text="不良率 (%)", row=1, col=1, secondary_y=True)
            fig4.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=2, col=1, secondary_y=False)
            fig4.update_yaxes(title_text="不良率 (%)", row=2, col=1, secondary_y=True)
            
            fig4.update_layout(
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
            
            st.plotly_chart(fig4, use_container_width=True)
            
            # チーム別シフト比較サマリー
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
                            'データ数': len(df_team_shift),
                            'スキル標準偏差': f"{df_team_shift[skill_col].std():.2f}",
                            '不良率標準偏差': f"{df_team_shift['品質不良率 (%)'].std():.2f}%"
                        })
            
            if summary_data:
                df_summary_table = pd.DataFrame(summary_data)
                st.dataframe(df_summary_table, use_container_width=True, hide_index=True)
                
                # チーム間の差分分析
                st.markdown("#### 💡 チーム間の差分分析")
                
                # 各シフトでの最高・最低パフォーマンスチーム
                for shift in ['日勤', '夜勤']:
                    shift_data = [d for d in summary_data if d['シフト'] == shift]
                    
                    if len(shift_data) > 1:
                        # 不良率で比較
                        defect_rates = [(d['チーム'], float(d['平均不良率'].rstrip('%'))) for d in shift_data]
                        best_team = min(defect_rates, key=lambda x: x[1])
                        worst_team = max(defect_rates, key=lambda x: x[1])
                        
                        diff = worst_team[1] - best_team[1]
                        
                        if diff > 0.5:
                            st.info(
                                f"**{shift}シフト分析**\n\n"
                                f"• 最優秀: {best_team[0]} ({best_team[1]:.2f}%)\n\n"
                                f"• 要改善: {worst_team[0]} ({worst_team[1]:.2f}%)\n\n"
                                f"• 差分: {diff:.2f}%\n\n"
                                f"→ {best_team[0]}のベストプラクティスを{worst_team[0]}に展開",
                                icon="📊"
                            )
            else:
                st.info("選択されたチームのデータがありません", icon="ℹ️")
    
    st.markdown("---")
    
    # 総合インサイト
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">💡 総合インサイト</h2>
        <p class="section-subtitle">4つの分析から得られる戦略的示唆</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 総合分析
    insights = []
    
    # スキルと品質の相関
    if skill_col in df_process.columns:
        try:
            from scipy import stats
            x_data = df_process[skill_col].dropna()
            y_data = df_process.loc[x_data.index, '品質不良率 (%)']
            
            if len(x_data) > 2:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                
                if r_value < -0.5:
                    insights.append(
                        f"✅ **{selected_category}スキルと品質に強い負の相関** (R={r_value:.3f})\n"
                        f"→ このスキルへの投資で品質改善が期待できます"
                    )
                elif r_value < -0.3:
                    insights.append(
                        f"📊 **{selected_category}スキルと品質に中程度の負の相関** (R={r_value:.3f})\n"
                        f"→ 他の要因と組み合わせて改善を検討"
                    )
        except:
            pass
    
    # シフト差
    df_day_shift = df_process[df_process['シフト'] == '日勤']
    df_night_shift = df_process[df_process['シフト'] == '夜勤']
    
    if not df_day_shift.empty and not df_night_shift.empty:
        day_defect = df_day_shift['品質不良率 (%)'].mean()
        night_defect = df_night_shift['品質不良率 (%)'].mean()
        defect_diff = abs(day_defect - night_defect)
        
        if defect_diff > 0.5:
            better_shift = '日勤' if day_defect < night_defect else '夜勤'
            worse_shift = '夜勤' if day_defect < night_defect else '日勤'
            insights.append(
                f"⚠️ **シフト間で品質差が顕著** ({defect_diff:.2f}%差)\n"
                f"→ {worse_shift}シフトの作業環境・教育を重点改善"
            )
    
    # チーム間のバラツキ
    team_defects = df_process.groupby('チーム')['品質不良率 (%)'].mean()
    if len(team_defects) > 1:
        defect_std = team_defects.std()
        if defect_std > 0.5:
            best_team = team_defects.idxmin()
            worst_team = team_defects.idxmax()
            insights.append(
                f"📍 **チーム間でバラツキが大きい** (σ={defect_std:.2f})\n"
                f"→ {best_team}のベストプラクティスを{worst_team}に展開"
            )
    
    # 時系列トレンド
    if len(df_process) > 10:
        recent_defect = df_process.tail(10)['品質不良率 (%)'].mean()
        older_defect = df_process.head(10)['品質不良率 (%)'].mean()
        trend_diff = recent_defect - older_defect
        
        if trend_diff > 0.3:
            insights.append(
                f"📉 **品質が悪化傾向** (直近vs初期: +{trend_diff:.2f}%)\n"
                f"→ 緊急の原因調査と対策が必要"
            )
        elif trend_diff < -0.3:
            insights.append(
                f"📈 **品質が改善傾向** (直近vs初期: {trend_diff:.2f}%)\n"
                f"→ 現在の取り組みを継続・強化"
            )
    
    # インサイト表示
    if insights:
        for insight in insights:
            st.success(insight, icon="💡")
    else:
        st.info("現在のデータからは特筆すべき傾向は見られません。継続的にモニタリングしてください。", icon="ℹ️")
    
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