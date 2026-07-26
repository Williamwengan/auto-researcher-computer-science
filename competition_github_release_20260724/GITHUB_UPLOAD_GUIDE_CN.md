# GitHub 上传说明

建议把当前目录 `competition_github_release_20260724/` 作为一个新的 GitHub 仓库根目录上传。

## 上传前检查

在本目录运行：

```bash
find . -type f -size +20M
find . -type f | grep -Ei 'api|key|secret|token|credential'
python -m py_compile focused_workflow/scripts/*.py iad_mvp/scripts/*.py
```

正常情况下，本目录不应包含：

- `Datasets/`
- `.venv/`
- `.git/`
- extra experiment result caches
- MVTec AD 原始图片
- API key 或 `.env` 文件
- 大型 `.npz` 特征缓存

## 初始化仓库

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/competition_github_release_20260724
git init
git add .
git commit -m "Initial competition release"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 推荐 GitHub 仓库描述

```text
Evidence-grounded and repairable AI research workflow based on ResearchArena, with focused idea generation, multi-LLM blind review, claim verification, and IAD execution feedback.
```
