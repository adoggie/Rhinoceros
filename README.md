# 位置监控服务系统(Rhinoceros)

## 1. 简介
系统提供位置服务对象的数据接入、存储、在线位置、历史轨迹回放等功能，在系统实现时充分考虑软件独立性、模块性实现可控制、可扩展的要求。

完全独立于业务系统，统一输出给应用程一致的交互呈现和数据接口。

系统采用系统模块边界化、模块化的思路，将各个功能的实现切割到不同子系统实现，通过消息中间件提供的数据总线实现控制和数据消息的传递。 

## 2. 系统组成
(adapter,shuffler,aggregator,tracer,locuserservice)

### 2.1. adapter 位置接入服务
提供标准的接入框架，接收不同数据源的输入，包括：车机、app和第三方消息，诸如：etc，天气，道路维修。 

### 2.2. aggregator 数据清洗、整理、缓冲、转换 服务

### 2.3. tracer 实时位置提供和历史轨迹查询提供，空间索引和搜索


## 3.设计方案

3.1 [系统架构设计图－1](https://github.com/adoggie/rhinoceros/blob/master/doc/Camel车辆运输监控服务系统(rhino)架构_1.1_zhangbin_20170324.png)

3.2 [系统架构设计图－2](https://github.com/adoggie/rhinoceros/blob/master/doc/Camel%E8%BD%A6%E8%BE%86%E8%BF%90%E8%BE%93%E7%9B%91%E6%8E%A7%E7%B3%BB%E7%BB%9F_1.3_zhangbin_20170425.png)

3.3 [系统架构设计图－3](https://github.com/adoggie/rhinoceros/blob/master/doc/camel%E6%8E%A5%E5%85%A5%E6%9C%8D%E5%8A%A1%E6%8A%80%E6%9C%AF%E6%9E%B6%E6%9E%84_1.0_zhangbin_20170318.png)

3.4 [与外部接口层集成方法](https://github.com/adoggie/rhinoceros/blob/master/doc/images/teresa%E9%9B%86%E6%88%90%E8%AE%A4%E8%AF%81%E7%A4%BA%E6%84%8F%E5%9B%BE_0.1_zhangbin_20170512.png)


## 4.接口定义
 4.1 [webapi接口定义](https://github.com/adoggie/rhinoceros/tree/master/doc)
 
 4.2 [数据规格定义](https://github.com/adoggie/rhinoceros/tree/master/doc)


## 5.运行

5.1 [全国热点图](https://github.com/adoggie/rhinoceros/blob/master/doc/images/teresa_1.png)

5.2 [小比例车辆图聚视图](https://github.com/adoggie/rhinoceros/blob/master/doc/images/teresa_2.png)


![](https://github.com/adoggie/rhinoceros/blob/master/doc/images/teresa_1.png =400x400)

![](https://github.com/adoggie/rhinoceros/blob/master/doc/images/teresa_2.png =400x400)
