# 工业工程开场｜制作与核验

当前交付：[播放页](../../../output/engineering-opening-v003.html) · [MP4](../../../output/engineering-opening-v003.mp4) · [最新任务状态](../../scenes/engineering-opening/v003/state.json) · [审核](../../scenes/engineering-opening/v003/review.json)。

**12秒、1920×1080、24fps、288帧，H.264/AAC、48kHz。** SHA-256：`37dddda3e8958f29c395a12b111ee7a3ea1602fac8d178e0b1a5da82efc53b1c`。

## 授权与参考

本轮用户要求回到主线、再看参考、开始制作。复看既有参考联系表03、05、07中的对象推进、局部定位和对照段；不声称本轮完整观影或试听。仅学习工程对象持续存在、整体/局部摄影和产物闭环，不导入参考PCB、角色、场景、音乐或品牌。

制作当前导演设计Shot01–03的开场局部，不沿历史角色样段扩片，不宣称整片完成。工程依据是最终MPS2 AN385 session，非BK7258、RTEMS或真实产品。

## 三个落点

1. **唯一输入**：实际故障版bin的400字节，各自一个几何单元；原始顺序、值、文件大小与SHA可核对。字节高度只是视觉编码，不是物理结构。
2. **分析产物**：64字节向量区与4字节.data分类，真实SP/Thumb向量；memory_map.json由对应ELF派生后重新排版。没有为NOBITS的.bss伪造文件字节，也未表现RAM初始化。
3. **环境建立**：Cortex-M3、选定28字节RAM窗口及UART0视图；模型边界和未执行提示明确。8条CPU状态示意槽不代表寄存器总数。目标板卡位位于后方，始终不被虚拟模型填入。

任务名称是单Agent职责视图，不是多个独立Agent运行证明或现场应用截图。全程“受控工程实验 · CG重现 · 非实拍”；CG桌面和外壳也不是实拍。没有展示启动成功、故障、修订结果或实机验收。

## 实际生产与修订

- WSL内准备和核验；复用宿主Blender 5.2.1 LTS＋RTX5060/Cycles/OptiX，32 samples、去噪；原创几何、材质、摄影和动作。
- v001首轮样帧保留；发现Boot任务标识与空板标记重叠、报告裁切、模型刻字遮挡。
- v002重新定位刻字和构图，完整逐帧渲染14秒，旧样帧/源不覆盖。实际MP4审看发现报告与环境出现前有空白等待。
- v003保留v002导出，删除原帧133–156、205–228各1秒：选原帧1–132、157–204、229–336，共288帧。不变速、不倒序、不插帧。重新对齐本段原创合成提示音和边界字幕，后期字幕最后生成。
- Windows临时目录仅此段packed blend与渲染帧，blend和336张帧转存逐项SHA核对；288张编辑选用帧再核对源哈希。未安装新工具、升级驱动、接管浏览器或关闭其他窗口。日志保留Cycles驱动偏旧警告，实际OptiX完成渲染；不宣称驱动无警告。

源：[v002构建](../../scenes/engineering-opening/v002/build.py)、[Blender场景](../../animation/engineering-opening/v002/opening.blend)、[v003剪辑来源](../../animation/engineering-opening/v003/frame-source-manifest.json)、[装配脚本](../../scenes/engineering-opening/v003/finish.py)、[来源和权利](../../scenes/engineering-opening/v003/sources.md)。

## 核验结果与未过门禁

- 来源场景逐帧检查336帧：400个单元和字体值逐项匹配，SP/RESET真实，主体中心在计划覆盖中，空目标位位置不变。此检查不等于所有微字均无视角遮挡。
- 最新12秒MP4完整解码、规格与288帧计数通过；审看72个顺序采样（5张联系表）和关键全尺寸帧。修订消除了主要标记重叠、报告正文裁切及两段长空白。
- 同一镜像身份、向量分类、data识别与报告状态保持；模型另处出现，不把实板空位填满。切点3.5/5.5/7.5秒。
- 隔离headless浏览器正常速度、静音完整播放，媒体错误0，本次丢帧0；不泛化所有播放设备，不等于已试听。
- 原创合成音轨实测**-20.76 LUFS、-8.00 dBTP**；记录的是实际编码输入测量，不是loudnorm假定二次输出目标。无削波；**主观试听尚未完成**。

**正式视觉终审未通过，状态review而非ready_publish。** 字节矩阵有“键盘/矩阵”式外观风险；真实性不能替代参考级美术判断。末镜RAM地址微字仍偏小并受视角遮挡；模型外壳仍简化，不应直接扩成大模块术语介绍片。后续要继续把摄影压到同一固件的真实执行、局部故障及修订对照，不靠解释文字补齐工程过程。

核验：[场景审核](../../animation/engineering-opening/v002/scene-audit.json)、[媒体检查](../../animation/engineering-opening/v003/review/media-check.json)、[浏览器记录](../../animation/engineering-opening/v003/review/browser-playback.json)、[响度](../../animation/engineering-opening/v003/review/audio-check.log)。

未创建final.mp4，未访问实板、发布、提交或推送；旧角色导出、v001样帧和v002的14秒MP4都保留。
