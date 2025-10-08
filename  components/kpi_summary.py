# components/kpi_summary.py
import streamlit as st

def show_kpi_summary(df_filtered, df_skill):
    """メイン画面のKPIサマリーを表示する."""
    total_efficiency = df_filtered['生産効率 (%)'].mean()
    total_defect_rate = df_filtered['品質不良率 (%)'].mean()
    avg_skill_score = df_filtered['総合スキルスコア'].mean()
    
    st.markdown("---")
    st.subheader("📊 主要KPIサマリー (フィルタ適用済み)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("対象従業員数", f"{len(df_filtered)} 名")
    col2.metric("平均総合スキルスコア (5点満点)", f"{avg_skill_score:.2f}")
    
    eff_delta = total_efficiency - df_skill['生産効率 (%)'].mean()
    col3.metric("平均生産効率", f"{total_efficiency:.1f} %", delta=f"{eff_delta:.1f}")
    
    def_delta = total_defect_rate - df_skill['品質不良率 (%)'].mean()
    col4.metric("平均品質不良率", f"{total_defect_rate:.2f} %", delta=f"{def_delta:.2f}", delta_color="inverse")
    st.markdown("---")