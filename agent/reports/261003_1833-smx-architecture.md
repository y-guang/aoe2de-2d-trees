# SMX 树木素材编辑与生成指南

2026-10-03。完整说明与可运行实现：[SMX architecture notebook](261003_1833-smx-architecture.ipynb)。

## 使用方式

- 在 notebook 第一段代码修改全局常量 MOD_ROOT，默认直接引用 reference/22014_Anne_HK - Identical Pine Trees with Grid Shadow。从项目根目录或 reports 目录启动均可。调色板另从 reference/SMX-Workshop/palettes 读取。
- 使用项目 .venv 的 Jupyter Python kernel。核心解析只需标准库；预览用项目已有 NumPy/Matplotlib。21 个单元格已完整运行并通过 nbformat 验证，测试 Python 3.14.4。
- 精确复现：model = parse_smx(raw)，然后 rebuild(model)，应与 raw 逐字节一致。模型保留命令分段、未知字段、memo、声明大小与全部打包槽。
- 编辑生成：修改 model 中图层 rows，调用 rebuild(canonical_model(model))。该路径从像素重新生成边界和命令，并更新实际长度；保证像素和锚点，字节可能不同。示例只在内存修改像素，reference 不变。
- 此实现覆盖目标目录，并非所有 SMX 变体的通用工具。游戏内兼容性另行验证。

## 字节实现要点

- little-endian；文件头 32、帧头 6、层头 16 字节。帧与层顺序存储，没有偏移表；层顺序 main → shadow → outline。
- flags 掩码：1 主图、2 阴影、4 轮廓、8 使用 8to5。不要照抄 openage 文档的位号表。0x10 语义在样本中未验证。
- 行边界 (65535,65535) 是全透明行，不消费命令或 EOL。普通行从 left 到 width−right。透明用 None，像素索引/阴影强度 0 仍可存在。
- 命令低两位：0 skip、1 draw、2 玩家色 draw（阴影/轮廓按 draw）、3 EOL；非 EOL 长度=(byte>>2)+1，最多 64。
- 主图的命令流和像素流分开；阴影是命令加内联强度值；轮廓 draw 无像素值。主图槽连续跨行，不能在 EOL 重置。
- 4plus1 五字节保存四个 10-bit 索引；第五字节 bits 0–1 对应第一个像素、2–3 第二个，依次递增。末块和多余槽必须保留才能字节复现。
- 8to5 五字节保存两个索引及两个 10-bit smudge 值。保留原 10 位，不使用预览灰度代替；详见 notebook 中成对 pack/unpack。
- 层声明 payload 大小不是可靠跳转依据；按高度、命令长度、像素流长度解析，检查 EOF 和每字节覆盖。unknown uint32 保留，即使目前全零。
- 各层锚点独立：像素映射到 (x−hotspot_x,y−hotspot_y)。变更尺寸时更新锚点并检视阴影对齐。RGBA 色表属于外部资源；JASC-PAL 可能有 alpha。

## 实测与有意留空素材

全部 **110 文件、20,229,293 字节、1,914 帧、3,802 层**通过完整解析与逐字节重建；全部也通过从像素重新生成、再解析后的像素/锚点比较。主图 1,914、阴影 1,879、轮廓 9（全部 0×0）。flags=1/3/7，palette=20/28/30，version=2，unknown=0。

树桩由用户确认是故意留空以在游戏中屏蔽，**不要补画或修复**。三个 x1 文件 stump_bamboo、stump_baobab、stump_generic 各 3 帧、1,409 字节，有陈旧长度元数据及空主图的额外零像素块；只保留并验证占位字节结构。

其余 107 文件的全局 uncompressed 是 frame.smp_size 总和；Workshop writer 的约定另加 4×帧数。原字节复现保留来源值，生成采用 notebook 中明确的 Workshop 约定。

真实样本全部 4plus1，无玩家色、8to5、非空轮廓。后三者通过合成样本测试，不能声称已验证游戏渲染。

## 资源与交付规则

主要依据：[本地 SpriteIO.java](../../reference/SMX-Workshop/src/com/imwg/smxworkshop/sprite/SpriteIO.java)，checkout ea461434f67fd8a421bedc4e383eefc5d1b5ba24；从 [reference.md](../../reference/reference.md) 入手。交叉参考 [openage SMX](https://github.com/SFTtech/openage/blob/master/doc/media/smx-files.md) 与 [SMX-Workshop](https://github.com/ImWG/SMX-Workshop)。sld-extractor 是另一种格式的工具。

一次性探索及验证脚本位于 tmp，已加入 gitignore，不作为 notebook 依赖。导出写 tmp 或新 mod 目录；reference 只读，不复制其 SMX、调色板或派生 PNG 到 git。notebook 的运行时预览单元格标记 transient_asset_output，交付已清除图像输出，仅保留结构清单及验证结果。重新运行后提交前再次清除素材输出。
