# Gap Map

- Text2Room/SceneScape/WonderJourney 等生成式方法可扩展场景，但容易缺少可验证的几何一致性。
- DUSt3R/MASt3R、monocular depth、NeRF/3DGS 等重建工具提供几何线索，但不直接保证 scene graph 和物理关系正确。
- 单图 3D 场景生成高度歧义，隐藏区域必须以 hypothesis + uncertainty 形式表达。
- 自动评估 scene plausibility 较难，需要 geometry、relation、collision、uncertainty 多维指标。
