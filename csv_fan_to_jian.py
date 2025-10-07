# t2s_fixpath.py
import pandas as pd
import opencc
import math
from pypinyin import pinyin, Style

# 1. 路径设置
IN_TSV = r"C:\Users\ZhuanZ（无密码）\Desktop\luna_pinyin_export.dict.yaml"  # 原始繁体文件
OUT_TXT = 'gbk.txt'  # 输出简体文件

# 2. 读TSV文件
df = pd.read_csv(IN_TSV, sep='\t', header=None)

# 3. 繁→简转换（只改第一列）
cc = opencc.OpenCC('t2s')  # 繁体 to 简体
df.iloc[:, 0] = df.iloc[:, 0].astype(str).apply(cc.convert)

# 4. 合并重复行，将第三列数字相加
# 确保第三列是数字类型
df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2], errors='coerce').fillna(0)

# 按第一列分组，对第二列取第一个值，第三列求和
df_merged = df.groupby(df.iloc[:, 0]).agg({
    df.columns[1]: 'first',  # 第二列取第一个值
    df.columns[2]: 'sum'     # 第三列求和
}).reset_index()

# 重新排列列的顺序为原始顺序
df_merged = df_merged[[df.columns[0], df.columns[1], df.columns[2]]]

# 5. 计算新的score值
total_freq = df_merged.iloc[:, 2].sum()  # 总频次

def calculate_score(freq):
    if freq == 0:
        return 0
    prob = freq / total_freq  # 概率
    score = math.log10(prob) * 10  # 计算对数概率并乘以10
    
    # 转换为整数并应用限制
    score_int = int(score)
    if score_int > 0:
        score_int = 0
    if score_int < -127:
        score_int = -127
    
    return score_int

df_merged.iloc[:, 2] = df_merged.iloc[:, 2].apply(calculate_score)

# 6. 按score降序排列（数值越大表示词频越高）
df_merged = df_merged.sort_values(by=df.columns[2], ascending=False)

# 7. 生成完整拼音（使用'分隔）
def generate_pinyin(chinese_text):
    pinyin_list = pinyin(chinese_text, style=Style.NORMAL)
    return "'".join([item[0] for item in pinyin_list])

df_merged.iloc[:, 1] = df_merged.iloc[:, 0].apply(generate_pinyin)

# 8. 写入文件，使用空格分隔
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    for _, row in df_merged.iterrows():
        line = f"{row[0]} {row[1]} {row[2]}\n"
        f.write(line)

print('转换完成 →', OUT_TXT)
print(f"总词频: {total_freq}")
print(f"score范围: {df_merged.iloc[:, 2].min()} 到 {df_merged.iloc[:, 2].max()}")