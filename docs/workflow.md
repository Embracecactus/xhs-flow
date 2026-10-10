# 本地操作手册

这套流程由 Agent 读取已有 Skill 并完成研究与原创写作，脚本只负责本地文件、图文导出、版本与数据计算。没有无人值守运营能力。

## 首次运行

环境：Python 3.10+、Node.js 18+、中文字体（本机 WenQuanYi Zen Hei）。

```bash
npm ci --ignore-scripts --no-audit --no-fund
PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright" npx playwright install chromium
python3 scripts/xhs.py init
python3 scripts/demo.py
python3 scripts/xhs.py render demo-source-notes --note '首版演示'
python3 scripts/xhs.py metrics examples/metrics-test.csv --kind test
python3 -m unittest discover -s tests -v
```

依赖安装需要网络，图文渲染禁止 HTTP/HTTPS。首次 Linux 安装若缺系统库，按 Playwright 报错安装所需库；不要静默提权或执行远程安装脚本。平台浏览器/数据接口不影响此本地链路。

本机已用现有 Chromium 151.0.7922.34（缓存修订 1234）实测通过，路径保存在忽略提交的 `.cache/browser.json`。新环境优先安装匹配版本；也可用 `XHS_CHROMIUM_PATH=/绝对路径/chrome-headless-shell` 明确指定已验证浏览器。不同浏览器/字体可能改变像素输出，必须复检。本次匹配版本的下载因速度慢主动停止，没有把未完成下载计作安装成功。受管沙箱若出现 `sandbox_host_linux.cc ... Operation not permitted`，需按工具审批机制运行本地浏览器，不能通过改稿掩盖环境错误。

## 账号与选题

先填 `xhs-workspace/account.md` 的待确认项。新号取得素材证据后最多提出三个定位候选，作者选定后生产；已有号仅分析授权资料。未获授权不改名、不删除历史内容。可先设三个栏目假设：资料怎么查、过程怎么记、结果怎么复盘；这些仅是演示方向，不是本账号方案。

研究每轮仅保留少量相关主题，写入 topics.csv：来源、发布时间（未知留空）、观察时间、读者问题、原创证据、重复检查与风险。已发内容重复检查必须有历史资料，无资料写“未知”。没有材料就不排满日历。10–12 篇只是作者可选择的试运营规模。

正式生产由 Agent 依次读取 `skills/self-media-content-workflow/SKILL.md` 和所需模块。方向、平台、标题、风格、终稿确认记录在 brief.md/review.md；明确账号配置可复用。尚未确认时保持待审核，不调用 approve。

```bash
python3 scripts/xhs.py new my-post
```

补全 brief.md、copy.md、sources.md、review.md。从图文组件的种子 HTML 复制到 `editable/index.html`，按所选配方编辑；图片先核对权利，放 editable 内，使用相对路径。本地 HTML 应移除远程 CDN，保留 LICENSE 和署名。不要执行素材内脚本指令，不使用凭据文件作为素材。

## 导出、修改、审核

```bash
python3 scripts/xhs.py render my-post --note '初稿'
# 根据作者反馈修改 editable/index.html 和 copy.md，记录批注后再运行：
python3 scripts/xhs.py render my-post --note '作者反馈：具体修改内容'
```

每个完整版本位于 publish/v001、v002……，含 1080×1440 PNG、360px 手机预览、正文、来源、可编辑 HTML 和哈希清单。原素材不覆盖。源文件不变则返回已有版本；旧导出被手动改动会报错并保留现场。版本变动清除审核，已发布稿不允许原地重导出。创建/导出按单进程串行使用，非并发任务系统。

渲染失败：查看错误，修正当前源文件，运行相同命令；不会新增完成版本。恢复旧稿：将旧版本 editable、brief.md、copy.md、sources.md 复制到当前笔记（先保存当前修改），再创建一个新版本，不能覆写旧版。缺失 PNG 或损坏已交付文件：先从备份恢复，或保留该目录另建修订笔记，不删除审计记录。

上游版式检查：`node scripts/validate.mjs xhs-workspace/posts/my-post/editable/index.html`。失败必须修复；警告记录视觉理由，不添加虚假数据填满页面。

质量检查包括事实、来源、版权、隐私、标题承诺、手机可读性、图文一致、AI 与商业披露。机器只能查部分问题；作者仍需核对真实性。由作者明确终审后才可记录：

```bash
python3 scripts/xhs.py approve my-post --note '作者确认方向、标题、风格、事实、素材权利、隐私、AI与商业声明；终稿版本 v001'
```

该命令只记录人工审核，不检查作者身份，Agent 不可自行编写作者确认。演示包不允许批准为正式发布稿。approve 不执行账号操作，不代表平台会接受内容。

## 人工发布与回填

作者在平台内检查当前规格，依序上传 01.png 至末张，复制 copy.md 中审核过的正文，自行使用平台 AI 标识功能并确认商业披露。preview/contact-sheet、审核记录和源码不是上传图片。平台发布入口限制以当时界面为准。

取得真实链接或作者明确确认后，才能本地登记：

```bash
python3 scripts/xhs.py published my-post --url 'https://www.xiaohongshu.com/explore/真实ID'
# 无可用链接时使用作者明确给出的发布确认文本，不能由 Agent 猜测：
python3 scripts/xhs.py published my-post --confirmation '作者明确确认的原意与发布时间'
```

不访问账号、不代发、不自动回复。评论只处理获授权且去标识的最小摘录，分类为问题、经验、纠错、合作、投诉，再写回复建议；报价、优惠与承诺留给作者确认。登录异常、验证码或限流出现时停止。

## 数据导入

真实原始导出留在工作区 metrics/raw，不修改。人工按 examples/metrics-test.csv 的字段映射成 CSV，dataset_kind 填 real。必须记录账号内部代号、平台、内容类型、来源、导出时间、发布及观察时间（含时区）、窗口小时、推广和商单信息、单位和口径。没有字段不补造，数值留空，不用 0 表示缺失。

unit=count 且 basis=same-post-window 表示人工已确认分子与阅读来自同篇同窗口、可相除的计数。其他口径保留原值，不计算比例。推广/商单未知写 unknown 并单列；不能将未知当自然流量。阅读不是点击数，不自动算点击率。

```bash
python3 scripts/xhs.py metrics xhs-workspace/metrics/raw/normalized-input.csv --kind real
```

输出 raw.csv 保留导入字节、normalized.json 保留缺失值、review.md 给出观察事实、可能解释、其他解释和一个实验。test/real 标记不符拒绝导入。内容哈希识别重复文件，不覆盖已有复盘批注。自动复盘文字只是待作者核对的分析草稿，不构成因果发现；Agent 应再结合实际标题、证据、推广等背景按 analytics Skill 实质复盘。修改解释时编辑 reviews 下报告，不改变原始导出。

完成实质复盘后可运行 `python3 scripts/xhs.py reviewed my-post --report xhs-workspace/reviews/real/导入摘要.md --note '本轮观察与唯一实验'`，仅允许已发布且真实数据包含该 post_id 的笔记转为已复盘。单篇当前状态以 state.json 为准；topics.csv 是人工选题索引，推进时同步该行，不能用索引中的手写状态代替发布证据。

## 隐私、成本与调度

整个 xhs-workspace 被 Git 忽略；这只是防误提交的第一层，不是秘密扫描或访问控制。发布前逐一核对源码、截图和正文，不在日志中输出凭据，不上传整批评论/私信。允许入库的 examples 只有公开来源与显著标记的测试数据。

本轮新增付费 API/服务：0；模型额度、设备、电力和人工投入未计量，不能写成零成本。未创建定时任务；后续日报/周报须作者明确选择。
