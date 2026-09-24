# EDA 芯片电路设计 skill

输入芯片型号和设计目标，获取可追溯的引脚说明、原厂典型电路、目标连接表、外围器件初选、计算、BOM 与验证清单。

## 使用

在 Codex 新会话中输入：

```text
/eda-chip-circuit-design-skill
芯片 TPS62130A，QFN-16；输入 9–17 V，输出 3.3 V/2 A。
请给出引脚表、原厂典型电路、目标电路、L/C/R 选型、BOM 和 EasyEDA 连接表。
```

只想查资料时写“只解释引脚和原厂典型电路”。已有图纸时附上原理图、BOM 或网表，并写“审查”。

## 安装到 Codex

将本目录复制到用户 skills 目录：

```powershell
Copy-Item -Recurse -Force . "$env:USERPROFILE\.agents\skills\eda-chip-circuit-design-skill"
```

然后在新会话中使用 `/eda-chip-circuit-design-skill`。本工作区同时提供同名 `.skill` 压缩包，便于备份或迁移。

## 使用边界

本 skill 会使用制造商原始资料作为主要证据。公式和脚本用于首轮估算，不能代替该芯片的稳定性矩阵、布局指南、仿真和实测。缺少完整料号、封装、关键指标或可靠数据手册时，将明确列出缺口，不给出伪确定的数值。

## 文件

- `SKILL.md`：触发条件和主流程。
- `references/`：资料检索、拓扑核查、交付模板和 EDA 协作。
- `scripts/power_calcs.py`：Buck/Boost/反馈分压初算，无外部 Python 依赖。
- `evals/evals.json`：源码目录中的回归场景；`.skill` 分发包按打包规范省略测试数据。

脚本示例：

```powershell
python scripts/power_calcs.py buck --vin 12 --vout 3.3 --iout 2 --fs 2500000 --ripple-fraction 0.3 --output-ripple 0.03 --efficiency 0.9
python scripts/power_calcs.py divider --vout 3.3 --vref 0.8 --rbot 100000 --min-current 0.000002
```

## 许可证

本项目采用 [MIT License](LICENSE)。

