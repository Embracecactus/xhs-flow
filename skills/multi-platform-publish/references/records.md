# 发布记录契约

计划和结果使用 JSON 对象的 `entries` 数组。一项由 `slug`（或 `content_id`）、`version`、`platform` 唯一标识；平台取 `xiaohongshu`、`wechat_official`、`wechat_channels`、`douyin`、`bilibili`。每项相互独立。

计划：`video_sha256`（或 `asset_sha256`）、`schedule_at`（立即发布为 null，否则含 UTC offset）、标题、正文、标签、封面、目标账号的本地引用。真实账号信息存任务工作区，不进技能库。

结果：相同身份字段、`asset_sha256`、`account_observed`、`scheduled_for`、`stage`、`submit_attempt`、`native_schedule_saved`、`backend_status`、`backend_verified_at`、`public_url`、`evidence`、`next_action`。时间按 ISO 8601 带时区保存，不能只记“18点”。证据用任务目录内相对路径。

`stage` 取 `not_started`、`editing`、`submission_unknown`、`submitted_for_review`、`scheduled`、`backend_published`、`blocked`、`needs_changes`。`native_schedule_saved` 是独立事实：平台审核中时也可能已经保存定时。`backend_published` 不自动产生公开链接。

`submit_attempt` 只计实际最终提交调用。预留计数、按钮定位、计划调用、工具返回均不证明调用完成；用 `attempts` 附加记录 `prepared_at`、`invoked_at`、`tool_result`、`user_verification` 和 `backend_observation`。扫码待办写 `block_reason` 和 `next_action`，保留原有提交记录。工具中断且无法确认调用是否发生时写未知，先查后台。

后台证据至少能对应当前作品和时间；截图不得带扫码图或地址栏令牌。发布管理显示“审核中”就保留原文，不推断已经公开。改期只有读到保存结果才更新台账。没有每天运行的任务时，只能称有限批次原生排期，不能称每日自动运营。

脚本检查的是记录完整性、计划一致性和本地证据路径，不读取平台，也不判断截图是否真实。将新平台 ID 或新字段加入脚本前先明确契约，不能为放行错误删掉检查。
