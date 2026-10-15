param([Parameter(Mandatory=$true)][string]$EvidencePath,[int]$DoubleClickX=-1,[int]$DoubleClickY=-1)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class DouyinWindowCapture {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int cmd);
}
'@
$process=Get-Process -Name JianyingPro -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $process) { throw 'Jianying main window not ready' }
$window=[System.Windows.Automation.AutomationElement]::FromHandle($process.MainWindowHandle)
[DouyinWindowCapture]::ShowWindow($process.MainWindowHandle,5)|Out-Null
[DouyinWindowCapture]::SetForegroundWindow($process.MainWindowHandle)|Out-Null
if ($DoubleClickX -ge 0 -and $DoubleClickY -ge 0) {
    Add-Type @'
using System;
using System.Runtime.InteropServices;
public class DouyinWindowInput {
 [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h,int m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
'@
    [DouyinWindowInput]::SetForegroundWindow($process.MainWindowHandle)|Out-Null
    $point=[IntPtr](($DoubleClickY -shl 16) -bor $DoubleClickX)
    [DouyinWindowInput]::SendMessage($process.MainWindowHandle,0x201,[IntPtr]1,$point)|Out-Null
    [DouyinWindowInput]::SendMessage($process.MainWindowHandle,0x202,[IntPtr]0,$point)|Out-Null
    [DouyinWindowInput]::SendMessage($process.MainWindowHandle,0x203,[IntPtr]1,$point)|Out-Null
    [DouyinWindowInput]::SendMessage($process.MainWindowHandle,0x202,[IntPtr]0,$point)|Out-Null
    Start-Sleep -Milliseconds 1200
}
$all=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
$names=@();foreach($el in $all){if($el.Current.Name){$names+=@{name=$el.Current.Name;type=$el.Current.ControlType.ProgrammaticName;id=$el.Current.AutomationId;class=$el.Current.ClassName;rect=$el.Current.BoundingRectangle.ToString()}}}
$json=$names|ConvertTo-Json -Depth 5
[IO.File]::WriteAllText((Join-Path $EvidencePath 'jianying-ui.json'),$json,(New-Object System.Text.UTF8Encoding($false)))
$rect=$window.Current.BoundingRectangle
$bmp=New-Object Drawing.Bitmap ([int]$rect.Width),([int]$rect.Height)
$graphics=[Drawing.Graphics]::FromImage($bmp)
$dc=$graphics.GetHdc()
$captured=[DouyinWindowCapture]::PrintWindow($process.MainWindowHandle,$dc,2)
$graphics.ReleaseHdc($dc)
if (-not $captured) { $graphics.Dispose();$bmp.Dispose();throw 'Window-only capture failed; no unrelated desktop capture taken.' }
$bmp.Save((Join-Path $EvidencePath 'jianying-window.png'))
$graphics.Dispose();$bmp.Dispose()
$names|Select-Object -First 70|ConvertTo-Json -Depth 5
