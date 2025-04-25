import pandas as pd
import os
import argparse
from datetime import datetime

def summarize_project_data(project_path):
    """
    彙總專案中每日的符號資料，依模組加總大小。
    
    Args:
        project_path (str): 專案資料夾路徑
    """
    all_summaries = []
    
    # 取得所有日期資料夾
    date_folders = sorted([d for d in os.listdir(project_path) 
                         if os.path.isdir(os.path.join(project_path, d))])
    
    for date_folder in date_folders:
        csv_path = os.path.join(project_path, date_folder, "symbols.csv")
        if not os.path.exists(csv_path):
            continue
            
        # 讀取CSV檔案
        df = pd.read_csv(csv_path)
        
        # 計算每個模組的總大小
        module_sizes = df.groupby('symbol_module')['symbol_size'].sum().reset_index()
        
        # 計算每種記憶體類型的使用量
        memory_usage = df.groupby('symbol_physical_memory')['symbol_size'].sum().to_dict()
        
        # 建立該日期的彙總資料
        summary = {
            'date': date_folder,
            'total_symbols': len(df),
            'total_size': df['symbol_size'].sum(),
            'ilm_usage': memory_usage.get('ilm', 0),
            'dlm_usage': memory_usage.get('dlm', 0),
            'sysram_usage': memory_usage.get('sysram', 0),
            'ext_memory1_usage': memory_usage.get('ext_memory1', 0),
            'ext_memory2_usage': memory_usage.get('ext_memory2', 0),
        }
        
        # 加入各模組的大小
        for _, row in module_sizes.iterrows():
            summary[f"module_{row['symbol_module']}_size"] = row['symbol_size']
        
        all_summaries.append(summary)
    
    # 轉換為DataFrame
    summary_df = pd.DataFrame(all_summaries)
    
    # 排序欄位
    cols = ['date', 'total_symbols', 'total_size', 
            'ilm_usage', 'dlm_usage', 'sysram_usage',
            'ext_memory1_usage', 'ext_memory2_usage']
    module_cols = [col for col in summary_df.columns if col.startswith('module_')]
    cols.extend(sorted(module_cols))
    
    # 輸出彙總CSV
    output_path = os.path.join(project_path, "summary.csv")
    summary_df[cols].to_csv(output_path, index=False)
    print(f"✅ Summary saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='彙總專案符號資料')
    parser.add_argument('--project', '-p', required=True, 
                       help='專案名稱 (位於 data/ 目錄下)')
    
    args = parser.parse_args()
    project_path = os.path.join("", args.project)
    
    if not os.path.exists(project_path):
        print(f"錯誤：找不到專案資料夾 {project_path}")
        exit(1)
        
    summarize_project_data(project_path)
