# 薯流 · XHS Flow

单账号、图文优先的本地内容工作流：来源 → 选题 → 原创文案 → HTML 图文 → 作者审核 → 人工发布包 → 真实数据 → 复盘。

Agent 和项目主流程运行在用户现有 **WSL2**，沿用现有 Linux 依赖；允许必要时调用宿主 Windows 的 PowerShell、Chrome/Edge、UI Automation 或已有桌面/浏览器连接工具。优先复用可用会话，不另建 Windows 原生项目，不迁移 Agent，不新增跨平台框架或多系统 CI。宿主调用遵守正常审批及单篇授权边界，详见 [项目规则](AGENTS.md)。

**本地制作、版本管理与测试数据复盘已跑通；每篇确认、授权及发布进度以被 Git 忽略的工作区记录为准。** 本地脚本没有账号操作接口；已有单篇授权不扩大到其他内容、互动、付费或调度。

## 直接查看

- [本轮 WSL2 审核包：正文、六张图、手机预览和源文件](xhs-workspace/wsl2-review.html)
- [WSL2 恢复路径与实际浏览器验收](docs/wsl2-acceptance.md)
- [指标计算结果](xhs-workspace/metrics/test/7d70fe6f0d80965c/calculations.md) / [待分析模板](xhs-workspace/metrics/test/7d70fe6f0d80965c/review-template.md) / [Agent 证据核对：资料不足，待分析](xhs-workspace/reviews/test/wsl2-evidence-review.md)
- [六页演示手机预览（质量修订版）](xhs-workspace/posts/demo-source-notes/publish/v002/preview.html)
- [整组预览图](xhs-workspace/posts/demo-source-notes/publish/v002/contact-sheet.png)
- [演示正文](xhs-workspace/posts/demo-source-notes/copy.md) / [来源](xhs-workspace/posts/demo-source-notes/sources.md) / [可编辑 HTML](xhs-workspace/posts/demo-source-notes/editable/index.html)
- [历史测试草稿（保留原文；其中固定解释和实验不作为有效分析）](xhs-workspace/reviews/test/7d70fe6f0d80965c.md)
- [实际验收与未完成项](docs/acceptance.md)

整个 xhs-workspace 默认被 Git 忽略。上面的运行产物存在于当前本机，不会随 clone 出现；可用下面命令从公开演示源重建。examples 仅含公开资料与测试数据。

## 运行

```bash
# 当前 WSL2 依赖已可用，下两行仅在依赖丢失时用于恢复：
npm ci --ignore-scripts --no-audit --no-fund
# 本机已配置可用浏览器；新机器需要安装：
PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npx playwright install chromium
python3 scripts/demo.py
python3 scripts/xhs.py render demo-source-notes --note '演示初稿'
python3 scripts/xhs.py metrics examples/metrics-test.csv --kind test
```

首次重建输出 v001；每次修改后导出新版本，源文件未变则复用已有版本。不要为追齐本机版本号反复生成。工作流由 Agent 使用 Skills 完成研究与写作，脚本不自行搜热点或凭空生产文章。

## 使用与检查

- [操作手册](docs/workflow.md)：账号信息、确认点、制作、修改、手工发布、数据字段和恢复方法。
- [WSL2 图文上传与发布流程](docs/ui-publishing.md)：目标窗口接通、顺序上传、正文回读、原创/AI 声明、合集、单次提交、后台核验及故障恢复。
- [组件与许可](docs/components.md)：七个 self-media 模块和一套 guizang 图文组件，固定提交及逐文件哈希。
- [项目 Agent 规则](AGENTS.md)：直接读取项目内 Skill，保留确认点与权限边界。

```bash
python3 scripts/verify_skills.py
python3 -m unittest discover -s tests -v
python3 tests/render_acceptance.py
node scripts/validate.mjs xhs-workspace/posts/demo-source-notes/editable/index.html
```

渲染验收需要可运行的本地浏览器，受管沙箱可能需要工具审批。上游检查当前为 0 失败、6 警告，详见验收记录；机器检查不代替作者真实性判断。

本轮 23 项回归及实际 WSL2 浏览器导出通过；导出后中断能恢复状态，导入后中断能补齐报告且保留批注。指标脚本不再预填原因与实验，资料不足时明确待分析。尚未收到作者真实修改意见，审核包等待该输入；技术自测不算反馈验收。

新增付费依赖为零；已有模型额度、设备、电力与人工成本未计量。没有增长承诺、全托管运营或平台合规保证。
