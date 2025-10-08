# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# --- 💡 解決策: ルートディレクトリをPythonの検索パスに追加 ---
# 現在のファイル (app.py) のディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
# ルートディレクトリをパスに追加
if current_dir not in sys.path:
    sys.path.append(current_dir)
# ------------------------------------------------------------------

# 外部ファイルのインポート
from data_loader import generate_dummy_data
from components.kpi_summary import show_kpi_summary
from components.step2_analysis import show_step2_analysis
from components.step3_kpi_linkage import show_step3_linkage
from components.step4_daily_trend import show_step4_daily_trend

# ... (以降のコードは変更なし) ...