import streamlit as st

def show_welcome_screen():
    """初期表示のウェルカム画面"""
    
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; color: #333; font-weight: 600; margin-bottom: 0.5rem;">
            グローバル拠点のスキルギャップを
        </h1>
        <h1 style="font-size: 2.5rem; color: #333; font-weight: 600; margin-bottom: 1rem;">
            データで見える化・改善しましょう
        </h1>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 3rem;">
            SDP（スキル・データ・プラットフォーム）分析で、製造拠点の生産性を最大化
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">📊</div>
            <div class="welcome-title">エグゼクティブサマリー</div>
            <div class="welcome-desc">
                年間損失額、ROI、投資回収期間など、経営判断に必要な情報を一目で把握。
                拠点別の優先順位を自動算出します。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">🔬</div>
            <div class="welcome-title">根本原因分析</div>
            <div class="welcome-desc">
                スキルギャップの詳細を分析し、ボトルネックとなっているチーム・シフト・スキル項目を特定。
                データに基づいた課題抽出が可能です。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">📋</div>
            <div class="welcome-title">アクションプラン</div>
            <div class="welcome-desc">
                具体的な施策パッケージと投資対効果を提示。
                タイムラインとKPIで実行可能な改善計画を立案できます。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 使い方ガイド
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">📚 使い方ガイド</h2>
        <p class="section-subtitle">4ステップで始める、データドリブンなスキル管理</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        st.markdown("""
        **STEP 1**  
        📊 **エグゼクティブサマリー**  
        全体の損失額とROIを確認
        """)
    
    with col_b:
        st.markdown("""
        **STEP 2**  
        🔬 **根本原因分析**  
        課題拠点のギャップを詳細分析
        """)
    
    with col_c:
        st.markdown("""
        **STEP 3**  
        📋 **アクションプラン**  
        具体的な施策を選定・承認
        """)
    
    with col_d:
        st.markdown("""
        **STEP 4**  
        📈 **継続モニタリング**  
        施策実行後の効果を追跡
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # クイックスタートボタン
    col_start1, col_start2, col_start3 = st.columns([1, 1, 1])
    
    with col_start2:
        if st.button("🚀 分析を開始する", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📊 エグゼクティブサマリー"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 主要機能の紹介
    with st.expander("💡 主要機能の詳細"):
        st.markdown("""
        ### 📊 エグゼクティブサマリー
        - 年間推定損失額の算出（ベンチマーク拠点との比較）
        - 教育投資のROI・投資回収期間の自動計算
        - 拠点別優先順位マトリクス（最優先・優先・中期対応）
        
        ### 🔬 根本原因分析
        - スキルカテゴリ別ギャップ分析（影響度加味）
        - 習熟度分布の可視化（ベンチマークとの比較）
        - ボトルネックチーム・シフトの特定
        
        ### 📋 アクションプラン
        - 4つの施策パッケージ（即効・中期・構造・リスク対応）
        - コスト・期間・KPIの明示
        - 投資対効果シミュレーション
        
        ### 📈 継続モニタリング
        - KPIトレンド（生産効率・スキルスコア・品質）
        - 健全性スコア（0-100）の自動算出
        - 早期警告アラート機能
        
        ### 📁 生データ閲覧
        - 従業員スキルデータの参照
        - 日次生産データの参照
        - CSVダウンロード機能
        """)