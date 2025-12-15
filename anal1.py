import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

DATA_FOLDER = 'data'

def load_and_merge_data(folder_path):
    all_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    if not all_files:
        print(f"错误：在 '{folder_path}' 文件夹下没有找到任何 .csv 文件！")
        return None

    print(f"找到 {len(all_files)} 个数据文件，正在合并...")
    
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
        except Exception as e:
            print(f"跳过损坏的文件 {filename}: {e}")

    if not df_list:
        return None

    merged_df = pd.concat(df_list, ignore_index=True)
    print(f"合并完成！共包含 {len(merged_df)} 个试次。")
    return merged_df

def analyze_aggregated_data():
    df = load_and_merge_data(DATA_FOLDER)
    if df is None: return

    key_map = {
        'd': 0, 'num_6': 0, '6': 0, 'right': 0,
        'e': 60, 'num_9': 60, '9': 60,
        'q': 120, 'w': 120, 'num_7': 120, '7': 120,
        'a': 180, 'num_4': 180, '4': 180, 'left': 180,
        'z': 240, 'num_1': 240, '1': 240,
        'x': 300, 'c': 300, 'num_3': 300, '3': 300
    }

    df = df[df['Response'].isin(key_map.keys())].copy()
    
    df['RespAngle'] = df['Response'].map(key_map)
    
    df['Delta'] = (df['RespAngle'] - df['TargetAngle']) % 360
    df.loc[df['Delta'] > 180, 'Delta'] -= 360

    error_df = df[df['Correct'] == 0].copy()
    
    n_total = len(df)
    n_errors = len(error_df)
    
    if n_errors == 0:
        print("数据里没有错误试次，无法分析错误分布。")
        return

    print(f"\n=== 数据概览 ===")
    print(f"总试次: {n_total}")
    print(f"错误试次: {n_errors} (错误率: {n_errors/n_total:.1%})")

    n_neighbor = len(error_df[error_df['Delta'].abs() == 60])
    n_opposite = len(error_df[error_df['Delta'].abs() == 180])
    
    neighbor_ratio = n_neighbor / n_errors
    
    print(f"\n=== 空间调谐分析 ===")
    print(f"近邻错误 (±60°): {n_neighbor} 次")
    print(f"正对错误 (180°): {n_opposite} 次")
    print(f"近邻错误占比: {neighbor_ratio:.1%} (若为随机猜测，理论值应接近 40%)")
    

    plt.figure(figsize=(12, 8))
    ax = plt.subplot(111, projection='polar')
    
    counts = df['Delta'].value_counts().sort_index()
    
    angles = np.deg2rad(counts.index.values)
    values = counts.values
    
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    
    bars = ax.bar(angles, values, width=0.8, bottom=0.0, edgecolor='black', alpha=0.85)
    
    for delta, bar in zip(counts.index, bars):
        if delta == 0:
            bar.set_facecolor('#2ecc71') # 绿色: 正确
            bar.set_label('Correct (Target)')
        elif abs(delta) == 60:
            bar.set_facecolor('#e74c3c') # 红色: 近邻错误
            bar.set_label('Neighbor Error (±60°)')
        elif abs(delta) == 120:
            bar.set_facecolor('#f39c12') # 橙色: 远端错误
            bar.set_label('Distal Error (±120°)')
        else: # 180
            bar.set_facecolor('#95a5a6') # 灰色: 正对错误
            bar.set_label('Opposite Error (180°)')

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    sorted_labels = ['Correct (Target)', 'Neighbor Error (±60°)', 'Distal Error (±120°)', 'Opposite Error (180°)']
    sorted_handles = [by_label[l] for l in sorted_labels if l in by_label]
    sorted_labels_present = [l for l in sorted_labels if l in by_label]
    
    plt.legend(sorted_handles, sorted_labels_present, loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.title(f"Aggregated Error Distribution (N={n_total})\nNeighbor Error Ratio: {neighbor_ratio:.1%}", y=1.1, fontsize=14)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_aggregated_data()