# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ! code .

# ## 2コンポーネント

import heatrapy as ht
import pandas as pd
import os

# コンポーネント1の特性

material_1 = "water"
length_1 = 10

# コンポーネント2の特性

material_2 = "Cu"
length_2 = 20

# 共通事項

# +
init_temperature = 293 #初期温度
output_file_name_header = "2comp_test"

analysis_time = 60
dt = 0.01
# -

# 解析モデルの作成

# + {"code_folding": []}
if os.path.exists(output_file_name_header+"_0.txt"):
    os.remove(output_file_name_header+"_0.txt")
if os.path.exists(output_file_name_header+"_1.txt"):
    os.remove(output_file_name_header+"_1.txt")

two_comp = ht.system_objects(number_objects=2, materials=(material_1, material_2),
                 objects_length=(length_1, length_2), amb_temperature=init_temperature, dx=0.001, dt=0.01,
                 file_name=output_file_name_header,boundaries=((0,0), (1, 0)), initial_state=False, materials_path=False)
# -

# 境界条件の設定（断熱以外のオブジェクトを設定する）

two_comp.objects[0].boundaries=(0,0)

for i in range(len(two_comp.objects)):
    print("コンポーネント" + str(i) + " （前端温度、後端温度)=" + str(two_comp.objects[i].boundaries) + "  ※0は断熱条件")

# 熱伝達で入熱

two_comp.set_input_heat_transfer((0,1),700,900)

# 接触の定義

two_comp.contactAdd(((0,11),(1,1),30000))
two_comp.contacts

# 問題を解く

two_comp.compute(timeInterval=analysis_time, write_interval=100, solver='implicit_k(x)')

# ポスト処理

df_1 = pd.read_csv(output_file_name_header+"_0.txt",dtype=float).drop(["T[0] (K)"],axis=1)
df_2 = pd.read_csv(output_file_name_header+"_1.txt",dtype=float).drop(["T[0] (K)"],axis=1)

df_1.plot(x="time(s)",figsize=(15,8))

df_2.plot(x="time(s)",figsize=(15,8))

# ## 3コンポーネント

import heatrapy as ht
import pandas as pd
import os

output_file_name_header = "test_1"

three_comp = ht.system_objects(number_objects=3, materials=('Cu', 'AL','Cu'),
                 objects_length=(10, 10,20), amb_temperature=293, dx=0.001, dt=0.01,
                 file_name=output_file_name_header, initial_state=False,
                 boundaries=((2, 0), (3, 0),(0,0)), materials_path=False)

three_comp.objects[0].boundaries=(500,0)
for i in range(len(three_comp.objects)):
    print("コンポーネント" + str(i) + " （前端温度、後端温度)=" + str(three_comp.objects[i].boundaries) + "  ※0は断熱条件")

three_comp.contacts.add(((0,10),(1,1),3000))

three_comp.contacts.add(((1,10),(2,1),5000))

three_comp.compute(timeInterval=60, write_interval=100, solver='implicit_k(x)')

df_1 = pd.read_csv(output_file_name_header+"_0.txt",dtype=float).drop(["T[0] (K)"],axis=1)
df_2 = pd.read_csv(output_file_name_header+"_1.txt",dtype=float).drop(["T[0] (K)"],axis=1)
df_3 = pd.read_csv(output_file_name_header+"_2.txt",dtype=float).drop(["T[0] (K)"],axis=1)

df_1.plot(x="time(s)",figsize=(15,8))

df_2.plot(x="time(s)",figsize=(15,8))

df_3.plot(x="time(s)",figsize=(15,8))


