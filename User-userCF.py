#导入一些基本库
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
import numpy as np
np.set_printoptions(suppress=True)

#首先定义jaccard相似度算法
def jaccard(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union

#返回相似度矩阵
def count_cov(aff):
    df_sim = pd.DataFrame()
    for i in range(len(aff)):
        vip1 = aff.iloc[i, 0]
        sku1 = aff.iloc[i, 1]
        for j in range(len(aff)):
            vip2 = aff.iloc[j, 0]
            sku2 = aff.iloc[j, 1]
            if vip1 == vip2:
                sim = 1
            else:
                sim = jaccard(sku1, sku2)
            df_sim.loc[vip1, vip2] = sim
    return df_sim

#推荐结果--返回dataframe
def final_result(test):
    result = pd.DataFrame()
    for i in test.index:
        rank = test.loc[:, i].sort_values(ascending=False).head(4)
        sku_list_old = []
        index1 = aff_test[aff_test['VIP_ID'] == i].index[0]
        sku_list_old.append(aff_test.iloc[index1, 1])
        sku_list = []
        for j in rank.index[1:4]:
            index2 = aff_test[aff_test['VIP_ID'] == j].index[0]
            sku_list.append(aff_test.iloc[index2, 1])
        final_recommend = [i for i in sku_list if i not in sku_list_old]
        result = result.append({'VIP_ID': i, 'recommend_sku': final_recommend}, ignore_index=True)
        return result

#read the data set，for this version, we choose user-user sim
df_sale = pd.read_csv('F_SALES_UN.csv',encoding='utf-16LE')

#对时间进行筛选，我们先用21年数据进行测试
year_fliter = [202101,202102,202103,202104,202105,202106]
df_sale = df_sale[df_sale['YEAR_MONTH'].isin(year_fliter)]

#user-user只能对VIP用户进行筛选
df_sale = df_sale[df_sale['VIP_ID']!=0]

#统一dataframe的格式，左边为VIPid，右边为购买过的商品-这样做有利于后期network的analysis
aff= df_sale.groupby('VIP_ID')['SKU_CODE'].agg(','.join)
aff= aff.apply(pd.unique)
aff= aff.apply(pd.Series)
aff = aff.reset_index()
aff.rename(columns = {0:'sku'},inplace = True)

#选取前100个用于测试,输出结果到XLS
aff_test = aff.head(100)
recommend = final_result(count_cov(aff_test))
recommend.to_excel('CFresult.xls',index = False)
