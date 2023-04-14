---
id: "doc-1a1d427b3817"
title: "shell实现面向对象编程"
date: "2023-04-14T15:57:00"
categories: ["Linux 与 Shell", "日常运维"]
tags: ["Linux 与 Shell", "日常运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/08-运维技巧/birdben/66979587.html"
---

# shell实现面向对象编程

原文地址: <https://coolshell.cn/articles/5035.html>
写Shell脚本的时候可以把你的变量和函数放到一个类中？不要以为这不可能

当然，这里并不是真正的面向对象，因为其只是封装罢了，还没有支持继承和多态。最变态的是居然还支持typeid，靠！

- 这个脚本定义了class,  func, var, new 等函数，其实这些就是所谓的关键字。
- class是一个函数，主要是记录类名。
- func和var实际上是把成员函数名和成员变量记成有相同前缀的各种变量。
- new方法主要是记录实例。大家重点看看new函数里的那个for循环，最核心的就在那里了。

脚本如下所示：

```bash
#!/bin/bash
# -------------------------------------------------------------------
# OO support functions
# Kludged by Pim van Riezen <[邮箱已脱敏]>
# -------------------------------------------------------------------
DEFCLASS=""
CLASS=""
THIS=0

class() {
 DEFCLASS="$1"
 eval CLASS_${DEFCLASS}_VARS=""
 eval CLASS_${DEFCLASS}_FUNCTIONS=""
}

static() {
 return 0
}

func() {
 local varname="CLASS_${DEFCLASS}_FUNCTIONS"
 eval "$varname=\"\${$varname}$1 \""
}

var() {
 local varname="CLASS_${DEFCLASS}_VARS"
 eval $varname="\"\${$varname}$1 \""
}

loadvar() {
 eval "varlist=\"\$CLASS_${CLASS}_VARS\""
 for var in $varlist; do
 eval "$var=\"\$INSTANCE_${THIS}_$var\""
 done
}

loadfunc() {
 eval "funclist=\"\$CLASS_${CLASS}_FUNCTIONS\""
 for func in $funclist; do
 eval "${func}() { ${CLASS}::${func} \"\$*\"; return \$?; }"
 done
}

savevar() {
 eval "varlist=\"\$CLASS_${CLASS}_VARS\""
 for var in $varlist; do
 eval "INSTANCE_${THIS}_$var=\"\$$var\""
 done
}

typeof() {
 eval echo \$TYPEOF_$1
}

new() {
 local
 local cvar="$2"
 shift
 shift
 local id=$(uuidgen | tr A-F a-f | sed -e "s/-//g")
 eval TYPEOF_${id}=$class
 eval $cvar=$id
 local funclist
 eval "funclist=\"\$CLASS_${class}_FUNCTIONS\""
 for func in $funclist; do
 eval "${cvar}.${func}() {
      local t=\$THIS; THIS=$id; local c=\$CLASS; CLASS=$class; loadvar;
      loadfunc; ${class}::${func} \"\$*\"; rt=\$?; savevar; CLASS=\$c;
      THIS=\$t; return $rt;
    }"
 done
 eval "${cvar}.${class} \"\$*\" || true"
}
```

#例程验证

```python
# -------------------------------------------------------------------
# Example code
# -------------------------------------------------------------------
# class definition
class Storpel
 func Storpel
 func setName
 func setQuality
 func print
 var name
 var quality
# class implementation
Storpel::Storpel() {
 setName "$1"
 setQuality "$2"
 if [ -z "$name" ]; then setName "Generic"; fi
 if [ -z "$quality" ]; then setQuality "Normal"; fi
}
Storpel::setName() { name="$1"; }
Storpel::setQuality() { quality="$1"; }
Storpel::print() { echo "$name ($quality)"; }
# usage
new Storpel one "Storpilator 1000" Medium
new Storpel two
new Storpel three
two.setName "Storpilator 2000"
two.setQuality "Strong"
one.print
two.print
three.print
echo ""
echo "one: $one ($(typeof $one))"
echo "two: $two ($(typeof $two))"
echo "three: $three ($(typeof $two))"
```
