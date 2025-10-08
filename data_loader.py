# data_loader.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

# ダミーデータの生成とロード関数を定義
@st.cache_data
def generate_dummy_data():
    # --- 定義 ---
    np.random.seed(42)
    num_data = 200
    locations = ['日本 (JP)', '拠点A (TH)', '拠点B (US)', '拠点C (MX)']
    teams = ['T1:成形', 'T2:加工', 'T3:組立', 'T4:検査']
    shifts = ['日勤', '夜勤']
    skills_info = {
        '成形技術': '成形工程の難易度設定能力',
        'NCプログラム': '加工工程のプログラム作成・修正能力',
        '品質検査': '製品の最終検査基準の遵守と判断能力',
        '設備保全': '日常的な設備点検と簡易修理能力',
        '安全管理': '危険予知・手順遵守能力'
    }
    skill_names = list(skills_info.keys())

    # --- スキルデータ生成 ---
    skill_data = {
        '拠点': np.random.choice(locations, num_data),
        '組織・チーム': np.random.choice(teams, num_data),
        'シフト': np.random.choice(shifts, num_data),
        '従業員ID': [f'EMP_{i+1:03d}' for i in range(num_data)],
        '評価日': [date.today() - timedelta(days=np.random.randint(1, 180)) for _ in range(num_data)]
    }
    df_temp = pd.DataFrame(skill_data)

    for skill_name in skill_names:
        scores = []
        for index, row in df_temp.iterrows():
            score = np.random.randint(2, 4)
            if skill_name == '成形技術' and row['組織・チーム'] == 'T1:成形': score += np.random.randint(1, 3)
            elif skill_name == 'NCプログラム' and row['組織・チーム'] in ['T1:成形', 'T2:加工']: score += np.random.randint(1, 2)
            if row['拠点'] == '日本 (JP)': score += 1
            elif row['拠点'] == '拠点A (TH)' and score > 2: score -= 1
            scores.append(np.clip(score + np.random.randint(-1, 2), 1, 5))
        skill_data[skill_name] = pd.Series(scores).astype(int)

    df_skill = pd.DataFrame(skill_data)
    
    # --- 日次生産実績データ生成 ---
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    production_records = []
    
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        for loc in locations:
            for shift in shifts:
                avg_skill_for_day = df_skill.loc[(df_skill['拠点'] == loc) & (df_skill['シフト'] == shift), skill_names].mean().mean()
                if pd.isna(avg_skill_for_day): avg_skill_for_day = 3.0

                efficiency = (75 + avg_skill_for_day * 4 + np.random.randn() * 3).clip(75, 98).round(1)
                defect_rate = (6 - avg_skill_for_day * 0.8 + np.random.randn() * 0.8).clip(0.5, 6).round(2)
                
                production_records.append({
                    '日付': single_date,
                    '拠点': loc,
                    'シフト': shift,
                    '日次生産量 (Unit)': np.random.randint(1000, 5000) * (1 + (avg_skill_for_day - 3.5) / 5),
                    '生産効率 (%)': efficiency,
                    '品質不良率 (%)': defect_rate,
                    '平均スキル予測値': avg_skill_for_day.round(2)
                })

    df_daily_prod = pd.DataFrame(production_records)
    
    # --- スキルデータにKPIを追加 ---
    df_skill['総合スキルスコア'] = df_skill[skill_names].mean(axis=1).round(2)
    df_skill['生産効率 (%)'] = (60 + df_skill['総合スキルスコア'] * 8 + np.random.randn(num_data) * 4).clip(75, 98).round(1)
    df_skill['品質不良率 (%)'] = (8 - df_skill['総合スキルスコア'] * 1.2 + np.random.randn(num_data) * 1).clip(0.5, 8).round(1)
    
    return df_skill, df_daily_prod, skills_info, skill_names