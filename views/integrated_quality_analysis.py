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
    # 1. 複合時系列グラフ（スキル・品質・シフトを1つのグラフで）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析① 複合時系列グラフ</h2>
        <p class="section-subtitle">スキルと品質の時系列推移を1つのグラフで可視化（シフト別色分け）</p>
    </div>
    """, unsafe_allow_html=True)
    
    # シフト別にデータを分ける
    df_day = df_process[df_process['シフト'] == '日勤'].copy()
    df_night = df_process[df_process['シフト'] == '夜勤'].copy()
    
    skill_col = f'{selected_category}_平均'
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 日勤 - スキルスコア
    if not df_day.empty and skill_col in df_day.columns:
        fig1.add_trace(
            go.Scatter(
                x=df_day['日付'],
                y=df_day[skill_col],
                name='日勤 スキル',
                line=dict(color='#2E86DE', width=3),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>日勤 スキル</b><br>日付: %{x}<br>スコア: %{y:.2f}<extra></extra>'
            ),
            secondary_y=False
        )
    
    # 夜勤 - スキルスコア
    if not df_night.empty and skill_col in df_night.columns:
        fig1.add_trace(
            go.Scatter(
                x=df_night['日付'],
                y=df_night[skill_col],
                name='夜勤 スキル',
                line=dict(color='#5F27CD', width=3, dash='dot'),
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>夜勤 スキル</b><br>日付: %{x}<br>スコア: %{y:.2f}<extra></extra>'
            ),
            secondary_y=False
        )
    
    # 日勤 - 品質不良率
    if not df_day.empty:
        fig1.add_trace(
            go.Scatter(
                x=df_day['日付'],
                y=df_day['品質不良率 (%)'],
                name='日勤 不良率',
                line=dict(color='#FF6348', width=2),
                mode='lines+markers',
                marker=dict(size=5, symbol='square'),
                hovertemplate='<b>日勤 不良率</b><br>日付: %{x}<br>不良率: %{y:.2f}%<extra></extra>'
            ),
            secondary_y=True
        )
    
    # 夜勤 - 品質不良率
    if not df_night.empty:
        fig1.add_trace(
            go.Scatter(
                x=df_night['日付'],
                y=df_night['品質不良率 (%)'],
                name='夜勤 不良率',
                line=dict(color='#EE5A6F', width=2, dash='dot'),
                mode='lines+markers',
                marker=dict(size=5, symbol='square'),
                hovertemplate='<b>夜勤 不良率</b><br>日付: %{x}<br>不良率: %{y:.2f}%<extra></extra>'
            ),
            secondary_y=True
        )
    
    fig1.update_xaxes(title_text="日付")
    fig1.update_yaxes(title_text=f"{selected_category}スキル スコア", secondary_y=False, range=[1, 5])
    fig1.update_yaxes(title_text="品質不良率 (%)", secondary_y=True)
    
    fig1.update_layout(
        title=f"{selected_process} - スキルと品質の関係（シフト別）",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # インサイト
    if not df_day.empty and not df_night.empty:
        day_defect_avg = df_day['品質不良率 (%)'].mean()
        night_defect_avg = df_night['品質不良率 (%)'].mean()
        day_skill_avg = df_day[skill_col].mean() if skill_col in df_day.columns else 0
        night_skill_avg = df_night[skill_col].mean() if skill_col in df_night.columns else 0
        
        col_insight1, col_insight2 = st.columns(2)
        
        with col_insight1:
            st.info(
                f"**📈 日勤の特徴**\n\n"
                f"• 平均スキル: {day_skill_avg:.2f}\n\n"
                f"• 平均不良率: {day_defect_avg:.2f}%\n\n"
                f"• データ数: {len(df_day)}件",
                icon="☀️"
            )
        
        with col_insight2:
            st.info(
                f"**🌙 夜勤の特徴**\n\n"
                f"• 平均スキル: {night_skill_avg:.2f}\n\n"
                f"• 平均不良率: {night_defect_avg:.2f}%\n\n"
                f"• データ数: {len(df_night)}件",
                icon="🌙"
            )
    
    st.markdown("---")
    
    # =============================================================================
    # 2. ヒートマップ + 時系列
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔥 分析② ヒートマップ + 時系列</h2>
        <p class="section-subtitle">チーム×時間のスキルレベルと品質不良率の関係を2次元で可視化</p>
    </div>
    """, unsafe_allow_html=True)
    
    # チーム×日付のピボットテーブル作成
    teams = sorted(df_process['チーム'].unique())
    
    # スキルのヒートマップ
    if skill_col in df_process.columns:
        pivot_skill = df_process.pivot_table(
            values=skill_col,
            index='チーム',
            columns='日付',
            aggfunc='mean'
        )
        
        # 品質不良率のバブル用データ
        pivot_defect = df_process.pivot_table(
            values='品質不良率 (%)',
            index='チーム',
            columns='日付',
            aggfunc='mean'
        )
        
        fig2 = go.Figure()
        
        # ヒートマップ（スキル）
        fig2.add_trace(go.Heatmap(
            z=pivot_skill.values,
            x=[d.strftime('%m/%d') for d in pivot_skill.columns],
            y=pivot_skill.index,
            colorscale='Blues',
            hovertemplate='チーム: %{y}<br>日付: %{x}<br>スキル: %{z:.2f}<extra></extra>',
            colorbar=dict(title="スキル<br>スコア", len=0.4, y=0.75)
        ))
        
        # 品質不良率のバブル（サイズで表現）
        for i, team in enumerate(pivot_defect.index):
            for j, date in enumerate(pivot_defect.columns):
                defect_val = pivot_defect.iloc[i, j]
                if not pd.isna(defect_val):
                    fig2.add_trace(go.Scatter(
                        x=[date.strftime('%m/%d')],
                        y=[team],
                        mode='markers',
                        marker=dict(
                            size=defect_val * 5,  # 不良率が高いほど大きい
                            color='red',
                            opacity=0.6,
                            line=dict(color='darkred', width=1)
                        ),
                        hovertemplate=f'チーム: {team}<br>日付: {date.strftime("%Y-%m-%d")}<br>不良率: {defect_val:.2f}%<extra></extra>',
                        showlegend=False
                    ))
        
        # 凡例用ダミートレース
        fig2.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='red', opacity=0.6),
            name='不良率 (大きさ=不良率)',
            showlegend=True
        ))
        
        fig2.update_layout(
            title=f"{selected_process} - チーム×日付 スキルマップ（バブル=不良率）",
            xaxis_title="日付",
            yaxis_title="チーム",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        st.success(
            "**💡 読み方**\n\n"
            "• **青色の濃さ**: スキルレベル（濃いほど高い）\n\n"
            "• **赤いバブル**: 品質不良率（大きいほど不良率が高い）\n\n"
            "• **パターン**: どのチーム・時期に問題があるかが一目瞭然",
            icon="📖"
        )
    
    st.markdown("---")
    
    # =============================================================================
    # 3. 相関散布図（時系列アニメーション）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🎬 分析③ 相関散布図（時系列アニメーション）</h2>
        <p class="section-subtitle">スキルと品質の関係が時間とともにどう変化するかをアニメーションで表現</p>
    </div>
    """, unsafe_allow_html=True)
    
    if skill_col in df_process.columns:
        # 週ごとにデータを集計
        df_process['週'] = df_process['日付'].dt.to_period('W').dt.start_time
        
        fig3 = go.Figure()
        
        # 各週のフレームを作成
        weeks = sorted(df_process['週'].unique())
        
        # すべてのデータポイント（静的）
        for shift in ['日勤', '夜勤']:
            df_shift = df_process[df_process['シフト'] == shift]
            
            fig3.add_trace(go.Scatter(
                x=df_shift[skill_col],
                y=df_shift['品質不良率 (%)'],
                mode='markers',
                marker=dict(
                    size=df_shift['日次生産量 (t)'] / 100,
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
                st.info(
                    f"**📊 相関分析結果**\n\n"
                    f"• 相関係数 (R): {r_value:.3f}\n\n"
                    f"• 決定係数 (R²): {r_value**2:.3f}\n\n"
                    f"• 傾き: {slope:.4f}\n\n"
                    f"• p値: {p_value:.4e}",
                    icon="📈"
                )
        except ImportError:
            st.warning("scipyがインストールされていないため、トレンドラインを表示できません。", icon="⚠️")
        
        fig3.update_layout(
            title=f"{selected_process} - スキル vs 品質不良率（バブルサイズ=生産量）",
            xaxis_title=f"{selected_category}スキル スコア",
            yaxis_title="品質不良率 (%)",
            height=600,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        st.success(
            "**💡 読み方**\n\n"
            "• **横軸**: スキルスコア（右ほど高スキル）\n\n"
            "• **縦軸**: 品質不良率（下ほど高品質）\n\n"
            "• **バブルサイズ**: 生産量（大きいほど多い）\n\n"
            "• **色**: シフト（青=日勤、紫=夜勤）\n\n"
            "• **理想**: 右下（高スキル・低不良率）",
            icon="🎯"
        )
    
    st.markdown("---")
    
    # =============================================================================
    # 4. ファセットグラフ（Small Multiples）
    # =============================================================================
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📊 分析④ ファセットグラフ（Small Multiples）</h2>
        <p class="section-subtitle">シフト間の差を同じ形式のグラフで並べて比較</p>
    </div>
    """, unsafe_allow_html=True)
    
    if skill_col in df_process.columns:
        # 2行1列のサブプロット（上段=日勤、下段=夜勤）
        fig4 = make_subplots(
            rows=2, cols=1,
            subplot_titles=['☀️ 日勤シフト - スキル×品質推移', '🌙 夜勤シフト - スキル×品質推移'],
            specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
            vertical_spacing=0.15
        )
        
        shifts = [('日勤', 1, '#2E86DE', '#FF6348'), ('夜勤', 2, '#5F27CD', '#EE5A6F')]
        
        for shift_name, row, skill_color, defect_color in shifts:
            df_shift = df_process[df_process['シフト'] == shift_name]
            
            if not df_shift.empty:
                # スキルスコア
                fig4.add_trace(
                    go.Scatter(
                        x=df_shift['日付'],
                        y=df_shift[skill_col],
                        name=f'{shift_name} スキル',
                        line=dict(color=skill_color, width=3),
                        mode='lines+markers',
                        marker=dict(size=8),
                        legendgroup=shift_name,
                        showlegend=True,
                        hovertemplate=f'<b>{shift_name} スキル</b><br>日付: %{{x}}<br>スコア: %{{y:.2f}}<extra></extra>'
                    ),
                    row=row, col=1,
                    secondary_y=False
                )
                
                # 品質不良率
                fig4.add_trace(
                    go.Scatter(
                        x=df_shift['日付'],
                        y=df_shift['品質不良率 (%)'],
                        name=f'{shift_name} 不良率',
                        line=dict(color=defect_color, width=2, dash='dash'),
                        mode='lines+markers',
                        marker=dict(size=6),
                        legendgroup=shift_name,
                        showlegend=True,
                        hovertemplate=f'<b>{shift_name} 不良率</b><br>日付: %{{x}}<br>不良率: %{{y:.2f}}%<extra></extra>'
                    ),
                    row=row, col=1,
                    secondary_y=True
                )
                
                # 平均線を追加
                skill_mean = df_shift[skill_col].mean()
                defect_mean = df_shift['品質不良率 (%)'].mean()
                
                fig4.add_hline(
                    y=skill_mean,
                    line=dict(color=skill_color, dash='dot', width=2),
                    row=row, col=1,
                    secondary_y=False,
                    annotation_text=f"平均: {skill_mean:.2f}",
                    annotation_position="right"
                )
                
                fig4.add_hline(
                    y=defect_mean,
                    line=dict(color=defect_color, dash='dot', width=2),
                    row=row, col=1,
                    secondary_y=True,
                    annotation_text=f"平均: {defect_mean:.2f}%",
                    annotation_position="left"
                )
        
        # 軸設定
        fig4.update_xaxes(title_text="日付", row=2, col=1)
        fig4.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=1, col=1, secondary_y=False)
        fig4.update_yaxes(title_text="不良率 (%)", row=1, col=1, secondary_y=True)
        fig4.update_yaxes(title_text=f"{selected_category}スキル", range=[1, 5], row=2, col=1, secondary_y=False)
        fig4.update_yaxes(title_text="不良率 (%)", row=2, col=1, secondary_y=True)
        
        fig4.update_layout(
            title=f"{selected_process} - シフト別比較（点線=平均値）",
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
        
        # シフト比較サマリー
        col_summary1, col_summary2 = st.columns(2)
        
        with col_summary1:
            df_day_shift = df_process[df_process['シフト'] == '日勤']
            if not df_day_shift.empty and skill_col in df_day_shift.columns:
                st.info(
                    f"**☀️ 日勤シフト 統計**\n\n"
                    f"• 平均スキル: {df_day_shift[skill_col].mean():.2f} (σ={df_day_shift[skill_col].std():.2f})\n\n"
                    f"• 平均不良率: {df_day_shift['品質不良率 (%)'].mean():.2f}% (σ={df_day_shift['品質不良率 (%)'].std():.2f})\n\n"
                    f"• データ数: {len(df_day_shift)}件",
                    icon="☀️"
                )
        
        with col_summary2:
            df_night_shift = df_process[df_process['シフト'] == '夜勤']
            if not df_night_shift.empty and skill_col in df_night_shift.columns:
                st.info(
                    f"**🌙 夜勤シフト 統計**\n\n"
                    f"• 平均スキル: {df_night_shift[skill_col].mean():.2f} (σ={df_night_shift[skill_col].std():.2f})\n\n"
                    f"• 平均不良率: {df_night_shift['品質不良率 (%)'].mean():.2f}% (σ={df_night_shift['品質不良率 (%)'].std():.2f})\n\n"
                    f"• データ数: {len(df_night_shift)}件",
                    icon="🌙"
                )
    
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