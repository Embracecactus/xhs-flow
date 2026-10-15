# WSL 调用 Windows UI Automation

仅在没有更合适的现有浏览器控制会话时读取。这里记录 2026-10-13 已验证的原生交互方式，不封装平台发布接口。参数均来自当次发现；示例不是可直接重放的完整发布脚本。

## 目标窗口

通过现有工具或 UIA 枚举桌面顶层窗口，选择目标浏览器窗口并读到正确地址/账号。后续查询从该窗口的 Document 元素向下进行，避免扫描其他窗口和登录输入内容。进入文件选择弹层时查询范围是该窗口的原生对话框。

PowerShell 避免用 `$HOME`、`$PID` 等系统变量保存任务参数。例如，当调用方已经提供 `$targetHwnd`、`$targetPid` 后：

```powershell
Add-Type -AssemblyName UIAutomationClient
$target = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$targetHwnd)
if ($target.Current.ProcessId -ne $targetPid) { throw 'Target process changed' }
if ($target.Current.Name -notlike '*抖音*') { throw 'Target page changed' }
$document = $target.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Document))
if (-not $document) { throw 'Target document absent' }
```

标题含“抖音”只是窗口防误操作条件，不能替代地址与实际账号核验。动作前重新检查目标与控件，键鼠输入还需确认前台 HWND 一致及坐标在窗口范围内。前台断言失败应停止该动作；先恢复目标窗口再继续，不能把后续输入发到其他应用。

## 选择控件模式

先检查 `GetSupportedPatterns()` 或 `TryGetCurrentPattern`，再选操作。`FindFirst` 不能代替唯一性检查，最终提交和多项同名按钮尤其如此。

| 控件/任务 | 本次可用方式 | 回读 |
| --- | --- | --- |
| 标题 Edit，名称“填写作品标题，为作品获得更多流量” | `ValuePattern.SetValue` | `ValuePattern.Current.Value` |
| 正文富文本 Group | `SetFocus`，目标窗口内 Unicode 原生输入 | `TextPattern.DocumentRange.GetText(-1)` |
| 普通 Button 或明确可 Invoke 的 Group | `InvokePattern.Invoke` | 弹层、编辑值或目标页面实际变化 |
| 同时发布/可见性等 CheckBox | `TogglePattern.Toggle` | `Current.ToggleState`；同时检查互斥项 |
| AI 声明 RadioButton | 先试 SelectionItem，失败后现场原生点击 | `Current.IsSelected` + 主表单声明 |
| 内容管理作品卡片 | 从唯一匹配标题找最近卡片祖先，`ScrollItemPattern.ScrollIntoView` | 只读取该条目中的时间与状态 |

富文本没有 `ValuePattern` 时不要强行调用。现场曾出现 class `zone-container editor-kit-container editor editor-comp-publish notranslate chrome window chrome88`，但 class 和内部浏览器版本后缀会变化；只能作为发现线索，不作为永久选择器。已保存封面入口的“选择封面”文字会消失，应重新定位封面 Group，不能继续依赖旧标签数量。

“上传封面”文字本身可能没有 Invoke，父元素也可能是整个 modal；不要盲目 Invoke 任意祖先。此时读取文字的最新矩形并截图，确认无遮挡后原生点击。提示气泡和下拉层可能挡住坐标，动作无效时先读实际状态。

## 文件选择器

本次使用过的原生结构：当前目标窗口下 `ClassName=#32770` 的文件对话框；文件名为原生 Edit，`AutomationId=1148`；打开按钮名“打开(O)”。这是历史观测，其他语言或浏览器现场可能不同。

1. 确认出现本次点击产生的对话框，重新获取其原生 HWND 和子控件句柄。
2. 传入真实可访问的 Windows 路径。`Test-Path -LiteralPath` 通过后，对文件调用 `Get-FileHash -LiteralPath ... -Algorithm SHA256`，与清单比较。
3. 本次文件名原生 Edit 使用 `WM_SETTEXT` 写入、`WM_GETTEXT` 回读完全相同的路径，然后对当前“打开”原生 Button 发 `BM_CLICK`。可访问的 Value/Invoke 模式同样可用，以现场为准。
4. 打开一次后等对话框消失和编辑页状态变化，再判断上传结果。路径回读不是上传成功证据。

不要将旧 HWND、固定用户名、发行版名或原生子控件句柄写成通用脚本常量。若临时转存，只复制本篇文件，并验证 Windows 副本与 WSL 原件哈希相同。

## 富文本输入与比较

本次备用输入使用 Windows `SendInput`：先确认目标编辑器获得焦点，Ctrl+A 仅替换该字段；逐行发送 UTF-16LE 单元，换行发送 Return。没有读取或改写系统剪贴板。不能在未核对焦点时发送 Ctrl+A。

正文回读示意：

```powershell
# $captionElement 必须来自本次确认的正文编辑器
$textPattern = $captionElement.GetCurrentPattern(
    [System.Windows.Automation.TextPattern]::Pattern)
$rawCaption = $textPattern.DocumentRange.GetText(-1)
```

保存 rawCaption，再按 [SOP 的正文比较规则](../../../docs/douyin-web-publishing.md) 处理已观察到的编辑器标记。示例中的 Superscript、中文标点、英文空格和空段都必须保留；话题行另行比较精确文本、顺序与实际实体。

## 工具调用与证据

- 脚本保存在本篇被忽略的运行目录，参数化目标窗口与输入文件，不把本例 `win_input.py` 的固定 HWND/PID 直接复制成通用能力。
- 调用宿主程序走工具正常审批。较长 PowerShell 代码优先写文件后用 `-File`；参数按 shell 语义引用，不把 JSON 字符串当 shell 转义，避免反引号或 `$()` 意外执行。
- 控件查询、状态回读和截图输出只保留本篇必要内容，不导出登录字段、Cookie、凭据或整个账号历史。截取目标窗口后实际查看图片；截图文件存在不代表已经检查。
- 相依动作串行执行并检查每步结果。等待以可见状态为准；工具返回失败时不盲目继续下一次输入。
- 记录“请求动作”“工具返回”“回读结果”三项。本次遇到 UIA Select 返回而状态未变、普通点击被气泡遮挡和前台断言失败，均应保留为真实错误，不归纳成“WSL 不支持”。
- 不为离线校验 Skill 再操作真实发布页。页面结构变化时，在下一次已授权操作中重新发现和核验。
