# 首条横屏测试视频交付

核验时间：2026-10-12。选题为《没插开发板，固件为什么也能跑？》，来自作者知识库选题线索及公开的 qemu-bk7258 项目。本片是标记清楚的演示测试作品；没有作者终稿确认或发布授权。

当前版本：[v002 预览](../../../workspace/douyin/qemu-without-board/v002/preview.html)、[成片](../../../workspace/douyin/qemu-without-board/v002/final.mp4)、[发布包](../../../workspace/douyin/qemu-without-board/publish-v002.zip)。v001 和此前工业相机测试保留，不覆盖旧导出。

## 实际生产结果

| 项目 | 已核验结果 |
| --- | --- |
| 成片 | 60.000 秒，1920×1080，30fps，H.264/yuv420p，AAC |
| 内容结构 | 8 个连续镜头，18 条字幕；CPU→内存→MMIO→UART/定时器→模型边界→实机验收 |
| 画面 | 原创 SVG/React 动画；同一芯片对象贯穿，因果动作与旁白对应，4 类以上构图 |
| 自动 QA | 9 项通过；35 个实际成片抽帧，字幕越界检测为零，最高 5.77 字/秒 |
| 音频 | 本机系统合成配音；实测 -17.24 LUFS，真峰值 -1.49 dBTP；未裁切旁白，边界淡化 |
| 实质审核 | Agent 已查看实际联系表、全尺寸封面及关键帧，核对技术来源和事实边界 |
| 剪映 SDK | 60 秒草稿，8 个视频片段、1 条独立音轨、18 个可编辑字幕片段 |
| Windows 导入 | 当前 v002 已导入剪映草稿目录，素材哈希一致；原有 161 个草稿索引条目保留 |
| 交付文件 | script.md、shotlist.yaml、subtitle.srt、thumbnail.png、project/、final.mp4、publish.json 均存在且哈希固定 |
| 状态与权限 | ready_publish、demo=true；author_confirmed=false、publish_authorized=false、publication=null |

成片 SHA-256：`be301d59551ff7f108c2e408feeba15e91fd3b809714eb29d3c58388b0d86bde`。发布包哈希见项目根目录的 `package-v002.json`；包内含工程、素材、质量记录、实质审核、预览与来源，排除私人剪映索引备份。输出哈希逐项与 ZIP 内容核对，压缩完整性检查通过。

## 实现与回归验证

- Douyin 状态、来源、版本保护、完整词切点、审核哈希失效、断点恢复与打包边界：11 项测试通过。
- 原有 XHS 工作流回归：23 项测试通过。
- 两个项目固定版本技能的 306 个文件哈希核验通过；没有修改上游技能文件。
- A 真人口播和 C 实拍剪辑的路径分别完成 6 秒横屏合成素材集成测试，时长、格式、字幕与音频检查通过，来源哈希保留在 [media-acceptance.json](media-acceptance.json)。这是合成色条和正弦音 fixture，不证明真人内容、对白识别或真实实拍审核。

## 验证边界

本片由当前 Agent 编写，用 Remotion/FFmpeg 实际渲染；没有调用 Opus 5.5。视觉方法和选题研究见 [opus55-research.md](opus55-research.md)。动画为原理解释，未以本轮实际固件运行、示意波形或旧 CI 代替整芯片和物理验收。

剪映 11.5.0.14471 的应用打开与应用内导出未验证；成片是已核验的 Remotion/FFmpeg 导出。Windows 导入证据不证明应用兼容性。官方剪映 Agent CLI 的只读尝试返回运行时令牌必需，未读取或绕过凭据。

音频机器测量不证明实际听感；作者正常速度试听、标题与风格确认、正式终稿确认仍待完成。本阶段没有平台上传、提交审核或发布操作。
