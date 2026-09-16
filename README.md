# FHD Algorithm 3 论文与数值实验

用于协作修订 Rosensweig 铁磁流体模型论文，包含论文 TeX、一阶/二阶数值实验、收敛图和对应数据。
仓库目前为公开；公开访问不等于授予开源许可证，本仓库尚未设置许可证。

## 目录

```text
main.tex                         论文主文件
sections/
  first_order_experiments.tex     一阶实验与共同算例设置
  second_order_experiments.tex    二阶实验
figures/                         两阶收敛图：PDF、SVG、PNG
data/
  results.csv                    8组主误差及42个观测收敛阶
  results.json                   同一数据的结构化版本
  provenance.json                数据与来源校验信息
previews/
  manuscript.pdf                 完整论文编译预览
  numerical_experiments.pdf       仅数值实验的编译预览
Makefile                         本地编译命令
```

## 协作方式

- 修改实验文字、表格和图注：编辑 `sections/` 中对应文件。`main.tex` 通过 `\input` 引用它们，不应再复制一份有效正文。
- 修改理论推导：编辑 `main.tex`。**本次上传只整合了数值实验，之前讨论的理论公式修订没有在本轮同步。** 协作者需要在后续修订中保持理论稿与实验对象一致。
- 图片引用采用相对路径 `figures/`。PDF用于论文排版，SVG用于矢量编辑，PNG用于快速查看。
- 生成的 `.aux`、`.log` 等中间文件放在 `build/`，不提交。修改 TeX 后应重新编译；`previews/` 是已编译快照，不会自行更新。
- 正文原有的 `eq:H-dis-f-1` 重复标签警告仍保留，属于待处理的理论稿排版问题，不是本次数值实验片段产生的新标签。

## 编译

需要 TeX Live 或 MacTeX，以及 `latexmk`。从仓库根目录执行：

```bash
make pdf
```

输出为 `build/main.pdf`。检查排版后运行 `make preview` 可更新 `previews/manuscript.pdf`。
也可以将整个仓库上传到 Overleaf，以 `main.tex` 为主文件并使用 pdfLaTeX 编译。

## 实验口径

- 三维单位立方体；同一 `balanced-linear-weak-coupling` 制造解。
- 一阶、二阶均有 K=4、8、16、32，T=2，dt=1/K，终点数据均已完成计算。
- 横轴为从左到右增加的 K=4、8、16、32，参考线为 K^{-1} 和 K^{-2}。
- 主指标：u完整H1、修正压力L2、omega完整H1、m-H(div)、k-L2、phi-H1、H-H(curl)，另报curl(H)的采样绝对最大值。
- 二阶压力参考为精确修正压力的端点平均；修正压力为去均值的 p-mu0*m.H/2。
- 二阶k-L2仍约一阶，未声称所有变量二阶收敛。dt与网格同时变化，结果不是独立的纯时间精度验证。
- 本轮没有加入能量稳定性实验、纯时间二阶试验或性能加速结论。

![一阶误差收敛](figures/first_order_errors.png)

![二阶误差收敛](figures/second_order_errors.png)

本仓库仅含论文协作材料，不包含SSH密钥、服务器登录资料、计算日志或完整有限元求解器。
