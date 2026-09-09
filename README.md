# 3D 旅行手账 · Travel Scrapbook 3D

把旅行照片变成一本可以打开、翻页、旋转的立体手账。

一个供 Codex 使用的 skill：从照片整理、场景排版、立体地标到网站展示视频，复用经过实际项目调整的设计与实现方法。默认莫奈花园与少女风装帧，也可以换成适合自己旅行的风格。

## 可以做什么

- 按行程整理照片，保留横竖方向与长宽比，完整放入对应景点的实体页面。
- 按照片数量设计不同跨页，交替照片与模型的位置。
- 制作默认合上的 3D 手账，支持开合、翻页、旋转、照片放大和地标展开。
- 处理照片重叠频闪、动画冲突，以及书本过小或上下截断的问题。
- 按需录制真实网站的展示视频，默认无音乐、无旁白。

这是给 AI 助手使用的工作流程和辅助工具，**不是双击就能运行的成品网站模板**。仓库不含个人照片、原项目的网站或展示视频。使用时提供自己的照片、行程和偏好。

## 安装到 Codex

将此仓库地址交给 Codex：

```text
帮我安装这个 skill：https://github.com/ppppty/travel-scrapbook-3d
```

也可以手动下载仓库 ZIP，解压后将文件夹命名为 `travel-scrapbook-3d`，放到：

- Windows：`%USERPROFILE%\.codex\skills\travel-scrapbook-3d`
- macOS / Linux：`~/.codex/skills/travel-scrapbook-3d`
- 自定义了 CODEX_HOME 时：`$CODEX_HOME/skills/travel-scrapbook-3d`

确保 `SKILL.md` 直接位于该文件夹内，没有多套一层目录。已有同名技能时先保留旧版本。安装后开启新对话；如果没有识别到，重启 Codex 再试。

## 使用示例

```text
使用 $travel-scrapbook-3d，把我提供的旅行照片做成莫奈少女风的 3D 手账。
默认合上，每个景点的照片全部放进去，保持照片原比例。
```

```text
使用 $travel-scrapbook-3d，改进这个已有手账网站。
每页排版更有变化，翻页更流畅，旋转时上下不要被截断。
```

```text
使用 $travel-scrapbook-3d，给这个手账网站录一段约 40 秒的展示视频。
不要音乐和旁白，展示封面开合、旋转、翻页和照片放大。
```

新建时提供照片目录或附件，以及景点分组；不能确定地点的照片可以先保留为未归类。日期、标题、是否包含餐饮、审美和视频画幅都可以调整。

## 文件与工具

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 技能入口与任务流程 |
| [视觉与交互](references/design-and-interactions.md) | 排版、色彩、交互和动效建议 |
| [3D 实现与取景](references/three-implementation.md) | 场景组织、稳定性和相机拟合 |
| [视频展示](references/video-showcase.md) | 本地实录、画幅、静音 MP4 与验收 |
| [数据约定](references/data-contract.md) | 照片清单与布局格式 |
| [import_photos.py](scripts/import_photos.py) | EXIF 方向纠正、缩略图与发布清单 |
| [validate_layout.py](scripts/validate_layout.py) | 漏图、重复、出界、重叠与预留区域检查 |
| [framing.mjs](assets/framing.mjs) | 考虑物体深度的透视取景函数 |

照片导入工具依赖 Python 与 Pillow；布局检查只需要 Python 标准库。网站的渲染依赖随具体工程配置；视频导出按需使用浏览器录制能力与 FFmpeg。无需在安装 skill 时一次装齐所有工具。

在本仓库目录运行工具的示例：

```sh
python -m pip install -r requirements.txt
python scripts/import_photos.py --manifest /path/to/trip-source.json --out /path/to/site
python scripts/validate_layout.py --trip /path/to/site/trip.json --layouts /path/to/layouts.json
```

输入清单参见 [照片示例](assets/trip-source.example.json) 和 [布局示例](assets/layouts.example.json)。示例中的图片路径需要换成自己的真实文件。

## 已验证的辅助行为

照片导入验证了 EXIF 方向、原比例缩放、缩略图、源文件保留、EXIF 移除和覆盖保护；排版检查验证了漏图、重复、碰撞、出界、预留区和同场景多跨页。取景函数通过了 400 组视口与旋转角度的投影检查。

具体生成的网站仍需在实际浏览器中验收，尤其是照片数量、斜视角遮挡与动画流畅度。技能默认本地处理照片；录制视频不会自动上传或代发社交平台。
