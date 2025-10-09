import streamlit as st

def apply_custom_styles():
    """Skillnote風のカスタムCSSを適用"""
    
    st.markdown("""
    <style>
        /* サイドバーのスタイリング */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
            color: #2e7d32;
            font-size: 1.5rem;
            font-weight: 600;
            padding: 0.5rem 0;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: #2e7d32;
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 1rem;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
            color: #666;
            font-size: 0.9rem;
            font-weight: 400;
            margin-top: 0;
        }
        
        /* サイドバーのボタンスタイリング */
        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            font-weight: 500;
            border: none;
            margin-bottom: 0.3rem;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] .stButton button[kind="primary"] {
            background-color: #2e7d32;
            color: white;
        }
        
        [data-testid="stSidebar"] .stButton button[kind="secondary"] {
            background-color: #f5f5f5;
            color: #333;
        }
        
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #1b5e20;
            color: white;
            transform: translateX(4px);
        }
        
        /* メインコンテンツエリア */
        .main {
            background-color: #fafafa;
            padding: 2rem;
        }
        
        /* ヘッダー部分 */
        .header-container {
            background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
            padding: 1.5rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
        }
        
        .header-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header-subtitle {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* セクションヘッダー */
        .section-header {
            background-color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border-left: 4px solid #2e7d32;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2e7d32;
            margin: 0;
        }
        
        .section-subtitle {
            font-size: 0.9rem;
            color: #666;
            margin: 0.3rem 0 0 0;
        }
        
        /* メトリクスカードのスタイリング */
        [data-testid="stMetric"] {
            background-color: white;
            padding: 1.2rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        
        [data-testid="stMetric"] label {
            font-size: 0.9rem !important;
            color: #666 !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        
        /* テーブルのスタイリング */
        .dataframe {
            border: none !important;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .dataframe thead tr th {
            background-color: #f5f5f5 !important;
            font-weight: 600 !important;
            padding: 12px !important;
            color: #333 !important;
            border-bottom: 2px solid #2e7d32 !important;
        }
        
        .dataframe tbody tr {
            transition: background-color 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background-color: #f9fbe7 !important;
        }
        
        .dataframe tbody tr td {
            padding: 10px !important;
        }
        
        /* タブのスタイリング */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: white;
            padding: 0.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 0 24px;
            font-weight: 500;
            color: #666;
            border: none;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #2e7d32 !important;
            color: white !important;
        }
        
        /* ボタンのスタイリング */
        .stButton button {
            background-color: #2e7d32;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            border: none;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            background-color: #1b5e20;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* ダウンロードボタン */
        .stDownloadButton button {
            background-color: #1976d2;
            color: white;
        }
        
        .stDownloadButton button:hover {
            background-color: #1565c0;
        }
        
        /* ウェルカムカード */
        .welcome-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            text-align: center;
            transition: all 0.3s ease;
            height: 100%;
            border: 1px solid #e0e0e0;
        }
        
        .welcome-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: #2e7d32;
        }
        
        .welcome-icon {
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }
        
        .welcome-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .welcome-desc {
            font-size: 0.95rem;
            color: #666;
            line-height: 1.6;
        }
        
        /* アラート・情報ボックス */
        .stAlert {
            border-radius: 10px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* エクスパンダー */
        .streamlit-expanderHeader {
            background-color: #f5f5f5;
            border-radius: 8px;
            font-weight: 500;
            padding: 0.75rem 1rem;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #e8f5e9;
        }
        
        /* セレクトボックス */
        .stSelectbox > div > div {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        /* プログレスバー */
        .stProgress > div > div {
            background-color: #2e7d32;
        }
        
        /* 成功メッセージ */
        .stSuccess {
            background-color: #e8f5e9;
            border-left: 4px solid #2e7d32;
        }
        
        /* エラーメッセージ */
        .stError {
            background-color: #ffebee;
            border-left: 4px solid #d32f2f;
        }
        
        /* 警告メッセージ */
        .stWarning {
            background-color: #fff3e0;
            border-left: 4px solid #f57c00;
        }
        
        /* 情報メッセージ */
        .stInfo {
            background-color: #e3f2fd;
            border-left: 4px solid #1976d2;
        }
        
        /* チャートのスタイリング */
        .js-plotly-plot {
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            background-color: white;
            padding: 1rem;
        }
        
        /* スクロールバーのカスタマイズ */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #2e7d32;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #1b5e20;
        }
    </style>
    """, unsafe_allow_html=True)