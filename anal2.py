
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import glob
import os
sns.set(style="ticks", context="talk")

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
DATA_FOLDER = 'data'


def load_data():
    all_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))
    if not all_files:
        print("未找到数据文件！")
        return None
    
    df_list = []
    for f in all_files:
        try:
            temp = pd.read_csv(f)
            if 'N_Choice' not in temp.columns:
                if '6Choice' in f: temp['N_Choice'] = 6
                elif '4Choice' in f: temp['N_Choice'] = 4
                elif '2Choice' in f: temp['N_Choice'] = 2
                else: temp['N_Choice'] = 6 # 默认值
            
            df_list.append(temp)
        except Exception as e:
            print(f"读取 {f} 失败: {e}")
            
    if not df_list: return None
    
    df = pd.concat(df_list, ignore_index=True)
    
    df = df[(df['RT'] > 0.1) & (df['RT'] < 5.0)]
    return df

def plot_psychometrics(df):
    data_n6 = df[df['N_Choice'] == 6]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. 正确率曲线 (Psychometric Curve)
    sns.lineplot(data=data_n6, x='Coherence', y='Correct', marker='o', ax=axes[0], color='navy', err_style="bars")
    axes[0].set_title('心理物理曲线 (Accuracy)')
    axes[0].set_ylabel('正确率 (Accuracy)')
    axes[0].set_ylim(0, 1.05)
    axes[0].axhline(1/6, linestyle='--', color='gray', label='随机水平 (16.7%)')
    axes[0].legend()

    # 2. 计时曲线 (Chronometric Curve) - 只看正确试次
    correct_trials = data_n6[data_n6['Correct'] == 1]
    sns.lineplot(data=correct_trials, x='Coherence', y='RT', marker='o', ax=axes[1], color='firebrick', err_style="bars")
    axes[1].set_title('计时曲线 (Chronometric Curve)')
    axes[1].set_ylabel('反应时 (RT, s)')
    
    plt.tight_layout()
    plt.show()

def plot_rt_distribution(df):
    """图2: 反应时分布 (长尾效应)"""
    min_coh = df['Coherence'].min()
    target_data = df[(df['N_Choice'] == 6) & (df['Coherence'] == min_coh)]
    
    if len(target_data) < 10:
        print("提示：N=6且低连贯性的数据太少，尝试使用所有 N=6 数据。")
        target_data = df[df['N_Choice'] == 6]

    if len(target_data) == 0: return

    plt.figure(figsize=(10, 6))
    
    sns.histplot(target_data['RT'], kde=True, bins=30, color='teal', stat='density')
    
    mean_rt = target_data['RT'].mean()
    median_rt = target_data['RT'].median()
    plt.axvline(mean_rt, color='red', linestyle='--', label=f'Mean: {mean_rt:.2f}s')
    plt.axvline(median_rt, color='orange', linestyle='-', label=f'Median: {median_rt:.2f}s')
    
    plt.title(f'反应时分布 (N=6, Coherence={min_coh})')
    plt.xlabel('反应时 (RT, s)')
    plt.legend()
    plt.xlim(0, 3.0)
    plt.show()
    
    skew = target_data['RT'].skew()
    print(f"\n>> RT分布偏度 (Skewness): {skew:.2f}")

if __name__ == "__main__":
    df_all = load_data()
    
    if df_all is not None:
        print(f"共加载 {len(df_all)} 条数据。")
        
        print("\n--- 正在绘制 1. 基础心理物理曲线 ---")
        plot_psychometrics(df_all)
        
        print("\n--- 正在绘制 2. 反应时分布图 ---")
        plot_rt_distribution(df_all)