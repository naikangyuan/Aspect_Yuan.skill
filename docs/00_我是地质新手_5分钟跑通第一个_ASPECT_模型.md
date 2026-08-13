# 我是地质新手，如何 5 分钟跑通第一个 ASPECT 模型

## 1. 做一个俯冲模型

不需要先写 `.prm`。直接运行：

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction
```

这会生成：

```text
/tmp/my_subduction/
├── case.prm
├── config.yaml
├── run.sh
├── output/
├── README.md
├── beginner_figure.yaml
└── beginner_report.md
```

如果本机已经有 ASPECT：

```bash
scripts/aspect-yuan beginner subduction --output-dir /tmp/my_subduction --run --aspect-bin /home/yuan/fem3/aspect/build/aspect-release
```

## 2. 看 log 是否正常

```bash
scripts/check_aspect_log.py /tmp/my_subduction/run.log
```

正常情况应该看到 exit status 为 `0`，没有 Exception、NaN、solver failed、parameter not declared。

## 3. 看 statistics

```bash
scripts/parse_aspect_statistics.py /tmp/my_subduction/output/statistics --json
```

先看：

- 时间步有没有增加
- Stokes 迭代是否异常大
- RMS velocity 是否有数量级异常
- statistics 是否为空

## 4. 画第一张图

```bash
scripts/aspect-yuan postprocess scan /tmp/my_subduction/output --json
scripts/aspect-yuan plot /tmp/my_subduction/beginner_figure.yaml
```

俯冲模型默认优先画 composition 图，用来直观看板片和材料分区在哪里。

## 5. 哪些东西不能随便改

不要为了“跑得快”静默改变这些地质含义：

- 模型维度和几何大小
- 边界速度和边界名称
- 俯冲板片位置、倾角、厚度
- compositional fields 的数量和含义
- 黏度、密度和材料分区
- 温度结构
- 重力方向
- 模型时间和输出频率

如果必须简化，要在 `case.prm` 注释或报告里写清楚简化改变了什么地质意义。

