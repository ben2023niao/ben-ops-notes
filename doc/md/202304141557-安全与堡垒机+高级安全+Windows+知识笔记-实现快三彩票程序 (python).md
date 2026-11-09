---
id: "doc-caa78401c5bb"
title: "实现快三彩票程序 (python)"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Windows", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/72066872.html"
---

# 实现快三彩票程序 (python)

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E9%AB%98%E7%BA%A7%E5%AE%89%E5%85%A8%2BWindows%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E5%AE%9E%E7%8E%B0%E5%BF%AB%E4%B8%89%E5%BD%A9%E7%A5%A8%E7%A8%8B%E5%BA%8F%20%28python%29.md)

【开发该软件的操作系统】：windows10

【软件开发环境/开发工具】：PyCharm

【编程语言】：Python

```python
#福利彩票快三程序
import random

'''
*********************************************************
快3游戏是指以三个号码组合为一注进行单式投注。
每个投注号码为1-6共六个自然数中的任意一个。
一组三个号码的组合称为一注,每注金额人民币2元。
购买者可对其选定的投注号码进行多倍投注,投注倍数范围为2-99倍。
单张彩票的投注金额最高不得超过20000元。
*********************************************************
'''
# *******************************************************
# 快3游戏根据号码组合共分为
# “和值”、“三同号”、“二同号”、“三不同号”、“二不同号”、“三连号通选”
# 投注方式
# *******************************************************
def printlist():
print("     请您选择您的玩法       ")
print("      1   和值投注         ")
print("      2   三同号投注         ")
print("      3   二同号投注         ")
print("      4   三不同号投注         ")
print("      5   二不同号投注         ")
print("      6   三连号通选投注         ")
def multipleprice(n):
while(True):
m = int(input("请选择投注倍数：")) # 投注倍数范围为2-99倍
if m < 2 or m > 99:
print("不在投注倍数的范围内，请重新选择投注倍数：")
continue
else:
l = m * n * 2
if l >= 20000:
print("超出规定金额请重新下注")
continue
else:
print("选号下注成功，您应支付的金额为：", l)
exit()
# *******************************************************
# 和值投注：
# 是指对三个号码的和值进行投注包括“和值4”至“和值17”投注。
# *******************************************************
def ruler1():
print("************和  值   投  注************")
flag=0
while (True):
arrs = input("请选择三个（1~6）的数下注：")
arrs = [int(value) for value in arrs.split(' ')]
sum = 0
for arr in arrs:
if arr < 1 or arr > 6:#判断投注号码是否在1~6
print("您选的号超出了投注范围，请重新投注！")
# break_all = True
flag=1
break
else:
sum += arr
if flag==1 : #不执行下面的语句
flag=0
else :
if sum < 4 or sum > 17: #判断和值是否在4~17
print("您的和值不合法，请重新投注!")
else:
print("您的和值是：",sum)
break
multipleprice(1)
# ****************************************************************
# 三同号通选：对所有相同的三个号码（111、222、…、666）进行全包投注
# 三同号单选：从所有相同的三个号码（111、…、666）中任意选择一组号码进行投注
# ****************************************************************
def ruler2():
print("***********三  同  号  投  注***********")
flag = 0
while(True):
i = int(input("三同号通选（选0）、三同号单选（选1）:"))
if i == 0: # 三同号通选：对所有相同的三个号码（111、222、…、666）进行全包投注
print("您将选择（111、222、…、666）六注下注！")
multipleprice(6)
break
elif i == 1: # 三同号单选：从所有相同的三个号码（111、…、666）中任意选择一组号码进行投注
print("请从所有相同的三个号码（111、…、666）中任意选择一组号码进行投注")
arrs = input("请选择相同的三个号码：")
arrs = [int(value) for value in arrs.split(' ')]
for arr in arrs:
if arr < 1 or arr > 6: # 判断投注号码是否在1~6
print("您选的号码超出了投注范围，请重新选择投注方式！")
flag = 1
break
if flag == 1: # 退出内循环,并且不执行下面的语句
flag = 0
elif arrs[0] == arrs[1] and arrs[1] == arrs[2]:
print("您选择的号为：", arrs)
multipleprice(1)
break
else:
print("您输入的号不合法，请重新选择投注方式！")
else:
print("您选错了，请您重选!")
continue
# **********************************************************
# 二同号复选：对三个号码中两个指定的相同号码和一个任意号码进行投注
# 二同号单选：对三个号码中两个指定的相同号码和一个指定的不同号码进行投注
# **********************************************************
def ruler3():
print("***********二  同  号  投  注***********")
flag = 0
while(True):
i = int(input("二同号复选（选0）、二同号单选（选1）:"))
if i == 0: # 二同号复选：对三个号码中两个指定的相同号码和一个任意号码进行投注
arrs = input("请选择两个同号投注值：")
arrs = [int(value) for value in arrs.split(' ')]
sum = arrs[0]
for arr in arrs:
if arr < 1 or arr > 6: # 判断投注号码是否在1~6
print("您选的号超出了投注范围，请重新选择投注方式！")
flag = 1
break
elif sum != arr:
sum = arr
print("您输入的号不合法，请重新选择投注方式！")
flag = 1
if flag == 1: #退出内循环,并且不执行下面的语句
flag = 0
else:
ran01 = random.randint(1, 6)
arrs.append(ran01)
print("您选择的号为：", arrs)
multipleprice(1)
elif i == 1: # 二同号单选：对三个号码中两个指定的相同号码和一个指定的不同号码进行投注
arrs = input("请按顺序选择两个同号和一个不同号进行投注：")
arrs = [int(value) for value in arrs.split(' ')]
for arr in arrs:
if arr < 1 or arr > 6: # 判断投注号码是否在1~6
print("您选的号超出了投注范围，请重新选择投注方式！")
flag = 1
break
if flag == 1: # 退出内循环,并且不执行下面的语句
flag = 0
elif arrs[0] == arrs[1] and arrs[1] != arrs[2]:
print("您选择的号为：", arrs)
multipleprice(1)
break
else:
print("您输入的号不合法，请重新选择投注方式！")
else:
print("您的选择有误，请重新选择投注方式！")
continue
# *******************************************************
#三不同号：对三个各不相同的号码进行投注
# *******************************************************
def ruler4():
print("*********三  不  同  号  投  注*********")
flag = 0
while (True):
arrs = input("请选择三个不同号码进行投注：")
arrs = [int(value) for value in arrs.split(' ')]
for arr in arrs:
if arr < 1 or arr > 6: # 判断投注号码是否在1~6
print("您选的号超出了投注范围，请重新选择投注方式！")
flag = 1
break
if flag == 1: # 退出内循环,并且不执行下面的语句
flag = 0
elif arrs[0] == arrs[1] or arrs[1] == arrs[2] or arrs[0]==arrs[2]:
print("您输入的号不合法，请重新选择投注方式！")
continue
else:
print("您选择的号为：", arrs)
multipleprice(1)
# *******************************************************
#二不同号：对三个号码中两个指定的不同号码和一个任意号码进行投注
# *******************************************************
def ruler5():
print("*********二  不  同  号  投  注*********")
flag = 0
while (True):
arrs = input("请选择两个不同号码进行投注:")
arrs = [int(value) for value in arrs.split(' ')]
for arr in arrs:
if arr < 1 or arr > 6: # 判断投注号码是否在1~6
print("您选的号超出了投注范围，请重新投注！")
flag = 1
break
if flag == 1: # 退出内循环,并且不执行下面的语句
flag = 0
elif arrs[0] == arrs[1]:
print("您输入的号不合法，请重新投注！")
continue
else:
ran01 = random.randint(1, 6)
arrs.append(ran01)
print("您选择的号为：", arrs)
multipleprice(1)
# *************************************************************
#三连号通选(顺子全包)：对所有三个相连的号码（123、234、345、456）进行投注
# *************************************************************
def ruler6():
print("*******三  连  号  通  选  投  注*******")
print("您将选择（123、234、345、456）四注下注！")
multipleprice(4)
while (True):
printlist()
k = int(input("请输入您的投注方式："))
if k == 1:
ruler1()
elif k == 2:
ruler2()
elif k == 3:
ruler3()
elif k == 4:
ruler4()
elif k == 5:
ruler5()
elif k == 6:
ruler6()
```
