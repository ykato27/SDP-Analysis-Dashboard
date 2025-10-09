# data_loader.py
# 鉄鋼業向けスキル・生産データ生成モジュール

import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_dummy_data():
    """
    鉄鋼業向けのダミーデータを生成
    
    Returns:
        tuple: (df_skill, df_daily_prod, skill_hierarchy, all_skills, 
                skill_to_category, skill_categories, processes)
    """
    # --- 定義 ---
    np.random.seed(42)
    num_data = 250
    locations = ['日本 (JP)', '拠点A (IN)', '拠点B (BR)', '拠点C (VN)']
    
    # 鉄鋼業の工程
    processes = ['製銑', '製鋼', '圧延', '表面処理', '出荷']
    
    shifts = ['日勤', '夜勤']
    
    # スキルカテゴリとスキルの階層構造
    skill_hierarchy = {
        '設備操作': {
            'description': '製造設備の操作・制御能力',
            'skills': [
                '高炉操作',
                '転炉操作',
                '圧延機操作',
                'めっき設備操作',
                '搬送設備操作'
            ]
        },
        '品質管理': {
            'description': '製品品質の検査・管理能力',
            'skills': [
                '成分分析',
                '寸法測定',
                '表面検査',
                '非破壊検査',
                '品質記録'
            ]
        },
        '設備保全': {
            'description': '設備の点検・保守・修理能力',
            'skills': [
                '日常点検',
                '予防保全',
                '故障対応',
                '設備診断',
                '部品交換'
            ]
        },
        '工程管理': {
            'description': '生産計画・進捗管理能力',
            'skills': [
                '生産計画',
                '工程監視',
                '在庫管理',
                'トラブル対応',
                '改善活動'
            ]
        },
        '安全環境': {
            'description': '安全管理・環境管理能力',
            'skills': [
                '危険予知',
                '作業手順遵守',
                '保護具使用',
                '環境測定',
                '異常時対応'
            ]
        }
    }
    
    # スキルカテゴリリスト
    skill_categories = list(skill_hierarchy.keys())
    
    # 全スキルのフラットリスト
    all_skills = []
    skill_to_category = {}
    for category, info in skill_hierarchy.items():
        for skill in info['skills']:
            all_skills.append(skill)
            skill_to_category[skill] = category

    # --- スキルデータ生成 ---
    skill_data = {
        '拠点': np.random.choice(locations, num_data),
        '工程': np.random.choice(processes, num_data),
        'シフト': np.random.choice(shifts, num_data),
        '従業員ID': [f'EMP_{i+1:03d}' for i in range(num_data)],
        '評価日': [date.today() - timedelta(days=np.random.randint(1, 180)) for _ in range(num_data)]
    }
    df_temp = pd.DataFrame(skill_data)

    # 各スキルのスコアを生成（工程と拠点によって差をつける）
    for skill in all_skills:
        scores = []
        category = skill_to_category[skill]
        
        for index, row in df_temp.iterrows():
            # 基本スコア
            base_score = np.random.randint(2, 4)
            
            # 日本拠点は全体的にスキルが高い
            if row['拠点'] == '日本 (JP)':
                base_score += 1
            
            # 海外拠点は若干低め
            elif row['拠点'] in ['拠点A (IN)', '拠点B (BR)']:
                if base_score > 2:
                    base_score -= np.random.choice([0, 1], p=[0.6, 0.4])
            
            # 工程ごとの得意スキル
            process = row['工程']
            
            # 製銑工程: 設備操作と安全環境が重要
            if process == '製銑':
                if category in ['設備操作', '安全環境']:
                    base_score += np.random.randint(0, 2)
                if skill in ['高炉操作', '危険予知']:
                    base_score += 1
            
            # 製鋼工程: 設備操作と品質管理が重要
            elif process == '製鋼':
                if category in ['設備操作', '品質管理']:
                    base_score += np.random.randint(0, 2)
                if skill in ['転炉操作', '成分分析']:
                    base_score += 1
            
            # 圧延工程: 設備操作と工程管理が重要
            elif process == '圧延':
                if category in ['設備操作', '工程管理']:
                    base_score += np.random.randint(0, 2)
                if skill in ['圧延機操作', '工程監視']:
                    base_score += 1
            
            # 表面処理工程: 品質管理と設備操作が重要
            elif process == '表面処理':
                if category in ['品質管理', '設備操作']:
                    base_score += np.random.randint(0, 2)
                if skill in ['めっき設備操作', '表面検査']:
                    base_score += 1
            
            # 出荷工程: 品質管理と工程管理が重要
            elif process == '出荷':
                if category in ['品質管理', '工程管理']:
                    base_score += np.random.randint(0, 2)
                if skill in ['品質記録', '在庫管理']:
                    base_score += 1
            
            # ランダムな変動を追加
            score = base_score + np.random.randint(-1, 2)
            scores.append(np.clip(score, 1, 5))
        
        skill_data[skill] = pd.Series(scores).astype(int)

    df_skill = pd.DataFrame(skill_data)
    
    # --- 日次生産実績データ生成 ---
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    production_records = []
    
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        for loc in locations:
            for process in processes:
                for shift in shifts:
                    # その工程・シフトの平均スキルを計算
                    avg_skill_for_day = df_skill.loc[
                        (df_skill['拠点'] == loc) & 
                        (df_skill['工程'] == process) & 
                        (df_skill['シフト'] == shift), 
                        all_skills
                    ].mean().mean()
                    
                    if pd.isna(avg_skill_for_day): 
                        avg_skill_for_day = 3.0

                    efficiency = (75 + avg_skill_for_day * 4 + np.random.randn() * 3).clip(75, 98).round(1)
                    defect_rate = (6 - avg_skill_for_day * 0.8 + np.random.randn() * 0.8).clip(0.5, 6).round(2)
                    
                    production_records.append({
                        '日付': single_date,
                        '拠点': loc,
                        '工程': process,
                        'シフト': shift,
                        '日次生産量 (t)': np.random.randint(500, 3000) * (1 + (avg_skill_for_day - 3.5) / 5),
                        '生産効率 (%)': efficiency,
                        '品質不良率 (%)': defect_rate,
                        '平均スキル予測値': avg_skill_for_day.round(2)
                    })

    df_daily_prod = pd.DataFrame(production_records)
    
    # --- スキルカテゴリ別の平均スコアを計算 ---
    for category in skill_categories:
        category_skills = skill_hierarchy[category]['skills']
        df_skill[f'{category}_平均'] = df_skill[category_skills].mean(axis=1).round(2)
    
    # --- 総合スキルスコアとKPIを追加 ---
    df_skill['総合スキルスコア'] = df_skill[all_skills].mean(axis=1).round(2)
    df_skill['生産効率 (%)'] = (60 + df_skill['総合スキルスコア'] * 8 + np.random.randn(num_data) * 4).clip(75, 98).round(1)
    df_skill['品質不良率 (%)'] = (8 - df_skill['総合スキルスコア'] * 1.2 + np.random.randn(num_data) * 1).clip(0.5, 8).round(1)
    
    return df_skill, df_daily_prod, skill_hierarchy, all_skills, skill_to_category, skill_categories, processes