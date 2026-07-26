# IAD MVP 实现前环境检查报告

生成时间：2026-07-11

结论先说：当前环境 **适合做轻量 IAD MVP**，但不适合直接复用 ResearchArena 内部代码，因为 ResearchArena 本身是 agent benchmark harness，不包含 PatchCore/IAD 实验实现。建议新建 `iad_mvp/` 工作流，先做轻量 PatchCore-style baseline + reference consistency agent。

## 1. ResearchArena 项目检查

检查结果：
- `researcharena/` 主要包含 CLI benchmark、pipeline、ideation、review、paper writing 等模块。
- 没有发现可直接复用的 PatchCore、PaDiM、FastFlow、RD4AD、WinCLIP、AnomalyCLIP 实验代码。
- 已有的 IAD 文件主要是我们前面生成的 idea、评分和报告，不是可运行实验代码。

判断：
- 不建议修改 ResearchArena 原 pipeline 来塞实验代码。
- 建议保留 ResearchArena 作为 idea/workflow 生成和评估系统。
- 新增 `iad_mvp/` 作为比赛 MVP 实验与演示工作流。

## 2. Python 环境检查

### 2.1 系统当前 Python
- Python：`/data1/huangyuling/bin/python`
- 版本：Python 3.8.18
- 可用包：`torch`、`torchvision`、`numpy`、`sklearn`、`PIL`、`cv2`、`timm`、`scipy`、`matplotlib`、`pandas`、`skimage`
- 缺失包：`faiss`、`anomalib`

判断：
- 这个环境更适合第一阶段 IAD MVP。
- 缺 `faiss` 不是阻塞，因为第一阶段可以用 `sklearn.neighbors.NearestNeighbors` 做 patch 检索。
- 缺 `anomalib` 也不是阻塞，第一阶段不建议依赖重型库。

### 2.2 ResearchArena `.venv`
- Python：`ResearchArena-main/.venv/bin/python`
- 版本：Python 3.11.14
- 可用包：`torch`、`torchvision`、`numpy`、`PIL`、`scipy`、`matplotlib`、`pandas`、`researcharena`
- 缺失包：`sklearn`、`cv2`、`timm`、`faiss`、`skimage`、`anomalib`

判断：
- `.venv` 适合继续跑 ResearchArena/focused_workflow。
- `.venv` 不适合直接跑 IAD 图像实验，除非额外安装依赖。

## 3. GPU 与磁盘检查

- PyTorch：`2.4.1+cu121`
- CUDA available：`True`
- GPU 数量：6
- GPU 型号：6 张 NVIDIA GeForce RTX 4090
- `/data1` 剩余空间：约 1.5T

判断：
- 计算资源充足，PatchCore-style baseline 和特征缓存完全可行。
- 数据集和输出文件有足够空间存放。

## 4. 数据集检查

当前没有找到可用的 MVTec AD / VisA / BTAD / MPDD 数据集目录。
只发现：
- `/data1/huangyuling/-A_HYL/Grounded-Segment-Anything-main/Grounded-Segment-Anything-main/VISAM`
- 但该目录大小约 `4.0K`，基本是空目录或占位，不是可用 VisA 数据集。

判断：
- 下一步必须准备一个 IAD 数据集。
- 第一阶段最推荐 MVTec AD，因为类别、normal/test/anomaly/mask 结构标准，最适合 PatchCore baseline 和演示。
- 如果短期下载完整 MVTec AD 太慢，也可以先准备 1-3 个类别做 smoke test。

## 5. 是否复用现有 PatchCore 实现

当前没有发现本地可直接复用的 PatchCore 代码。可选方案如下：

| 方案 | 优点 | 缺点 | 建议 |
|---|---|---|---|
| 安装 anomalib 跑 PatchCore | 标准、指标完整 | 安装重、依赖多，比赛前期容易卡环境 | 暂不作为第一选择 |
| 克隆第三方 PatchCore repo | 比自己写快 | 依赖和接口不可控 | 可作为备选 |
| 自写轻量 PatchCore-style baseline | 可控、容易封装、适合比赛演示 | 不一定完全复现论文最优性能 | 推荐第一阶段使用 |

推荐路线：**自写轻量 PatchCore-style baseline**。第一阶段目标不是刷榜，而是证明 agent 工作流有效。

## 6. 推荐最小实现路线

建议新建：
```text
iad_mvp/
  README_CN.md
  data/
    mvtec_split.json
  scripts/
    check_env.py
    prepare_mvtec_subset.py
    run_patchcore_baseline.py
    build_patch_memory.py
    score_reference_consistency.py
    run_reference_consistency_agent.py
    evaluate_iad_agent.py
  outputs/
    patchcore_baseline/
    reference_consistency/
    reports/
    tables/
    figures/
```

第一版只需要实现：
1. 读取 MVTec AD 类别目录。
2. 用 torchvision backbone 提取正常图 patch features。
3. 用 nearest neighbor 计算 test patch anomaly score。
4. 生成 anomaly heatmap 和 image score。
5. 对可疑区域检索 top-k normal reference patch。
6. 输出结构化 JSON report。
7. 计算 baseline vs agent 的小规模指标。

## 7. 当前阻塞项

唯一真实阻塞：**缺 IAD 数据集路径**。

需要用户确认或准备：
- MVTec AD 数据集是否已经在别的目录？如果有，提供路径。
- 如果没有，需要下载 MVTec AD，或先放入 1-3 个类别做 smoke test。

## 8. 下一步建议

下一步不建议继续写最终设计文档，而是先搭 `iad_mvp/` 最小工程骨架。
我建议下一步做：
1. 创建 `iad_mvp/` 目录和 README。
2. 写 `scripts/check_env.py`，固定以后每次运行前检查依赖/GPU/数据路径。
3. 写 `scripts/prepare_mvtec_subset.py`，先要求用户传入 MVTec 根目录。
4. 等数据路径确认后，再写并跑 `run_patchcore_baseline.py`。

这样做的好处是：即使现在没有数据，也能先把比赛工程结构搭起来；等 MVTec 数据一到，就可以直接进入 baseline 运行。
