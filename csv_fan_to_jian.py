# t2s_fixpath.py
import pandas as pd
import opencc
import math
from pypinyin import pinyin, Style

'''简介：
1. 将小狼毫的繁体词库.dict.yaml转换为符合小企鹅标准的简体txt词库
2. 输入路径为IN_TSV
3. 输入中的0词频依照小企鹅官方建议设为0，需修改则调整第5步
'''

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

# 5. 计算对数词频
max_freq = df_merged.iloc[:, 2].max()
df_merged.iloc[:, 2] = df_merged.iloc[:, 2].apply(
    lambda x: 0 if x == 0 else math.log10(x / max_freq)
)

# 6. 按对数词频降序排列
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