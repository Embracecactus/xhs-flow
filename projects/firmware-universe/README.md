# Firmware Universe

## 后续完整成片入口（2026-10-12）

用户本轮重新要求制作QEMU抖音视频后，已在主视频流程产出[70秒完整审核版](../../workspace/douyin/qemu-without-board/v008/preview.html)与[参考拆解](../../workspace/douyin/qemu-without-board/v008/reference-analysis.md)。使用本目录真实MPS2实验证据并重做原创工程画布动画；本目录以下“仅分镜/未生成视频”保留为当时阶段记录，当前交付以[handoff](../../workspace/douyin/qemu-without-board/handoff.md)为准。无平台发布，作者终稿和试听待确认。

工业科技纪录片＋AI工程助手演示：《没插开发板，固件为什么还能跑？》

## 创作原则

制作定位：导演、技术顾问、制片人。主角是Firmware启动工程链路，不是人物。过程优先于术语，镜头优先于文字，真实工程优先于虚构炫技。禁止真人、卡通人物、动物、小怪兽及动漫叙事。

不制作模板视频、PPT动画、随机AI图片拼接或解释文字墙；不为凑时长降低质量。参考视频只提供制作方法研究，不复制PCB、角色、情节或音轨。

表达边界：不是程序无需硬件，而是宿主计算机上的软件模型承接了部分目标运行环境，使匹配固件的部分逻辑不必等待目标开发板。

## 目录

```text
firmware-universe/
├── README.md
├── references/
│   ├── pcb-analysis.md
│   ├── engineering-reanalysis.md # 当前：工程任务与证据闭环重新分析
│   └── videos/                 # 原参考素材只读；目前不复制视频
├── story/
│   ├── engineering-treatment.md # 当前：真实工程＋AI任务视觉方案
│   ├── visual-treatment.md     # 历史纯链路视觉方案
│   ├── treatment.md            # 历史人物故事，不沿用
│   ├── world.md
│   ├── characters.md
│   ├── storyboard.md
│   └── director-plan.md         # 本次归档的完整导演方案
├── production/
│   ├── director-design/v002/   # 当前：30秒工程对象生命周期分镜，仅文字方案
│   ├── director-design/v001/   # 历史导演设计及v003开场制作记录
│   ├── scenes/                 # 当前engineering-opening及历史场景源
│   ├── assets/
│   │   └── asset-plan.md
│   └── animation/              # 工业CG场景、逐帧渲染与核验
├── engineering/
│   ├── qemu-lab/mps2-an385/v001/ # 当前：已实际运行的Cortex-M3受控实验
│   ├── qemu.md                  # 历史BK7258机制规划
│   ├── boot.md
│   └── validation.md
└── output/
    └── final.mp4               # 目标路径；尚不存在，不创建假成片
```

## 阅读顺序

**最新入口：** [参考片叙事与建模重看](references/process-and-modeling-review-20261012.md) → [30秒开场分镜](production/director-design/v002/opening-storyboard-30s.md)。最新用户要求先重新设计视觉逻辑，不生成视频；以下目录保留此前阶段资料，其中“当前”指当时状态。

1. **当前导演设计：** [Visual Treatment](production/director-design/v001/visual-treatment.md) → [Artifact Flow](production/director-design/v001/artifact-flow.md) → [Shot List](production/director-design/v001/shot-list.md)。12个镜头段围绕同一固件版本谱系，每镜记录对象状态、镜头位置、视觉变化、技术含义、输入与输出；设计阶段未生成视频。上一阶段[工程方案](story/engineering-treatment.md)保留。
2. **当前研究：[参考片重新分析](references/engineering-reanalysis.md)**。重点学习工程对象、AI任务产物、微观定位、干预对照与结果闭环；[旧参考分析](references/pcb-analysis.md)保留，不复制角色、PCB或场景。
3. **当前工程：[Cortex-M3 / MPS2 AN385实验](engineering/qemu-lab/mps2-an385/v001/README.md)** → [问题报告](engineering/qemu-lab/mps2-an385/v001/issue_report.md) → [有限验证报告](engineering/qemu-lab/mps2-an385/v001/validation_report.md) → [镜头工程更新](production/director-design/v001/engineering-update.md)。旧BK7258机制文档保留，不沿用其平台结论。
4. **当前制作：[工业CG开场预览](output/engineering-opening-v003.html)** → [制作与核验](production/director-design/v001/opening-production.md)。12秒/1080p/24fps，真实镜像字节→向量识别→分析报告→模型建立。[历史资产计划](production/assets/asset-plan.md)不作为当前资产清单。

## 当前状态

最新交付是10镜、30秒的文字分镜：同一固件从输入、分析成结构、匹配环境、运行到UART等待，再经源码修订、重建与复位重跑获得有限证据。已从原片重新取样审看叙事和建模，方案采用工程画布、薄层结构与局部状态的连续表达。新方案尚无画面或视觉验收，不继续以材质和运镜打磨v003。旧预览、源码及审核保留；本轮不启动建模或渲染。

此前工程与制作记录：

用户授权选架构开始QEMU工程后，已建立并实际运行原创Cortex-M3诊断：mps2-an385、真实ELF/bin/map/linker、受控UART TX_EN遗漏、修订重建、5次带状态观测运行＋2次无GDB运行。故障版0字节，修订版42字节；报告绑定实际源码、镜像及环境。不是缺门控、BK7258产品固件或实机验收，也不是独立多Agent协作。已保留导演设计并增加工程更新。用户本轮授权开始制作后，已生成本方向原创工业CG开场v003：12秒、1080p、24fps，绑定同一真实bin、ELF派生报告与MPS2模型。已做解码、字节/来源核验、72个实际MP4样本审看和浏览器完整静音播放；正式视觉终审和试听尚未完成，当前review/demo，不是ready_publish或完整片。旧角色样段只保留历史，不作为当前资产或审核通过证据。

既有`references/analysis.md`、`storyboard/director-plan.md`、`assets/asset-plan.md`保留。本目录是本次整理的快照，不自动同步；归档文档中的原工作区路径仍按仓库根目录理解。后续修订应明确更新哪个版本，不覆盖旧审核，不修改旧导出。

参考原片仍在`workspace/douyin/firmware-animation/pcb-example.mp4`，只读，不移动、不复制进Git。所有制作素材、缓存、模型、音频与成片默认不入Git；不自动提交或推送。

**当前交付为30秒开场文字分镜。QEMU受控实验已有有限回归记录，v003保留为历史试作；新版运行、故障及修订镜头尚未制作。**
