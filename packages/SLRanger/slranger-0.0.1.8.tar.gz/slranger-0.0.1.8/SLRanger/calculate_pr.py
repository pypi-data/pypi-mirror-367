import os
import plotnine as p9
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

def get_file_list(directory_path):
    file_list = []
    try:
        # 检查路径是否存在
        if not os.path.exists(directory_path):
            return [f"错误：路径 '{directory_path}' 不存在"]

        # 获取文件夹中的所有文件和子文件夹
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            # 只添加文件，排除文件夹
            if os.path.isfile(item_path):
                file_list.append(item)

        return file_list if file_list else ["文件夹中没有文件"]

    except PermissionError:
        return [f"错误：没有权限访问路径 '{directory_path}'"]
    except Exception as e:
        return [f"发生错误：{str(e)}"]

def calculate_pr(tru_df,pre_df):
    tru_df = pd.read_csv(tru_df)['gene'].values
    pre_df = pd.read_csv(pre_df)['gene'].values
    tru_set=set(tru_df)
    pre_set=set(pre_df)
    tp_set = tru_set.intersection(pre_set)
    precision = len(tp_set) / len(pre_set)
    recall = len(tp_set) / len(tru_set)
    return precision, recall

tru_path ='/t4/ywshao/cbr_cni_directrna/raw_data/cbn_SL/operon_ground_truth.csv'
pre_path='/t4/ywshao/cbr_cni_directrna/raw_data/cbn_SL/0710/operon_sw_detected/'

file_list = get_file_list(pre_path)
result_list = []
for file_name in file_list:
    file_path = os.path.join(pre_path, file_name)
    precision, recall = calculate_pr(tru_df=tru_path, pre_df=file_path)
    result_list.append([file_name.split('.')[0], precision, recall])
result_df = pd.DataFrame(result_list, columns=['file_name', 'precision', 'recall'])
print(result_df)
pp = p9.ggplot(result_df, p9.aes(y='precision', x='recall', fill='file_name')) \
     + p9.theme_bw() \
     + p9.geom_point(color='none',size=3,alpha=0.5,position='jitter')\
     + p9.xlim(0,1)\
     + p9.ylim(0,1)\
     + p9.theme(
    figure_size=(5, 5),
    axis_text=p9.element_text(size=12, family='Arial'),
    axis_title=p9.element_text(size=12, family='Arial'),
    panel_grid_minor=p9.element_blank(),
    title=p9.element_text(size=12, family='Arial'),
    strip_background=p9.element_rect(alpha=0),
    strip_text=p9.element_text(size=12, family='Arial'),
    legend_position='bottom'
)
pp.show()

