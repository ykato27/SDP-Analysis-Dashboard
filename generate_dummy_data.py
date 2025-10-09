"""
ダミーデータ生成スクリプト
- 30日間のデータ
- 各チーム・各日で休む人が変わる → スキル平均値が変動
- スキル平均値が低い日 → 品質不良率が高い（負の相関 R≒-0.7）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ランダムシード固定（再現性のため）
np.random.seed(42)

# 設定
START_DATE = datetime(2025, 1, 1)
NUM_DAYS = 30
TEAMS = ['Aチーム', 'Bチーム', 'Cチーム']
PROCESSES = ['加工', '組立', '検査']

# データリスト
data = []

# 日付ループ
for day_offset in range(NUM_DAYS):
    current_date = START_DATE + timedelta(days=day_offset)
    
    # その日のシフト割り当て（3チームを日勤・夜勤・休みにローテーション）
    team_rotation_index = day_offset % 3
    
    if team_rotation_index == 0:
        day_team = 'Aチーム'
        night_team = 'Bチーム'
        rest_team = 'Cチーム'
    elif team_rotation_index == 1:
        day_team = 'Bチーム'
        night_team = 'Cチーム'
        rest_team = 'Aチーム'
    else:
        day_team = 'Cチーム'
        night_team = 'Aチーム'
        rest_team = 'Bチーム'
    
    # 工程ごとにデータ生成
    for process in PROCESSES:
        # 日勤のデータ
        # スキル平均値：2.5～4.5の範囲でランダムに変動（休む人が変わる想定）
        day_skill_mean = np.random.uniform(2.5, 4.5)
        
        # 品質不良率：スキルと負の相関（R≒-0.7）
        # スキルが高い → 不良率低い、スキルが低い → 不良率高い
        # 基準不良率 = 5.0 - (スキル平均 * 1.2) + ノイズ
        day_defect_base = 5.0 - (day_skill_mean * 1.2)
        day_defect_noise = np.random.normal(0, 0.3)  # ノイズ追加
        day_defect_rate = max(0.1, day_defect_base + day_defect_noise)  # 最低0.1%
        
        # 生産数量
        day_production = np.random.randint(800, 1200)
        
        # 歩留まり = 100 - 不良率
        day_yield = 100 - day_defect_rate
        
        data.append({
            '日付': current_date,
            '拠点': '東京工場',
            '工程': process,
            'シフト': '日勤',
            'チーム': day_team,
            '生産数量': day_production,
            '歩留まり (%)': round(day_yield, 2),
            '品質不良率 (%)': round(day_defect_rate, 2),
            '平均スキル予測値': round(day_skill_mean, 2),
            f'技術力_平均': round(day_skill_mean + np.random.uniform(-0.2, 0.2), 2),
            f'安全意識_平均': round(day_skill_mean + np.random.uniform(-0.3, 0.3), 2),
            f'品質意識_平均': round(day_skill_mean + np.random.uniform(-0.2, 0.2), 2),
            f'チームワーク_平均': round(day_skill_mean + np.random.uniform(-0.3, 0.3), 2),
            f'改善提案力_平均': round(day_skill_mean + np.random.uniform(-0.4, 0.4), 2),
        })
        
        # 夜勤のデータ
        # 夜勤は日勤よりもやや低めのスキル平均値（夜勤効果）
        night_skill_mean = np.random.uniform(2.3, 4.3)
        
        # 品質不良率：スキルと負の相関 + 夜勤効果でやや高め
        night_defect_base = 5.5 - (night_skill_mean * 1.2)  # 夜勤は基準値が少し高い
        night_defect_noise = np.random.normal(0, 0.3)
        night_defect_rate = max(0.1, night_defect_base + night_defect_noise)
        
        night_production = np.random.randint(700, 1100)
        night_yield = 100 - night_defect_rate
        
        data.append({
            '日付': current_date,
            '拠点': '東京工場',
            '工程': process,
            'シフト': '夜勤',
            'チーム': night_team,
            '生産数量': night_production,
            '歩留まり (%)': round(night_yield, 2),
            '品質不良率 (%)': round(night_defect_rate, 2),
            '平均スキル予測値': round(night_skill_mean, 2),
            f'技術力_平均': round(night_skill_mean + np.random.uniform(-0.2, 0.2), 2),
            f'安全意識_平均': round(night_skill_mean + np.random.uniform(-0.3, 0.3), 2),
            f'品質意識_平均': round(night_skill_mean + np.random.uniform(-0.2, 0.2), 2),
            f'チームワーク_平均': round(night_skill_mean + np.random.uniform(-0.3, 0.3), 2),
            f'改善提案力_平均': round(night_skill_mean + np.random.uniform(-0.4, 0.4), 2),
        })

# DataFrameに変換
df = pd.DataFrame(data)

# CSVとして保存
output_path = '/home/claude/SDP-Analysis-Dashboard/data/daily_production_dummy.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"✅ ダミーデータ生成完了: {output_path}")
print(f"📊 データ件数: {len(df)}行")
print(f"📅 期間: {df['日付'].min()} ～ {df['日付'].max()}")

# 相関係数を確認
print("\n【相関係数確認】")
for process in PROCESSES:
    df_process = df[df['工程'] == process]
    
    # 日勤
    df_day = df_process[df_process['シフト'] == '日勤']
    if len(df_day) > 2:
        corr_day = df_day['平均スキル予測値'].corr(df_day['品質不良率 (%)'])
        print(f"{process} - 日勤: R = {corr_day:.3f}")
    
    # 夜勤
    df_night = df_process[df_process['シフト'] == '夜勤']
    if len(df_night) > 2:
        corr_night = df_night['平均スキル予測値'].corr(df_night['品質不良率 (%)'])
        print(f"{process} - 夜勤: R = {corr_night:.3f}")

print("\n【サンプルデータ】")
print(df.head(10))