#!/usr/bin/env python3
"""First horizontal explainer, selected from the author's public GitHub."""
import yaml
from flow import WORKSPACE, create

SLUG='qemu-without-board'
TITLE='没插开发板，固件为什么也能跑？'

def main():
    if (WORKSPACE/SLUG).exists():
        print('已有本篇任务，保留当前内容。');return
    p=create(WORKSPACE,SLUG,'B',TITLE,demo=True);v=p/'v001'
    lines=[
        (0,2.7,'没插开发板，固件也能跑？',None),
        (2.7,6,'秘密是，用软件模拟硬件。',None),
        (6,9.6,'QEMU模拟CPU执行指令。','模拟器先模拟处理器的指令。'),
        (9.6,13,'再按地址，提供内存。',None),
        (13,16.2,'程序读写外设寄存器时，',None),
        (16.2,20,'访问会交给外设模型。',None),
        (20,23.4,'比如写串口，模型输出字符。',None),
        (23.4,27,'定时器到点，再触发中断。',None),
        (27,30.3,'一条硬件路径，就跑通了。',None),
        (30.3,34,'整块芯片，还不能打勾。',None),
        (34,37.7,'这是BK7258诊断项目的边界：','看这个诊断项目的边界：'),
        (37.7,40.3,'部分CPU、内存和外设已建模。','已有部分硬件模型。'),
        (40.3,43,'无线和音视频，仍不支持。',None),
        (43,47,'模拟里通过，也要上板验证。',None),
        (47,51,'尤其是电压、波形和实际时序。',None),
        (51,54,'先验证逻辑，再验证硬件。',None),
        (54,57.2,'能先查清逻辑问题，',None),
        (57.2,60,'实机验收，仍然不能省。',None),
    ]
    cues=[dict(start=a,end=b,text=t,**({'spoken':sp} if sp else {})) for a,b,t,sp in lines]
    specs=[(0,6,'没有开发板\n固件也能跑？','hook','反差','实体芯片轮廓变为软件模型'),(6,13,'指令与内存\n先让程序执行','cpu','执行','ARM指令经过TCG；内存行逐格点亮'),(13,20,'一个地址\n找到一个模型','bus','访问','CPU写寄存器，经MMIO路由到外设响应'),(20,27,'写入字符\n看到响应','uart','响应','串口输出A；定时器到点触发IRQ'),(27,34,'一条路径通过\n整芯片仍有边界','boundary','边界','局部连通路径和整芯片缺块并列'),(34,43,'公开项目\n支持到哪一步','inventory','证据','部分CPU/内存/外设；无线与音视频未支持'),(43,51,'模拟里的逻辑\n实机上的物理','hil','实机','并列逻辑流与概念波形，物理仍待测'),(51,60,'先验证逻辑\n再验证硬件','closing','判断','同一芯片对象回归，收束验收边界')]
    scenes=[dict(start=a,end=b,heading=h,diagram=g,chapter=c,note=n) for a,b,h,g,c,n in specs]
    d=dict(kind='B',title=TITLE,duration=60,width=1920,height=1080,style='qemu-cinematic',voice='windows_sapi',kicker='见微录 / QEMU 原理',description='不插开发板也能运行匹配模型的程序，靠的是CPU、内存和外设模型共同响应。用qemu-bk7258公开诊断项目讲清原理和范围：局部路径通过，不能替代整芯片支持或实机验收。本片是原创原理动画测试版，系统合成配音，未展示本轮实机或固件启动实测。',hashtags=['嵌入式开发','QEMU','固件开发'],cover_kicker='QEMU · 60秒看懂',cover_lines=['没插开发板','固件也能跑？'],cover_categories=['执行指令','响应外设','实机验收'],cover_payoff='软件模拟硬件，验收边界要分清',cues=cues,scenes=scenes)
    (v/'shotlist.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
    script=f'# {TITLE}\n\n横屏技术动画测试作品。用户已委托从知识库/GitHub选题；本篇标题、风格和正式终稿尚未获作者确认，无发布授权。默认受众为想理解固件调试的嵌入式开发者；目标是讲清一个原理，不承诺涨粉或故障修复。\n\n## 核心判断\n\n用软件实现CPU、内存与外设的行为，可以运行匹配这些模型的程序；模拟器的覆盖范围和实机验收必须分别证明。\n\n## 完整口播\n\n'
    for c in cues:script+=f"- {c['start']:g}–{c['end']:g}s：{c['text']}"+(f"（配音：{c['spoken']}）" if c.get('spoken') else '')+'\n'
    script+='\n## 制作设计\n\n1920×1080、30fps、60秒；8个连续镜头、18句变长旁白。原创SVG芯片对象贯穿，使用形变、流动、局部放大和双列构图；每段呈现一项因果状态变化。确定性按frame渲染，无案例素材、无音乐、无真人/克隆声音。字幕最后烧录，独立安全区；系统语音按整句对齐，不截词。\n\n## 事实边界\n\nQEMU执行和外设响应均为原理示意，不是本轮实际跑固件的录屏。项目表述限定qemu-bk7258@7057f17的诊断子集；不宣称上游支持、整芯片完成、无线或音视频可用。波形是概念示意，绝不是实机测量。模拟能验证的逻辑范围依模型而定；本片不声称性能与真实芯片一致，也没有时间节省数据。\n'
    (v/'script.md').write_text(script)
    (v/'sources.md').write_text('''# 技术来源与权利

读取时间：2026-10-12。知识库提供选题线索，公开项目及QEMU官方文档提供成片事实。未搬运截图、Logo、原作者动画、音乐或长段代码。全部画面和封面为原创图形；配音为本机Microsoft Huihui Desktop系统语音。没有客户素材或个人资料。

| 论断 / 时段 | 一手来源与固定范围 | 使用边界 |
| --- | --- | --- |
| QEMU可模拟CPU指令，6–13s | https://www.qemu.org/docs/master/about/emulation.html | 解释TCG的软件模拟能力，不宣称每个CPU都完整支持 |
| 访存可路由到RAM或设备MMIO，13–20s | https://www.qemu.org/docs/master/devel/memory.html | 地址/箭头为原理示意，不是实际指令跟踪 |
| CPU、内存、UART、定时器的诊断子集，20–43s | https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/docs/system/arm/bk7258.rst | 读取时master=7057f179ad2a31c415053675af72027f1675fb1e；文件blob=218115e824dfc4152215b36ca93402ac12aeeee7 |
| 无线、音视频未建模；模型不能替代物理验收，27–60s | 同上文档的能力边界与Chip-first validation status | 本轮没有启动固件/物理测量，不把模型子集或旧CI当成整芯片验收 |

知识库选题线索：Embracecactus/jianwei 的QEMU ARM启动笔记（blob c3a70c1672dd5f6806fd4686343b60b4d55ffc8d）。只借选题方向，未导出其私人信息或照搬旧启动命令；虚拟平台和串口解释未作为本片证据。

画面研究见../../../../platforms/douyin/docs/opus55-research.md。借鉴代码动画的因果表达和确定性渲染，不借用角色、品牌或原作者音乐。本片由当前Agent制作，没有调用Opus 5.5。
''')
    print(v)

if __name__=='__main__':main()
