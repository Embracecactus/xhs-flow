# Creator Flow

Creator Flow 是一个本地优先的多平台内容工作区，覆盖选题、写作、图文、短视频、技术手绘、审核、经授权网页发布和数据复盘。项目主体运行在 WSL2，按需复用宿主 Windows 的浏览器、PowerShell、UI Automation 与剪映；不维护第二套 Windows 工程，也不提供无人值守账号运营或平台私有接口。

## 目录

| 路径 | 内容 |
| --- | --- |
| [`platforms/xiaohongshu/`](platforms/xiaohongshu/README.md) | 小红书图文生产、公开演示与测试 |
| [`platforms/douyin/`](platforms/douyin/README.md) | 抖音/头条短视频本地生产引擎与测试 |
| `workspace/` | 本机账号、素材、版本、成片和发布证据；整体忽略 Git |
| [`projects/firmware-universe/`](projects/firmware-universe/README.md) | Firmware Universe 专题工程与可审阅资料 |
| [`skills/`](skills/) | 内容策略、创作、分析、技术视频和多平台发布 Skill |
| [`docs/`](docs/) | 跨平台组件、技能库、手绘视频与发布规范 |
| [`AGENTS.md`](AGENTS.md) | 所有 Agent 必须遵守的结构、权限和验收边界 |

平台源码、私有生产数据和独立专题严格分离。不要在根目录新增临时素材、分镜、引用或平台文件夹；完整规则以 [`AGENTS.md`](AGENTS.md) 为准。

## 当前能力与边界

- 小红书图文链路已有 23 项文件工作流回归；真实账号与发布状态以 `workspace/xiaohongshu/` 的最新记录为准。
- 抖音本地流程支持 Remotion、FFmpeg 与剪映草稿衔接；任务统一位于 `workspace/douyin/`，本地生产状态不等于平台发布。
- 技术手绘与多平台发布通过项目 Skill 路由；发布只在用户对具体篇目、版本、账号、平台与时间明确授权后使用官方网页/UI。
- `projects/firmware-universe/` 保留 QEMU 受控实验、导演设计和历史试作；30 秒新版目前仍是文字分镜，不冒充已生成视频或视觉验收。

## 基础检查

从仓库根目录执行：

```bash
python3 scripts/verify_skills.py
python3 -m unittest discover -s platforms/xiaohongshu/tests -v
python3 -m unittest discover -s platforms/douyin/tests -v
```

渲染、完整视频审核、浏览器发布和平台后台回读各有独立证据边界；机器检查不能替代作者终审、主观试听或公开发布确认。
