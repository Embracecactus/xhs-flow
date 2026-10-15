# Xiaohongshu Flow

本目录保存小红书图文生产代码、公开演示、测试和平台专属文档。真实账号记录、正文版本、图片、后台证据与排期统一位于仓库根目录下被 Git 忽略的 `workspace/xiaohongshu/`。

流程为：来源 → 选题 → 原创文案 → HTML 图文 → 作者审核 → 经授权网页发布 → 真实数据 → 复盘。本地 CLI 不含账号登录、上传或发布接口。

## 运行

从仓库根目录执行：

```bash
npm ci --ignore-scripts --no-audit --no-fund
python3 platforms/xiaohongshu/scripts/demo.py
python3 platforms/xiaohongshu/scripts/xhs.py render demo-source-notes --note '演示初稿'
python3 platforms/xiaohongshu/scripts/xhs.py metrics platforms/xiaohongshu/examples/metrics-test.csv --kind test
```

首次重建输出 v001；源文件未变时复用已有版本。改稿应修改源文件、导出新版本并使旧审核失效，不为追齐本机版本号重复生成。

## 本地入口

- 账号与授权记录：`workspace/xiaohongshu/account.md`
- 本机审核入口：`workspace/xiaohongshu/wsl2-review.html`
- 公开演示源：`platforms/xiaohongshu/examples/demo-source-notes/`
- 操作手册：[docs/workflow.md](docs/workflow.md)
- 官方界面发布流程：[docs/ui-publishing.md](docs/ui-publishing.md)
- 初始验收边界：[docs/acceptance.md](docs/acceptance.md)

`workspace/` 中的链接只在当前本机存在，不会随 Git clone 出现。发布链接或用户明确确认才可把内容登记为已发布；指标模板不等于完成复盘。

## 检查

```bash
python3 -m unittest discover -s platforms/xiaohongshu/tests -v
python3 platforms/xiaohongshu/tests/render_acceptance.py
node platforms/xiaohongshu/scripts/validate.mjs workspace/xiaohongshu/posts/demo-source-notes/editable/index.html
```

浏览器导出与像素检查不代替作者对事实、排版和真实手机显示的终审。
