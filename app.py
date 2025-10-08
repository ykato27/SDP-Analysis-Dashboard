import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

# 外部ファイルからデータ生成関数のみをインポート
try:
    from data_loader import generate_dummy_data
except ModuleNotFoundError:
    st.error("エラー: data_loader.py が見つかりません。app.py と同じフォルダに配置してください。", icon="🔥")
    st.stop()


# --------------------------------------------------------------------------------
# エグゼクティブサマリー: 経営判断に必要な情報を凝縮
# --------------------------------------------------------------------------------

def show_executive_summary(df_skill, df_daily_prod):
    """経営層向けエグゼクティブサマリー"""
    
    st.markdown("## 📊 エグゼクティブサマリー")
    st.markdown("##### グローバル製造拠点の生産性格差とスキル起因の損失額")
    
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
        defect_loss = monthly_production_value * (defect_gap / 100) * 1.5  # 不良品の損失倍率
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
            'スキルギャップ': f"{skill_gap:.2f}",
            '効率ギャップ': f"{efficiency_gap:.1f}%",
            '不良率ギャップ': f"{defect_gap:.2f}%",
            '月間損失額': f"¥{total_loss:.1f}M",
            '年間損失額': f"¥{annual_loss:.0f}M",
            '教育投資額': f"¥{total_training_cost:.1f}M",
            'ROI': f"{roi:.1f}x",
            '投資回収期間': f"{payback_months:.1f}ヶ月"
        })
    
    df_summary = pd.DataFrame(location_summary)
    
    # 重要指標のハイライト
    col1, col2, col3, col4 = st.columns(4)
    
    total_annual_loss = df_summary['年間損失額'].apply(lambda x: float(x.replace('¥', '').replace('M', ''))).sum()
    total_training_cost = df_summary['教育投資額'].apply(lambda x: float(x.replace('¥', '').replace('M', ''))).sum()
    avg_roi = df_summary['ROI'].apply(lambda x: float(x.replace('x', ''))).mean()
    
    col1.metric("🔴 年間推定損失額", f"¥{total_annual_loss:.0f}M", help="ベンチマーク(日本)との生産性格差による")
    col2.metric("💰 必要教育投資", f"¥{total_training_cost:.0f}M", help="スキルギャップ解消のための投資額")
    col3.metric("📈 期待ROI", f"{avg_roi:.1f}x", help="教育投資に対するリターン")
    col4.metric("⏱️ 投資回収期間", f"{(total_training_cost / (total_annual_loss/12)):.1f}ヶ月", help="平均的な投資回収期間")
    
    st.markdown("---")
    st.markdown("### 🎯 拠点別 優先順位マトリクス")
    
    # 優先度スコアリング（損失額とROIの加重平均）
    df_summary['損失額_数値'] = df_summary['年間損失額'].apply(lambda x: float(x.replace('¥', '').replace('M', '')))
    df_summary['ROI_数値'] = df_summary['ROI'].apply(lambda x: float(x.replace('x', '')))
    df_summary['優先度スコア'] = (df_summary['損失額_数値'] / df_summary['損失額_数値'].max() * 0.6 + 
                                    df_summary['ROI_数値'] / df_summary['ROI_数値'].max() * 0.4) * 100
    
    df_summary_display = df_summary.drop(columns=['損失額_数値', 'ROI_数値'])
    df_summary_display['優先度'] = df_summary['優先度スコア'].apply(
        lambda x: '🔴 最優先' if x > 70 else ('🟡 優先' if x > 50 else '🟢 中期対応')
    )
    df_summary_display = df_summary_display.sort_values('優先度スコア', ascending=False)
    
    st.dataframe(
        df_summary_display[['優先度', '拠点', '従業員数', 'スキルギャップ', '年間損失額', '教育投資額', 'ROI', '投資回収期間']],
        use_container_width=True,
        hide_index=True
    )
    
    st.info(
        "💡 **経営判断のポイント**: 最優先拠点（🔴）から教育投資を実行することで、最短6ヶ月で投資回収が見込まれます。"
        "特に**拠点A (TH)**は損失額が大きく、ROIも高いため、即座のアクション推奨。",
        icon="💼"
    )
    
    return df_summary


# --------------------------------------------------------------------------------
# 根本原因分析: スキルギャップの詳細ドリルダウン
# --------------------------------------------------------------------------------

def show_root_cause_analysis(df_skill, target_location):
    """特定拠点の根本原因分析"""
    
    st.markdown(f"## 🔬 根本原因分析: {target_location}")
    st.markdown("##### スキルギャップの具体的な原因と、ボトルネックとなっている従業員・シフト・スキル項目を特定")
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    df_benchmark = df_skill[df_skill['拠点'] == '日本 (JP)'].copy()
    
    skill_names = ['成形技術', 'NCプログラム', '品質検査', '設備保全', '安全管理']
    
    # スキル別ギャップ分析
    st.markdown("### 📉 スキルカテゴリ別ギャップ分析")
    
    skill_gap_data = []
    for skill in skill_names:
        target_mean = df_target[skill].mean()
        benchmark_mean = df_benchmark[skill].mean()
        gap = benchmark_mean - target_mean
        impact_weight = {
            '成形技術': 1.5,  # 生産効率への影響度（重み）
            'NCプログラム': 1.3,
            '品質検査': 1.4,
            '設備保全': 1.2,
            '安全管理': 1.0
        }
        weighted_gap = gap * impact_weight.get(skill, 1.0)
        
        skill_gap_data.append({
            'スキル': skill,
            '当拠点平均': f"{target_mean:.2f}",
            'ベンチマーク': f"{benchmark_mean:.2f}",
            'ギャップ': f"{gap:.2f}",
            '影響度加味': f"{weighted_gap:.2f}",
            '改善優先度': '🔴 最優先' if weighted_gap > 0.8 else ('🟡 優先' if weighted_gap > 0.5 else '🟢 中')
        })
    
    df_skill_gap = pd.DataFrame(skill_gap_data)
    st.dataframe(df_skill_gap, use_container_width=True, hide_index=True)
    
    # 最も課題のあるスキルを特定
    priority_skill = df_skill_gap.sort_values('影響度加味', ascending=False).iloc[0]['スキル']
    
    st.markdown(f"### 🎯 最優先改善スキル: **{priority_skill}**")
    
    # 該当スキルの習熟度分布比較
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
        st.plotly_chart(fig_target, use_container_width=True)
        
        low_skill_count = df_target[df_target[priority_skill] <= 2].shape[0]
        st.error(f"⚠️ レベル2以下: **{low_skill_count}名** ({low_skill_count/len(df_target)*100:.1f}%)", icon="🚨")
    
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
        st.plotly_chart(fig_bench, use_container_width=True)
        
        bench_low = df_benchmark[df_benchmark[priority_skill] <= 2].shape[0]
        st.success(f"✅ レベル2以下: **{bench_low}名** ({bench_low/len(df_benchmark)*100:.1f}%)", icon="✨")
    
    # シフト別・チーム別のボトルネック特定
    st.markdown("### 🔍 ボトルネック特定: シフト×チーム×スキル")
    
    bottleneck_analysis = df_target.groupby(['シフト', '組織・チーム']).agg({
        priority_skill: ['mean', 'std', 'count'],
        '生産効率 (%)': 'mean',
        '品質不良率 (%)': 'mean'
    }).reset_index()
    
    bottleneck_analysis.columns = ['シフト', 'チーム', 'スキル平均', 'スキルバラツキ', '人数', '生産効率', '不良率']
    bottleneck_analysis['リスクスコア'] = (
        (5 - bottleneck_analysis['スキル平均']) * 0.4 + 
        bottleneck_analysis['スキルバラツキ'] * 0.3 +
        bottleneck_analysis['不良率'] * 0.3
    )
    bottleneck_analysis = bottleneck_analysis.sort_values('リスクスコア', ascending=False)
    bottleneck_analysis['対策優先度'] = bottleneck_analysis['リスクスコア'].apply(
        lambda x: '🔴 即時対応' if x > bottleneck_analysis['リスクスコア'].quantile(0.7) else '🟡 計画対応'
    )
    
    st.dataframe(
        bottleneck_analysis[['対策優先度', 'シフト', 'チーム', 'スキル平均', 'スキルバラツキ', '人数', '生産効率', '不良率']],
        use_container_width=True,
        hide_index=True
    )
    
    # 最優先対応チーム
    top_bottleneck = bottleneck_analysis.iloc[0]
    st.error(
        f"🚨 **即時対応が必要**: {top_bottleneck['シフト']} - {top_bottleneck['チーム']} "
        f"(スキル平均: {top_bottleneck['スキル平均']:.2f}, 人数: {int(top_bottleneck['人数'])}名)",
        icon="⚠️"
    )
    
    return priority_skill, top_bottleneck


# --------------------------------------------------------------------------------
# アクションプラン: 具体的な施策と実行計画
# --------------------------------------------------------------------------------

def show_action_plan(df_skill, target_location, priority_skill, bottleneck_team):
    """具体的なアクションプランの提示"""
    
    st.markdown("## 📋 アクションプラン: 実行可能な施策")
    st.markdown(f"##### {target_location} における {priority_skill} スキル改善の具体的施策")
    
    df_target = df_skill[df_skill['拠点'] == target_location].copy()
    
    # 施策オプションの提示
    st.markdown("### 💡 推奨施策パッケージ（優先順位順）")
    
    action_plans = [
        {
            '施策': '🎯 即効施策: 日本からの技術者短期派遣',
            '対象': f"{bottleneck_team['シフト']} - {bottleneck_team['チーム']} (最優先ボトルネック)",
            '期間': '2週間 x 2回',
            'コスト': '¥3.0M (渡航費・人件費込)',
            '効果': 'スキル +0.8pt, 効率 +5%pt',
            '実施時期': '即時 (来月から)',
            'KPI': '3ヶ月後に生産効率85%達成'
        },
        {
            '施策': '📚 中期施策: オンライン教育プログラム展開',
            '対象': f'{priority_skill}がレベル2以下の全従業員 (約{df_target[df_target[priority_skill] <= 2].shape[0]}名)',
            '期間': '3ヶ月間 (週2時間)',
            'コスト': '¥5.0M (プラットフォーム・コンテンツ制作)',
            '効果': 'スキル +1.2pt, 効率 +8%pt',
            '実施時期': '2ヶ月後開始',
            'KPI': '6ヶ月後にスキル平均3.5達成'
        },
        {
            '施策': '👥 構造施策: ベテラン-若手ペアリング制度',
            '対象': '全チーム',
            '期間': '継続的',
            'コスト': '¥1.0M (制度設計・インセンティブ)',
            '効果': 'スキルバラツキ -30%',
            '実施時期': '3ヶ月後',
            'KPI': '1年後にスキルバラツキ<0.5達成'
        },
        {
            '施策': '🔄 リスク対応: シフト間ローテーション',
            '対象': f'{bottleneck_team["シフト"]}の低スキル者',
            '期間': '3ヶ月トライアル',
            'コスト': '¥0.5M (管理コスト)',
            '効果': 'シフト間格差 -40%',
            '実施時期': '即時可能',
            'KPI': 'シフト間効率差<3%pt'
        }
    ]
    
    df_actions = pd.DataFrame(action_plans)
    st.dataframe(df_actions, use_container_width=True, hide_index=True)
    
    # 投資対効果シミュレーション
    st.markdown("### 📊 投資対効果シミュレーション")
    
    total_cost = 3.0 + 5.0 + 1.0 + 0.5  # 百万円
    expected_efficiency_gain = 5 + 8  # %pt
    monthly_production = 1000  # 百万円
    monthly_benefit = monthly_production * (expected_efficiency_gain / 100)
    payback = total_cost / monthly_benefit
    
    col1, col2, col3 = st.columns(3)
    col1.metric("総投資額", f"¥{total_cost:.1f}M")
    col2.metric("月間効果額", f"¥{monthly_benefit:.1f}M")
    col3.metric("投資回収期間", f"{payback:.1f}ヶ月")
    
    # タイムライン
    st.markdown("### 📅 実行タイムライン（今後12ヶ月）")
    
    timeline_data = {
        '月': list(range(1, 13)),
        '即効施策': [3 if i in [1, 3] else 0 for i in range(1, 13)],
        '中期施策': [0, 0] + [5/10]*10,
        '構造施策': [0, 0, 0] + [1/9]*9,
        'リスク対応': [0.5]*12,
        '累積効果': [monthly_benefit * min(i*0.3, 1) for i in range(1, 13)]
    }
    
    df_timeline = pd.DataFrame(timeline_data)
    
    fig_timeline = go.Figure()
    
    for col in ['即効施策', '中期施策', '構造施策', 'リスク対応']:
        fig_timeline.add_trace(go.Bar(
            x=df_timeline['月'],
            y=df_timeline[col],
            name=col,
        ))
    
    fig_timeline.add_trace(go.Scatter(
        x=df_timeline['月'],
        y=df_timeline['累積効果'],
        name='累積効果',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red', width=3)
    ))
    
    fig_timeline.update_layout(
        title='施策実行タイムラインと累積効果',
        xaxis=dict(title='月'),
        yaxis=dict(title='投資額 (百万円)'),
        yaxis2=dict(title='累積効果 (百万円/月)', overlaying='y', side='right'),
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.success(
        "✅ **実行承認の判断材料**: 全施策を実行した場合、約3.5ヶ月で投資回収が完了し、"
        "年間で約¥100M以上の利益改善が見込まれます。即時実行を推奨。",
        icon="💼"
    )


# --------------------------------------------------------------------------------
# モニタリングダッシュボード: 施策実行後の追跡
# --------------------------------------------------------------------------------

def show_monitoring_dashboard(df_daily_prod, target_location):
    """施策実行後のモニタリング"""
    
    st.markdown("## 📈 継続モニタリングダッシュボード")
    st.markdown("##### 施策実行後のKPI追跡と早期警告システム")
    
    df_target_daily = df_daily_prod[df_daily_prod['拠点'] == target_location].copy()
    df_target_daily = df_target_daily.groupby('日付').mean(numeric_only=True).reset_index()
    
    # KPIトレンド
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('生産効率トレンド', 'スキルスコアトレンド', '品質不良率トレンド', '総合健全性スコア'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 目標ライン
    target_efficiency = 85  # 目標生産効率
    target_skill = 3.5  # 目標スキル
    target_defect = 3.0  # 目標不良率
    
    # 生産効率
    fig.add_trace(
        go.Scatter(x=df_target_daily['日付'], y=df_target_daily['生産効率 (%)'], 
                   name='実績', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_hline(y=target_efficiency, line_dash="dash", line_color="green", 
                  annotation_text="目標", row=1, col=1)
    
    # スキルスコア
    fig.add_trace(
        go.Scatter(x=df_target_daily['日付'], y=df_target_daily['平均スキル予測値'], 
                   name='スキル', line=dict(color='orange')),
        row=1, col=2
    )
    fig.add_hline(y=target_skill, line_dash="dash", line_color="green", 
                  annotation_text="目標", row=1, col=2)
    
    # 不良率
    fig.add_trace(
        go.Scatter(x=df_target_daily['日付'], y=df_target_daily['品質不良率 (%)'], 
                   name='不良率', line=dict(color='red')),
        row=2, col=1
    )
    fig.add_hline(y=target_defect, line_dash="dash", line_color="green", 
                  annotation_text="目標", row=2, col=1)
    
    # 総合健全性スコア（0-100）
    df_target_daily['健全性'] = (
        (df_target_daily['生産効率 (%)'] / target_efficiency * 40) +
        (df_target_daily['平均スキル予測値'] / target_skill * 30) +
        ((10 - df_target_daily['品質不良率 (%)']) / 7 * 30)
    ).clip(0, 100)
    
    fig.add_trace(
        go.Scatter(x=df_target_daily['日付'], y=df_target_daily['健全性'], 
                   name='健全性', fill='tozeroy', line=dict(color='purple')),
        row=2, col=2
    )
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                  annotation_text="健全", row=2, col=2)
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # アラート
    latest_health = df_target_daily['健全性'].iloc[-1]
    
    if latest_health < 70:
        st.error(f"🚨 **緊急アラート**: 健全性スコアが{latest_health:.1f}に低下。即座の介入が必要です。", icon="⚠️")
    elif latest_health < 80:
        st.warning(f"⚠️ **注意**: 健全性スコアが{latest_health:.1f}。モニタリング強化が必要です。", icon="👀")
    else:
        st.success(f"✅ **良好**: 健全性スコア{latest_health:.1f}。目標達成に向けて順調です。", icon="🎯")


# --------------------------------------------------------------------------------
# メインアプリケーション
# --------------------------------------------------------------------------------

def main():
    st.set_page_config(layout="wide", page_title="SDP経営ダッシュボード", page_icon="💼")
    
    # データ生成
    df_skill, df_daily_prod, skills_info, skill_names = generate_dummy_data()
    
    # ヘッダー
    st.title('💼 SDP経営ダッシュボード - Global Manufacturing Excellence')
    st.markdown("##### データ駆動型の拠点間スキル格差解消と生産性向上のための意思決定支援システム")
    st.markdown("---")
    
    # サイドバー: 分析対象選択
    st.sidebar.header('🎯 分析対象拠点')
    st.sidebar.markdown("**エグゼクティブサマリー以外のセクション**で詳細分析する拠点を選択してください。")
    
    overseas_locations = [loc for loc in df_skill['拠点'].unique() if loc != '日本 (JP)']
    target_location = st.sidebar.selectbox(
        '詳細分析対象拠点',
        options=overseas_locations,
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 このダッシュボードは事業統括部長が**即座に意思決定**できるよう設計されています。", icon="💼")
    
    # タブ構成
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 エグゼクティブサマリー",
        "🔬 根本原因分析", 
        "📋 アクションプラン",
        "📈 モニタリング",
        "📁 生データ"
    ])
    
    with tab1:
        df_summary = show_executive_summary(df_skill, df_daily_prod)
    
    with tab2:
        priority_skill, bottleneck_team = show_root_cause_analysis(df_skill, target_location)
    
    with tab3:
        show_action_plan(df_skill, target_location, priority_skill, bottleneck_team)
    
    with tab4:
        show_monitoring_dashboard(df_daily_prod, target_location)
    
    with tab5:
        st.markdown("## 📁 生データ閲覧")
        st.markdown("##### 詳細分析用の元データ")
        
        data_type = st.radio("表示データ", ["従業員スキルデータ", "日次生産データ"], horizontal=True)
        
        if data_type == "従業員スキルデータ":
            st.dataframe(df_skill, use_container_width=True, height=600)
            st.download_button(
                "📥 CSVダウンロード",
                df_skill.to_csv(index=False).encode('utf-8-sig'),
                "skill_data.csv",
                "text/csv"
            )
        else:
            st.dataframe(df_daily_prod, use_container_width=True, height=600)
            st.download_button(
                "📥 CSVダウンロード",
                df_daily_prod.to_csv(index=False).encode('utf-8-sig'),
                "daily_production_data.csv",
                "text/csv"
            )
    
    # フッター
    st.markdown("---")
    st.caption("© SDP Executive Dashboard | Designed for Strategic Decision Making")


if __name__ == "__main__":
    main()