# 零外场能量耗散数据

本目录记录一阶、二阶各三个算例，不是制造解误差数据。

- `curves.csv`：六条曲线的全部 118 行时间层记录，包括各算例的初始行。
- `energy_summary.csv/json`：终点能量、平衡残差、方程残差及计算资源汇总。
- `provenance.json`：文件校验和、可公开的运行设置及来源摘要；不包含登录信息或机器目录。
- 绘图命令：在仓库根目录运行 `python3 scripts/plot_energy.py`。

## 口径

- 单位立方体，K=8，T=0.5，dt=1/16、1/32、1/64，分别运行8、16、32步。
- 物理参数均为1；外加磁场、制造源和边界能量输入均为0。
- 初值只取已有平滑制造解在t=0的u/omega/m形状，再施加离散约束；phi0由零外场磁静力问题重算。
- 一阶使用其生产空间order=1，二阶使用其生产空间order=2，因此不是相同空间上的时间精度对照。
- `energy`：原生有限元场上积分得到的总离散能量。
- `energy_normalized`：同一算例的E(t)/E(0)，不是误差。
- `dissipation`：一阶端点或二阶中点的离散耗散率。
- `numerical_dissipation`：一阶的额外非负步增量项；二阶为0。
- `balance_residual`：E_n-E_(n-1)+dt*dissipation+numerical_dissipation。
- `balance_residual_scaled`：除以max(E_n,E_(n-1),dt*dissipation+numerical_dissipation,1e-14*E0)。
- `cumulative_balance_scaled`：累计能量平衡缺口除以E0。
- 第0行的耗散和残差为起始占位，不能解释为初态瞬时耗散率为0。
- `monolithic_difference`：正式K8算例未做单体对照，此列的0是未执行占位；真正的单体对照在K4预检中完成，指标见provenance.json。
- `full_relative_residual`包含该步存档的线性求解残差；二阶首步还包含重新装配的非线性方程残差。
- 资源汇总的RSS是每5秒采样的聚合值，不是逐瞬时精确峰值。

绘图使用原始计算点，不做平滑、拟合或数据删选。二阶大步长的较慢后期衰减如实保留。
原始完整日志、最终字段和求解器源码另行留档，不包含在本论文仓库中。
