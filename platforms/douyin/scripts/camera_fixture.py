#!/usr/bin/env python3
"""Original source-backed 60s animation test. Never overwrite author edits."""
import yaml
from flow import WORKSPACE, create

SLUG='industrial-camera-disconnect'


def main():
    if (WORKSPACE/SLUG).exists():
        print('已有测试任务，保留当前内容。');return
    p=create(WORKSPACE,SLUG,'B','工业相机为什么会掉线？',demo=True);v=p/'v001'
    narration=['相机掉线，先别急着换线。','画面停住，可能是三种现象。','断链、丢帧，或者等待触发。','先看设备列表：相机还在吗？','再看链路事件和错误码。','设备在，只有图像失败，','不一定是真正的断线。','网口相机先查丢包和重传。','网线、交换机和网卡都要看。','降低帧率，观察坏帧是否减少。','如果控制连接超时，','还要检查程序有没有发心跳。','调试暂停，也可能触发超时。','USB相机要查线材和带宽。','多个插口，可能共用控制器。','先减少带宽，再做对照。','每次只改一个条件，','记录同时刻的日志和帧统计。','先分清断链、丢帧、等触发，','再定位原因，以日志为准。']
    cues=[dict(start=i*3,end=(i+1)*3,text=t) for i,t in enumerate(narration)]
    specs=[(0,3,'相机“掉线”？\n先别急着换线','link','第一步：描述看到的现象'),(3,9,'画面停住\n先区分三种现象','three','断链、丢帧和等待触发，排查路径不同'),(9,15,'先确认\n设备与链路状态','checklist','设备列表 + 链路事件 + 错误码'),(15,21,'图像失败\n未必是真断线','packets','设备仍在线，也可能拿到不完整的帧'),(21,30,'网口相机\n查丢包与重传','packets','网线 → 交换机 → 网卡；降帧率做对照'),(30,39,'控制连接超时\n检查心跳','heartbeat','调试暂停是一个已知例子；超时值依设备而定'),(39,48,'USB：多个插口\n也可能共用带宽','usb','检查线材与控制器；降低带宽做对照'),(48,54,'一次只改一项\n把证据对齐','checklist','按时间关联事件日志和帧统计'),(54,60,'先分清现象\n再定位原因','three','常见排查思路；具体以设备与SDK日志为准')]
    scenes=[dict(start=a,end=b,heading=h,diagram=g,note=n) for a,b,h,g,n in specs]
    d=dict(kind='B',title='工业相机为什么会掉线？',duration=60,width=1920,height=1080,voice='windows_sapi',kicker='工业相机 / 常见排查思路',description='画面停住时，先分清断链、丢帧和等待触发，再对照设备日志、链路事件与帧统计逐项排查。技术动画测试作品，资料依据见sources.md；没有实机复现或维修结论。',hashtags=['工业相机','机器视觉','嵌入式开发'],cover_kicker='工业相机 · 60秒排查',cover_lines=['工业相机','为什么会掉线？'],cover_summary='断链  /  丢帧  /  等触发',cover_payoff='先分清现象，再定位原因',cues=cues,scenes=scenes)
    (v/'shotlist.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
    script='# 工业相机为什么会掉线？\n\n技术动画测试作品；受众默认机器视觉/嵌入式开发者；标题、风格、账号和终稿未获正式确认。本篇未授权发布。\n\n## 核心判断\n\n画面停住不是单一故障。先区分断链、丢帧和等待触发，再用同一时刻的设备状态、链路事件和帧统计定位。\n\n## 完整60秒口播与分镜\n\n'
    for c in cues:script+=f"- {c['start']:02}–{c['end']:02}s：{c['text']}\n"
    script+='\n## 证据边界\n\n图解均为原创概念动画，不是实际相机、后台或测试截图。丢包/心跳/USB带宽来自Basler/pylon文档，不能推导所有厂商相机的故障原因。降帧率、降带宽、单变量对照为诊断建议，不能保证修复。等待触发仅为分类提示，具体需SDK证据。没有故障率、虚构个人维修经历或商业推荐。\n\n## 制作策略\n\n横屏1920×1080、30fps；0–3秒Hook，九个连续镜头；深蓝底、青色链路、红色缺失或超时；系统中文合成音，逐句对齐，不用音乐；最后烧录字幕。没有真人原片，不调用付费ASR、不克隆声音。\n'
    (v/'script.md').write_text(script)
    (v/'sources.md').write_text('''# 技术来源与素材权利

读取：2026-10-12。官方文档作为事实依据，未搬运图片、Logo或长段文字。画面、封面和脚本为本项目原创；配音为本机Microsoft Huihui Desktop系统语音。无音乐、无肖像、无客户素材。

| 论断 | 一手来源 | 本片边界 |
| --- | --- | --- |
| GigE丢包可重传，帧保留期到期会使帧失败；不能把失败帧当掉线证据 | https://docs.baslerweb.com/stream-grabber-parameters | pylon语义；15–30s |
| 网线、交换机、网卡与不完整帧有关；降低流量用于对照 | https://docs.baslerweb.com/knowledge/troubleshooting-error-code-3774873620-0xe1000014-with-gige-cameras | 21–30s；不承诺修复 |
| GigE心跳超时可能关闭控制连接；调试暂停会阻止心跳 | https://docs.baslerweb.com/python-prog-guide | 30–39s；不宣称所有设备统一超时值 |
| USB3部件和带宽不足可使图像丢失/损坏，控制器上的相机共享资源 | https://docs.baslerweb.com/daa720-520um | 39–48s；原文针对该产品，采用常见排查措辞 |
| 不完整与跳帧计数可用于检查USB/GigE传输状况 | https://docs.baslerweb.com/bandwidth-manager | 48–60s；本片未展示实际计数 |

“一次只改一项、对齐时间戳”为方法建议。“设备还在”仅是证据之一，控制连接仍需单独核验。没有实机测量，不能声称复现或修好了掉线。
''')
    print(v)


if __name__=='__main__':main()
