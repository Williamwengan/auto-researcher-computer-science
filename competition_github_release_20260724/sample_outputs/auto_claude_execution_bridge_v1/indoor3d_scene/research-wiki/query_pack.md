# Query Pack

Problem: 从单张室内 RGB 图像推断 room layout、visible objects、occluded hypotheses、3D positions、geometry proxies、relations、materials/textures 和 renderable 3D scene representation。

Idea: Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。

Evidence:
- v0.7 indoor3d evidence-card repair 后：papers 18，claims 18，pass rate 1.0。
- 证据库覆盖 Text2Room、SceneScape、WonderJourney、DUSt3R、MASt3R、3D Gaussian Splatting、NeRF、HorizonNet、MiDaS、3D-FRONT、Matterport3D、ScanNet、Structured3D、Hypersim。
- 注意：该方向使用 seeded evidence bank，最终材料必须透明披露。
