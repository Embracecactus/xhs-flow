# 组件核验记录 · 2026-10-10

2026-10-14 技能入口整合：本项目总控与内容模块改为四个维护入口，单篇/多平台发布统一用 `multi-platform-publish`。旧固定上游源码与哈希保留；分类、映射及独立版本库见 [技能库说明](skill-library.md)。新增自维护副本不纳入旧上游哈希表。

2026-10-12 视频分支补充：项目内新增固定版本 video-use 与 jianying-editor-skill，来源、提交与许可见 [Douyin 集成记录](../platforms/douyin/docs/integrations.md)；当前哈希核验共306个文件。Remotion 4.0.534 的同版本包与锁文件位于 `platforms/douyin/`。没有安装所有上游组件，业务脚本不修改固定 Skill。

| 组件 | 固定提交 | 使用范围 | 许可 |
| --- | --- | --- | --- |
| yanhua1010/self-media-content-workflow | cf2526942a9f68ff80e1ac77031cd68d8383ec6c | 总控、简报、策略、热点研究、平台文案、复盘、交付七模块 | MIT，原文见 licenses/self-media-MIT.txt |
| op7418/guizang-social-card-skill | cf4b810fac1c73fb65a2bb31d8c9278d82cbc4c5 | Swiss 种子模板、版式配方、图文检查器 | 根 LICENSE 为 AGPL-3.0；package.json/lock 写 ISC，存在元数据冲突 |

实际下载并读取所用 SKILL.md、相关引用、许可证、npm 清单和安装器源码。原始组件不修改，skills.lock.json 保存逐文件 SHA-256，`python3 scripts/verify_skills.py` 可复核。安装使用系统 skill-installer 的 install-skill-from-github.py，指定 commit 与项目 skills 目录；未运行上游全量安装命令。

图文模板原样保存在 skills；示例 HTML 的修改单独注明，并附完整许可证和可编辑源码。未将 AGPL 文件改标 MIT/ISC。本轮仅本地使用、没有推送或对外提供网络服务；未来分发或服务另核对许可适用条件，不将本记录当成法律意见。

依赖：上游固定锁定 Playwright 1.60.0；本项目相同版本、npm lockfile 带完整性摘要，使用 npm --ignore-scripts 安装。运行上游检查器需同一依赖与匹配 Chromium。上游原模板请求 Google Fonts 和 unpkg/lucide@latest；示例已移除远程加载，使用本机中文字体，渲染器阻断 HTTP/HTTPS。模板内可编辑 HTML 属可信本地代码，导入外来 HTML 前应检查内容和引用，不将其当安全隔离格式。

没有安装 creator-buddy：尚未发现需要第二套能力的缺口。没有安装 content-boom-monitor 或 xiaohongshu-ops-skill；没有配置 Just One API、飞书、OpenClaw profile 或任何账号。未对这两个排除组件进行新一轮运行验证；任务书列出的依赖和许可限制保留为选型边界，不声称其已可运行。

上游冲突已通过项目 AGENTS.md 显式覆盖：版权确认优先于抓图，AI/商业声明由作者落实；演示可先制作，正式确认点保留；本轮已授权质量核查，不重复询问是否检查。

项目 skills 目录用于明确路径调用。当前受管环境的 .agents/.codex 不可写，因此未声称全局自动发现安装成功；后续 Agent 从 AGENTS.md 路由并读取模块即可。新增模块可在下一轮按这些路径使用。

2026-10-13 项目自维护补充：[douyin-web-publish](../skills/douyin-web-publish/SKILL.md) 及 [SOP](douyin-web-publishing.md) 沉淀单篇抖音网页发布与后台核验，包含按需读取的 Windows UIA 参考。该模块是本项目编写的文档，不属于上表固定上游组件，不写入上游哈希清单；没有新增依赖、发布接口或全局安装。真实账号和本次操作证据留在被忽略的 `workspace/douyin/`，不随 Skill 分发。

同日补充 [technical-handdraw-video](../skills/technical-handdraw-video/SKILL.md) 及 [制作 SOP](technical-handdraw-video.md)，复用现有手绘引擎并记录剪映指定配音、横屏4K重排和成片验收。该项目自维护入口未复制或修改上游固定模块；本机 `.local/skills/` 中的 sweety v1.0.0 运行副本及已有字幕/音效适配不随仓库分发，来源和差异见 Skill 的运行参考。没有新增渲染器、声音服务或发布授权。

核验链接：

- https://github.com/yanhua1010/self-media-content-workflow/tree/cf2526942a9f68ff80e1ac77031cd68d8383ec6c
- https://github.com/op7418/guizang-social-card-skill/tree/cf4b810fac1c73fb65a2bb31d8c9278d82cbc4c5
- https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm （已读取第十条用户声明义务；具体平台入口仍需作者在发布时核对）

任务书所述薯管家公告不作为第三方代发的合规授权，本轮没有代发实现，也未将媒体转载等同于已读取平台原文。
