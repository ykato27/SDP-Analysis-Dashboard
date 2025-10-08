# components/step4_daily_trend.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_step4_daily_trend(df_daily_prod, selected_location, selected_shift):
    """Step 4: 日次生産データとの傾向分析を表示する。（ValueError対策済み）"""
    st.header('Step 4: 日次生産データとの傾向分析')
    st.markdown("直近の日次生産データと、それに影響を与えたと推測される**平均スキルレベルの変動**を比較分析します。")

    df_daily_filtered = df_daily_prod[
        df_daily_prod['拠点'].isin(selected_location) & 
        df_daily_prod['シフト'].isin(selected_shift)
    ].copy()

    col_daily_filter, _ = st.columns([1, 3])
    with col_daily_filter:
        selected_analysis_locations = st.multiselect('分析対象の拠点 (日次)', options=df_daily_filtered['拠点'].unique().tolist(), default=df_daily_filtered['拠点'].unique().tolist())
        selected_analysis_shifts = st.multiselect('分析対象のシフト (日次)', options=df_daily_filtered['シフト'].unique().tolist(), default=df_daily_filtered['シフト'].unique().tolist())

    df_analysis = df_daily_filtered[
        df_daily_filtered['拠点'].isin(selected_analysis_locations) & 
        df_daily_filtered['シフト'].isin(selected_analysis_shifts)
    ].groupby('日付').mean(numeric_only=True).reset_index()

    if df_analysis.empty:
        st.warning("日次分析対象のデータが存在しません。", icon="⚠️")
    else:
        
        # 2軸グラフの作成 (生産効率 vs 平均スキル予測値)
        # PlotlyのLayoutを辞書として定義し、ValueErrorを回避
        layout_config = {
            'title': '日次 生産効率と平均スキル予測値の推移 (過去30日間)',
            'xaxis': dict(title='日付'),
            'yaxis': dict(
                title='生産効率 (%)',
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4'),
                range=[df_analysis['生産効率 (%)'].min() * 0.98, df_analysis['生産効率 (%)'].max() * 1.02]
            ),
            'yaxis2': dict(
                title='平均スキル予測値 (5点満点)',
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e'),
                overlaying='y', 
                side='right',
                range=[2.5, 4.5] 
            ),
            'legend': dict(x=0.1, y=1.1, orientation="h")
        }
        
        # 辞書とgo.Layout()を使ってFigureを初期化
        fig_time_series = go.Figure(layout=go.Layout(**layout_config))
        
        # 1. 生産効率 (左軸)
        fig_time_series.add_trace(go.Scatter(
            x=df_analysis['日付'], 
            y=df_analysis['生産効率 (%)'], 
            name='平均生産効率 (%)',
            yaxis='y', # プライマリ軸は 'y' または 'y1' を参照
            mode='lines+markers',
            marker=dict(color='#1f77b4')
        ))

        # 2. 平均スキル予測値 (右軸)
        fig_time_series.add_trace(go.Scatter(
            x=df_analysis['日付'], 
            y=df_analysis['平均スキル予測値'], 
            name='平均スキル予測値',
            yaxis='y2',
            mode='lines+markers',
            marker=dict(color='#ff7f0e')
        ))

        st.plotly_chart(fig_time_series, use_container_width=True)
        
        st.info(
            "**分析の洞察**: 生産効率の低下と**平均スキル予測値の低下**が同期している場合、その期間のシフトメンバーのスキルが不足していた可能性が高いです。特に、**夜勤で生産効率が急落している場合**、夜勤メンバーのスキルレベルや、夜間特有の設備トラブルへの対応スキルが課題である可能性があります。", icon="📈"
        )
    
    st.markdown("---")
    st.success(
        "**次なるアクション**: 日次データから特定された**スキルが低い特定日**のメンバー構成（従業員ID）をドリルダウンし、そのメンバーに集中的なフォローアップ教育を実施します。",
        icon="🚀"
    )