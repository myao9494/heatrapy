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

# ## 1コンポーネント
#

# 基本

# +
import heatrapy as ht
import pandas as pd
import os

if os.path.exists("heat_transfer.txt"):
    os.remove("heat_transfer.txt")
    
example = ht.single_object(amb_temperature=293, materials=('water',), borders=(1,21),materials_order=(0,),
                            dx=0.001, dt=0.001, file_name='heat_transfer.txt',boundaries=(0,0), Q=[], Q0=[],initial_state=False)

example.Cp[1],example.k[1],example.rho[1]

example.set_input_heat_transfer(1,700,1500)

example.set_radiation(1,0.9,293.15)

example.compute(timeInterval=30, write_interval=10, solver='implicit_k(x)')

df = pd.read_csv("heat_transfer.txt")
df=df.drop("heat[1](W)", axis=1)
df=df.drop("heat[-2](J)", axis=1)
df = df.set_index("time(s)")
df.plot(figsize=(15,8))
# -

# ２物質の固着

# +
import heatrapy as ht
import pandas as pd
import utility
import os

if os.path.exists("example.txt"):
    os.remove("example.txt")
    
example = ht.single_object(amb_temperature=293, materials=('Gd','Cu'), borders=(1,11,21),materials_order=(0,1),
                            dx=0.05, dt=0.1, file_name='example.txt',boundaries=(300,0), Q=[], Q0=[],initial_state=False)
example.compute(timeInterval=100000, write_interval=1000, solver='implicit_k(x)')

# +
df = pd.DataFrame({"time(s)":[0,100,200,300,1000],
                   "Heat_transfer_coefficient":[30,90,45,50,20],
                   "temparature":[500,600,650,450,300]
                  })

f_Heat_transfer_coefficient = utility.create_function(df["time(s)"], df["Heat_transfer_coefficient"])
f_temparature = utility.create_function(df["time(s)"], df["temparature"])

example.set_input_heat_transfer_function(1,f_Heat_transfer_coefficient,f_temparature)
# -

example.compute(timeInterval=100000, write_interval=1000, solver='implicit_k(x)')

df = pd.read_csv("example.txt")
df=df.drop("heat[1](W)", axis=1)
df=df.drop("heat[-2](J)", axis=1)
df = df.set_index("time(s)")
# df.plot(figsize=(15,8))

df_taisho = df.T

import numpy as np
df_taisho = df_taisho.set_index(pd.Series(np.arange(0,11,0.5)))
df_taisho = df_taisho[100000.000001]
df_taisho = df_taisho[0:10]

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set()# SeabornのデフォルトStyleを使用
fig = plt.figure(figsize=(5,4))# グラフのサイズを設定(横×縦)
ax = fig.add_subplot(111)
df_taisho.plot()
ax.set_xticks(np.arange(0,11,1))# X軸のTick（目盛）の位置を設定
ax.set_yticks(np.arange(297, 301., 0.5))# X軸のTick（目盛）の表記を設定

# ## 2コンポーネント

# ## 2コンポーネント

import heatrapy as ht
import pandas as pd
import utility
import os

# コンポーネント1の特性

material_1 = "water"
length_1 = 50

# コンポーネント2の特性

material_2 = "Gd"
length_2 = 50

# 共通事項

# +
init_temperature = 293 #初期温度
output_file_name_header = "2comp_test"

analysis_time = 1000
dt = 0.1
# -

# 解析モデルの作成

# + {"code_folding": []}
if os.path.exists(output_file_name_header+"_0.txt"):
    os.remove(output_file_name_header+"_0.txt")
if os.path.exists(output_file_name_header+"_1.txt"):
    os.remove(output_file_name_header+"_1.txt")

two_comp = ht.system_objects(number_objects=2, materials=(material_1, material_2),
                 objects_length=(length_1, length_2), amb_temperature=init_temperature, dx=0.01, dt=dt,
                 file_name=output_file_name_header,boundaries=((0,0), (1, 0)), initial_state=False, materials_path=False)
# -

# 境界条件の設定（断熱以外のオブジェクトを設定する）

two_comp.objects[0].boundaries=(300,0)

for i in range(len(two_comp.objects)):
    print("コンポーネント" + str(i) + " （前端温度、後端温度)=" + str(two_comp.objects[i].boundaries) + "  ※0は断熱条件")

# 熱伝達で入熱

# +
# two_comp.set_input_heat_transfer((0,1),700,900)
# -

# 熱伝達で入熱 関数

df = pd.DataFrame({"time(s)":[0,100,200,300,1000],
                   "Heat_transfer_coefficient":[300,500,600,900,1200],
                   "temparature":[1000,1200,1500,1700,1800]
                  })
f_Heat_transfer_coefficient = utility.create_function(df["time(s)"], df["Heat_transfer_coefficient"])
f_temparature = utility.create_function(df["time(s)"], df["temparature"])
two_comp.set_input_heat_transfer_function((0,1),f_Heat_transfer_coefficient,f_temparature)

df.plot(x="time(s)")

# 輻射を追加 

two_comp.set_radiation((0,1),0.9,293.15)

# 接触の定義

two_comp.contactAdd(((0,11),(1,1),30000))
two_comp.contacts

# 問題を解く

two_comp.compute(timeInterval=analysis_time, write_interval=100, solver='implicit_k(x)')

# ポスト処理

df_1 = pd.read_csv(output_file_name_header+"_0.txt",dtype=float).drop(["T[0] (K)"],axis=1)
df_2 = pd.read_csv(output_file_name_header+"_1.txt",dtype=float).drop(["T[0] (K)"],axis=1)

1493.298796

df_1

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


