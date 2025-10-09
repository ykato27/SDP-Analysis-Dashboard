import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_quality_skill_analysis(df_daily_prod, df_skill, target_location, skill_categories, skill_hierarchy, processes):
    """品質×力量の時系列分析"""
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">📈 品質×力量 時系列分析: {target_location}</div>
        <div class="header-subtitle">工程別・チーム別の歩留まりとスキルカテゴリ平均の時系列推移</div>
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
    
    # 基本統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_yield = df_filtered['歩留まり (%)'].mean()
        st.metric("平均歩留まり", f"{avg_yield:.1f}%")
    
    with col2:
        avg_defect = df_filtered['品質不良率 (%)'].mean()
        st.metric("平均不良率", f"{avg_defect:.2f}%")
    
    with col3:
        total_production = df_filtered['日次生産量 (t)'].sum()
        st.metric("累計生産量", f"{total_production:,.0f}t")
    
    with col4:
        data_days = df_filtered['日付'].nunique()
        st.metric("データ期間", f"{data_days}日間")
    
    st.markdown("---")
    
    # 分析設定
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🔍 分析設定</h2>
        <p class="section-subtitle">工程とスキルカテゴリを選択して時系列推移を確認</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_setting1, col_setting2 = st.columns(2)
    
    with col_setting1:
        selected_process = st.selectbox(
            '分析対象の工程',
            options=processes,
            index=0
        )
    
    with col_setting2:
        selected_category = st.selectbox(
            '分析対象のスキルカテゴリ',
            options=skill_categories,
            index=0
        )
    
    # 選択した工程のデータ
    df_process = df_filtered[df_filtered['工程'] == selected_process].copy()
    
    if df_process.empty:
        st.warning(f"{selected_process}のデータが存在しません。", icon="⚠️")
        return
    
    # 日付でソート
    df_process = df_process.sort_values('日付')
    
    st.markdown("---")
    
    # 時系列グラフ: 歩留まりとスキルカテゴリ平均
    st.markdown(f"### 📊 時系列推移: {selected_process} - {selected_category}")
    
    # チーム別の時系列グラフ
    teams = df_process['チーム'].unique()
    
    fig = make_subplots(
        rows=len(teams), cols=1,
        subplot_titles=[f'{team} の推移' for team in sorted(teams)],
        specs=[[{"secondary_y": True}] for _ in teams],
        vertical_spacing=0.08
    )
    
    colors_yield = {'Aチーム': '#1f77b4', 'Bチーム': '#ff7f0e', 'Cチーム': '#2ca02c'}
    colors_skill = {'Aチーム': '#9467bd', 'Bチーム': '#8c564b', 'Cチーム': '#e377c2'}
    
    for i, team in enumerate(sorted(teams), 1):
        df_team = df_process[df_process['チーム'] == team].copy()
        
        # 歩留まり
        fig.add_trace(
            go.Scatter(
                x=df_team['日付'],
                y=df_team['歩留まり (%)'],
                name=f'{team} 歩留まり',
                line=dict(color=colors_yield.get(team, '#1f77b4'), width=2),
                mode='lines+markers',
                legendgroup=team,
                showlegend=(i == 1)
            ),
            row=i, col=1,
            secondary_y=False
        )
        
        # スキルカテゴリ平均
        skill_col = f'{selected_category}_平均'
        if skill_col in df_team.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_team['日付'],
                    y=df_team[skill_col],
                    name=f'{team} {selected_category}',
                    line=dict(color=colors_skill.get(team, '#9467bd'), width=2, dash='dash'),
                    mode='lines+markers',
                    legendgroup=team,
                    showlegend=(i == 1)
                ),
                row=i, col=1,
                secondary_y=True
            )
        
        # シフト情報を背景色で表示
        for idx, row in df_team.iterrows():
            if row['シフト'] == '夜勤':
                fig.add_vrect(
                    x0=row['日付'], x1=row['日付'] + pd.Timedelta(days=1),
                    fillcolor="LightGray", opacity=0.2,
                    layer="below", line_width=0,
                    row=i, col=1
                )
        
        # Y軸設定
        fig.update_yaxes(title_text="歩留まり (%)", range=[90, 100], row=i, col=1, secondary_y=False)
        fig.update_yaxes(title_text=f"{selected_category} (スコア)", range=[1, 5], row=i, col=1, secondary_y=True)
    
    fig.update_xaxes(title_text="日付")
    
    fig.update_layout(
        height=300 * len(teams),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title_text=f"{selected_process} - チーム別 歩留まり×{selected_category}スキル 推移<br><sub>背景グレー: 夜勤シフト</sub>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 相関分析
    st.markdown(f"### 🔬 相関分析: 歩留まり vs {selected_category}スキル")
    
    col_corr1, col_corr2 = st.columns(2)
    
    with col_corr1:
        # 散布図
        skill_col = f'{selected_category}_平均'
        
        if skill_col in df_process.columns:
            fig_scatter = go.Figure()
            
            for team in sorted(teams):
                df_team = df_process[df_process['チーム'] == team]
                
                # 日付をフォーマット（datetime型に変換済みであることを確認）
                if pd.api.types.is_datetime64_any_dtype(df_team['日付']):
                    date_text = df_team['日付'].dt.strftime('%Y-%m-%d')
                else:
                    date_text = df_team['日付'].astype(str)
                
                fig_scatter.add_trace(go.Scatter(
                    x=df_team[skill_col],
                    y=df_team['歩留まり (%)'],
                    mode='markers',
                    name=team,
                    marker=dict(size=8, color=colors_yield.get(team, '#1f77b4')),
                    text=date_text,
                    hovertemplate='<b>%{text}</b><br>スキル: %{x:.2f}<br>歩留まり: %{y:.1f}%<extra></extra>'
                ))
            
            # トレンドライン
            try:
                from scipy import stats
                x_data = df_process[skill_col].dropna()
                y_data = df_process.loc[x_data.index, '歩留まり (%)']
                
                if len(x_data) > 2:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                    line_x = [x_data.min(), x_data.max()]
                    line_y = [slope * x + intercept for x in line_x]
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=line_x,
                        y=line_y,
                        mode='lines',
                        name=f'トレンド (R²={r_value**2:.3f})',
                        line=dict(color='red', dash='dash', width=2)
                    ))
            except ImportError:
                st.warning("scipyがインストールされていないため、トレンドラインを表示できません。", icon="⚠️")
            
            fig_scatter.update_layout(
                title=f'歩留まり vs {selected_category}スキル',
                xaxis_title=f'{selected_category}スキル 平均',
                yaxis_title='歩留まり (%)',
                height=400
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_corr2:
        # 相関係数マトリックス
        st.markdown("#### 相関係数")
        
        corr_data = []
        for cat in skill_categories:
            skill_col = f'{cat}_平均'
            if skill_col in df_process.columns:
                corr = df_process[[skill_col, '歩留まり (%)']].corr().iloc[0, 1]
                corr_data.append({
                    'スキルカテゴリ': cat,
                    '歩留まりとの相関': f"{corr:.3f}",
                    '相関強度': '強' if abs(corr) > 0.7 else ('中' if abs(corr) > 0.4 else '弱')
                })
        
        df_corr = pd.DataFrame(corr_data)
        st.dataframe(df_corr, use_container_width=True, hide_index=True)
        
        # インサイト
        if skill_col in df_process.columns:
            corr = df_process[[skill_col, '歩留まり (%)']].corr().iloc[0, 1]
            
            if corr > 0.5:
                st.success(
                    f"✅ **正の相関**: {selected_category}スキルが高いほど歩留まりが向上\n\n"
                    f"相関係数: {corr:.3f}\n\n"
                    f"**推奨**: このスキルへの教育投資が効果的",
                    icon="📈"
                )
            elif corr < -0.3:
                st.warning(
                    f"⚠️ **負の相関**: {selected_category}スキルと歩留まりに負の関係\n\n"
                    f"相関係数: {corr:.3f}\n\n"
                    f"**要確認**: 他の要因を調査",
                    icon="🔍"
                )
            else:
                st.info(
                    f"💡 **弱い相関**: {selected_category}スキルと歩留まりの直接的な関係は弱い\n\n"
                    f"相関係数: {corr:.3f}\n\n"
                    f"**示唆**: 他のスキルカテゴリも確認",
                    icon="ℹ️"
                )
    
    st.markdown("---")
    
    # シフトパターン分析
    st.markdown("### 🔄 シフトパターン分析")
    
    col_shift1, col_shift2 = st.columns(2)
    
    with col_shift1:
        # シフト別の歩留まり比較
        shift_summary = df_process.groupby('シフト').agg({
            '歩留まり (%)': ['mean', 'std', 'count']
        }).round(2)
        
        shift_summary.columns = ['平均歩留まり', '標準偏差', 'データ数']
        shift_summary = shift_summary.reset_index()
        
        st.dataframe(shift_summary, use_container_width=True, hide_index=True)
    
    with col_shift2:
        # チーム別の歩留まり比較
        team_summary = df_process.groupby('チーム').agg({
            '歩留まり (%)': ['mean', 'std', 'count']
        }).round(2)
        
        team_summary.columns = ['平均歩留まり', '標準偏差', 'データ数']
        team_summary = team_summary.reset_index()
        
        st.dataframe(team_summary, use_container_width=True, hide_index=True)
    
    # 次のステップ
    st.markdown("---")
    
    col_next1, col_next2 = st.columns(2)
    
    with col_next1:
        if st.button("🔬 根本原因分析へ", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.rerun()
    
    with col_next2:
        if st.button("📋 アクションプラン作成", use_container_width=True):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.rerun()