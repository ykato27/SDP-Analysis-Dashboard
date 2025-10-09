# data_loader.py
# 鉄鋼業向けスキル・生産データ生成モジュール

import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_dummy_data():
    """
    鉄鋼業向けのダミーデータを生成
    新しい30日間のダミーデータ（daily_production_dummy.csv）を優先的に読み込み
    
    Returns:
        tuple: (df_skill, df_daily_prod, skill_hierarchy, all_skills, 
                skill_to_category, skill_categories, processes)
    """
    import os
    
    # 新しいダミーデータのパス
    new_dummy_path = os.path.join(os.path.dirname(__file__), 'data', 'daily_production_dummy.csv')
    
    # 新しいダミーデータが存在するか確認
    use_new_dummy = os.path.exists(new_dummy_path)
    
    if use_new_dummy:
        print(f"✅ 新しいダミーデータを読み込みます: {new_dummy_path}")
    else:
        print("⚠️ 従来のダミーデータ生成ロジックを使用します")
    
    # --- 定義 ---
    np.random.seed(42)
    num_data = 300  # 従業員数を増やす（各拠点×各工程で十分な人数を確保）
    locations = ['日本 (JP)', '拠点A (IN)', '拠点B (BR)', '拠点C (VN)']
    
    # 工程（新しいダミーデータに合わせて変更）
    if use_new_dummy:
        processes = ['加工', '組立', '検査']
    else:
        processes = ['製銑', '製鋼', '圧延', '表面処理', '出荷']
    
    # チーム（3チーム制でローテーション）
    teams = ['Aチーム', 'Bチーム', 'Cチーム']
    
    shifts = ['日勤', '夜勤']
    
    # スキルカテゴリとスキルの階層構造
    if use_new_dummy:
        # 新しいダミーデータ用のスキル階層
        skill_hierarchy = {
            '技術力': {
                'description': '技術的な能力',
                'skills': ['技術力_A', '技術力_B', '技術力_C']
            },
            '安全意識': {
                'description': '安全に対する意識',
                'skills': ['安全意識_A', '安全意識_B', '安全意識_C']
            },
            '品質意識': {
                'description': '品質に対する意識',
                'skills': ['品質意識_A', '品質意識_B', '品質意識_C']
            },
            'チームワーク': {
                'description': 'チームで働く能力',
                'skills': ['チームワーク_A', 'チームワーク_B', 'チームワーク_C']
            },
            '改善提案力': {
                'description': '改善を提案する能力',
                'skills': ['改善提案力_A', '改善提案力_B', '改善提案力_C']
            }
        }
    else:
        # 従来の鉄鋼業向けスキル階層
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

    # --- 新しいダミーデータを読み込む場合 ---
    if use_new_dummy:
        # 日次生産データを読み込み
        df_daily_prod = pd.read_csv(new_dummy_path)
        df_daily_prod['日付'] = pd.to_datetime(df_daily_prod['日付'])
        
        # 新データの拠点リストを取得
        available_locations = df_daily_prod['拠点'].unique().tolist()
        
        # スキルデータは拠点×工程ごとに生成（各組み合わせ20人）
        skill_data_list = []
        emp_id_counter = 1
        
        for location in available_locations:
            for process in processes:
                for _ in range(20):  # 各拠点×工程で20人
                    skill_data_list.append({
                        '拠点': location,
                        '工程': process,
                        'チーム': np.random.choice(teams),
                        '従業員ID': f'EMP_{location[:2]}_{emp_id_counter:04d}',
                        '評価日': date.today() - timedelta(days=np.random.randint(1, 180))
                    })
                    emp_id_counter += 1
        
        # 各スキルのスコアを生成
        for item in skill_data_list:
            # 拠点ごとにスキルレベルを調整
            if item['拠点'] == '日本 (JP)':
                base_score = np.random.uniform(3.5, 4.8)
            elif item['拠点'] == '拠点A (IN)':
                base_score = np.random.uniform(2.5, 4.0)
            elif item['拠点'] == '拠点B (BR)':
                base_score = np.random.uniform(2.3, 3.8)
            else:  # 拠点C (VN)
                base_score = np.random.uniform(2.2, 3.6)
            
            # 各スキルにスコアを付与（カテゴリごとに少し変動）
            for skill in all_skills:
                variation = np.random.uniform(-0.3, 0.3)
                item[skill] = int(np.clip(base_score + variation, 1, 5))
        
        df_skill = pd.DataFrame(skill_data_list)
        
        # カテゴリ別の平均スコアを計算
        for category in skill_categories:
            category_skills = skill_hierarchy[category]['skills']
            df_skill[f'{category}_平均'] = df_skill[category_skills].mean(axis=1).round(2)
        
        # 総合スキルスコアを追加
        num_employees = len(df_skill)
        df_skill['総合スキルスコア'] = df_skill[all_skills].mean(axis=1).round(2)
        df_skill['生産効率 (%)'] = (60 + df_skill['総合スキルスコア'] * 8 + np.random.randn(num_employees) * 4).clip(75, 98).round(1)
        df_skill['品質不良率 (%)'] = (8 - df_skill['総合スキルスコア'] * 1.2 + np.random.randn(num_employees) * 1).clip(0.5, 8).round(1)
        
        return df_skill, df_daily_prod, skill_hierarchy, all_skills, skill_to_category, skill_categories, processes
    
    # --- 従来のダミーデータ生成ロジック ---
    # （以下、従来のコードをそのまま維持）

    # --- スキルデータ生成 ---
    skill_data = {
        '拠点': np.random.choice(locations, num_data),
        '工程': np.random.choice(processes, num_data),
        'チーム': np.random.choice(teams, num_data),
        '従業員ID': [f'EMP_{i+1:04d}' for i in range(num_data)],
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
    
    # --- 日次生産実績データ生成（シフトローテーション対応） ---
    start_date = date.today() - timedelta(days=60)  # 60日分のデータ
    end_date = date.today()
    production_records = []
    
    # シフトローテーションパターン: 4日日勤 → 2日休み → 4日夜勤 → 2日休み（10日サイクル）
    # Aチーム: Day 0-3 日勤, Day 4-5 休み, Day 6-9 夜勤, Day 10-11 休み
    # Bチーム: Day 0-3 夜勤, Day 4-5 休み, Day 6-9 日勤, Day 10-11 休み  
    # Cチーム: Day 0-1 休み, Day 2-5 日勤, Day 6-7 休み, Day 8-11 夜勤
    
    def get_shift_for_team(team, day_offset):
        """チームと経過日数からシフトを決定"""
        cycle_day = day_offset % 12  # 12日サイクル
        
        if team == 'Aチーム':
            if 0 <= cycle_day <= 3:
                return '日勤'
            elif 4 <= cycle_day <= 5:
                return '休み'
            elif 6 <= cycle_day <= 9:
                return '夜勤'
            else:
                return '休み'
        elif team == 'Bチーム':
            if 0 <= cycle_day <= 3:
                return '夜勤'
            elif 4 <= cycle_day <= 5:
                return '休み'
            elif 6 <= cycle_day <= 9:
                return '日勤'
            else:
                return '休み'
        else:  # Cチーム
            if 0 <= cycle_day <= 1:
                return '休み'
            elif 2 <= cycle_day <= 5:
                return '日勤'
            elif 6 <= cycle_day <= 7:
                return '休み'
            else:
                return '夜勤'
    
    # 日ごとにデータを生成
    for day_offset, single_date in enumerate((start_date + timedelta(n) for n in range((end_date - start_date).days + 1))):
        for loc in locations:
            for process in processes:
                for team in teams:
                    shift = get_shift_for_team(team, day_offset)
                    
                    if shift == '休み':
                        continue  # 休みの日はデータなし
                    
                    # その工程・チームの従業員のスキルを計算
                    team_members = df_skill[
                        (df_skill['拠点'] == loc) & 
                        (df_skill['工程'] == process) & 
                        (df_skill['チーム'] == team)
                    ]
                    
                    if len(team_members) == 0:
                        continue
                    
                    # カテゴリ別の平均スキル
                    category_skills = {}
                    for category in skill_categories:
                        cat_skills = skill_hierarchy[category]['skills']
                        category_skills[f'{category}_平均'] = team_members[cat_skills].mean().mean()
                    
                    avg_skill_for_day = team_members[all_skills].mean().mean()
                    
                    if pd.isna(avg_skill_for_day): 
                        avg_skill_for_day = 3.0

                    # 生産効率と品質（歩留まり）
                    efficiency = (75 + avg_skill_for_day * 4 + np.random.randn() * 3).clip(75, 98).round(1)
                    defect_rate = (6 - avg_skill_for_day * 0.8 + np.random.randn() * 0.8).clip(0.5, 6).round(2)
                    yield_rate = (100 - defect_rate).round(2)  # 歩留まり = 100 - 不良率
                    
                    record = {
                        '日付': single_date,
                        '拠点': loc,
                        '工程': process,
                        'チーム': team,
                        'シフト': shift,
                        '日次生産量 (t)': np.random.randint(500, 3000) * (1 + (avg_skill_for_day - 3.5) / 5),
                        '生産効率 (%)': efficiency,
                        '品質不良率 (%)': defect_rate,
                        '歩留まり (%)': yield_rate,
                        '平均スキル予測値': avg_skill_for_day.round(2),
                        '従業員数': len(team_members)
                    }
                    
                    # カテゴリ別スキル平均を追加
                    for cat, val in category_skills.items():
                        record[cat] = round(val, 2) if not pd.isna(val) else 3.0
                    
                    production_records.append(record)

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