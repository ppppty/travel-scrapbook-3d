# 数据与布局

## 输入与输出

参考 assets/trip-source.example.json。根对象含 title、dateLabel（日期未确认可省略）、photos、scenes、unassigned。

photos 是 `{id, source, caption?}` 数组。ID 为唯一字符串，仅允许英文字母、数字、短横线、下划线。source 为绝对路径或相对清单路径。scenes 是 `{id, name, day?, model?, photos:[photoId]}` 数组。场景 ID 唯一，场景内无重复照片；同一照片可以明确属于多个场景。unassigned 是未归类 ID 数组，与场景照片不重叠。所有输入照片必须有归属或被标为未归类。

导入脚本产生 assets/photos/<id>.jpg（最长边默认 2048）、assets/thumbs/<id>.jpg（640）、trip.json、photo-metadata.js。不放大原图。发布清单保留根配置和分组，每张照片替换为 `{id, caption?, src, thumb, width, height, ratio, orientation}`。width、height 是纠正 EXIF 后导出的实际尺寸，ratio = width / height。JS 文件导出 photoMetadata 数组。source 不进入发布清单，JPEG 不携带源图 EXIF/GPS。输入含透明通道时合成白底。其他用户手写配置如有私人信息，分享前按实际内容检查。

EXIF 纠正恢复正确显示方向，不是装饰性旋转。保留用户原文件；新增照片保持旧 ID 稳定。

## 布局

参考 assets/layouts.example.json：根对象含 bounds、border、spreads。

- bounds：页面图片区的 left/right/top/bottom，左右页各自使用同一套局部坐标。
- border：图片框左右各 x、上 top、下 bottom 的额外厚度；没有边框可全填 0。
- spreads：`{scene, items, reserved?}` 数组，同一场景可有多组跨页。
- items：`{id, side, x, z, width}`。side 为 left/right，x 向右，z 向下，x/z 是图片内容中心。内容高度由 width / ratio 推导，边框加在内容外。
- reserved：`{side, x, z, width, height}`，矩形中心与宽高，表示模型或标题的预留占位。

同一场景所有跨页的图片合计须与场景 photos 完全一致，不漏放、不重复。校验基于已导入的 trip.json。预留区域仅检查页内平面占位，斜视角建筑遮挡仍需浏览器检查。示例是结构样例，不是固定美术模板。
