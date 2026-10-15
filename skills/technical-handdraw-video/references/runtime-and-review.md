# 引擎、契约与验收

外部引擎来源：`threerocks/sweety-handdraw-video`，仓库外部依赖清单锁定版本。按库根 README 的安装命令安装引擎，或通过 `HANDDRAW_SKILL_DIR`/本机配置指向已有安装。不要复制旧电脑绝对路径或把当前工作目录当引擎位置。

先读该版本引擎的 `SKILL.md`、依赖说明、runtime-contract 和 quality-gates，确认真实 CLI 和 schema。生产任务放独立工作目录，不能写入技能安装目录。字体、声音、图像来源从当前机器核验，不分发系统字体或私有素材。

常用任务契约包含 design.json、script.md、narration.json、job.json、inputs、work/timeline.json、review.json、outputs；以实际引擎版本为准。图像美术指导与已看图证据绑定图像哈希，准确文字和标注由编辑图层生成。

已有 CLI 的示例（运行前用 `--help` 核对）：

```bash
python "$HANDDRAW_SKILL_DIR/scripts/handdraw_video.py" doctor "$HANDDRAW_JOB_DIR"
python "$HANDDRAW_SKILL_DIR/scripts/handdraw_video.py" build "$HANDDRAW_JOB_DIR"
python "$HANDDRAW_SKILL_DIR/scripts/handdraw_video.py" verify "$HANDDRAW_JOB_DIR" --assets-only
python "$HANDDRAW_SKILL_DIR/scripts/handdraw_video.py" render "$HANDDRAW_JOB_DIR" --preview --start 0 --duration 15
```

两个变量由本机配置/任务提供；预览区间选真实代表段，15秒不是固定门槛。看过代表段后再全片 render、verify；依据观察填写审核，最后 finalize。不要把这些步骤串成无人审查的自动放行。

`doctor` 的离线合成 ready 与语音服务 available 分开：已有准确 WAV 时不需要再次生成旁白。缺声音时不能删音轨门槛。旧版字幕边界、音效开关或片头约束可能需要有证据的运行副本补丁；先核对是否仍存在，保留补丁，不重放历史任务专用脚本。

最终验证：

- 从最终 MP4 全解码检查规格、时长、字体、时序与源指纹。
- 查看每个完成页与代表动作连续帧，检查描线/填色顺序、笔尖归属、裁边和长词/数字。
- 连续播放并记录实际范围；静音播放只证明视觉路径。
- 解码最终音轨，核对源段→混音→有损输出对应、末句、切边、削波、响度与音画长度；AAC 不要求与 WAV 字节一致。
- 每次变更后绑定新哈希。输出含当前视频、封面、字幕、两种稿件、来源及可编辑源；打包白名单防止混入内部日志和旧版本。

引擎 finalize 是工程交付回执，不代表作者确认、平台投稿或公众端可见。
