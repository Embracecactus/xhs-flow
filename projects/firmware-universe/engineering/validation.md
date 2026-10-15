# 工程机制审核与证据边界

> 归档来源：`../story/director-plan.md`。机制审核不等于固件运行、生产审核或实机验收。

## 5 技术审核

### 5.1 审核对象与证据等级

**本方案的机制级审核通过：下列七项未发现技术关系错误。** 这不是“已运行固件”“完整引导通过”或“硬件验收通过”的声明。没有本轮目标ELF、运行记录和实板测量，不能保证某一实际固件可跑，也不能证明未来成片不会画错。

为避免混用启动方式，本片固定采用：

- **平台范围：** `qemu-bk7258@7057f179ad2a31c415053675af72027f1675fb1e` 的匹配裸机诊断路径。
- **处理器视点：** CPU0，一般Cortex-M33模型；不声称已完整模拟厂商CPU身份、缓存或性能。其他两核不参加本故事，不意味着目标芯片只有一核。
- **入口：** 文档所述 `-kernel` 诊断逻辑XIP模式，使用有效向量位于 `0x02010000` 的ELF；绕过ROM与Bootloader。
- **固件设定：** 规划中的最小裸机程序，含适合本模式的向量、启动代码、RAM初始化和一次UART0字符输出。不是现有产品镜像已运行的复刻，也不展示伪造命令日志。
- **输出：** UART0模型连接宿主字符后端；字符A的输出为机制示意，不采用semihosting直接打印来冒充UART。

### 5.2 七项逐条审核

|项目|正确关系与本片采用方式|必须避免的错误|对应镜头／结论|
|---|---|---|---|
|ELF|ELF是可携带机器类型、程序头、可装载内容及其他元数据的文件格式。本片按可装载段映射内容，而不是按视觉页数装载所有节。存在ELF不保证ISA、链接地址或设备依赖匹配|把ELF当源码、指令执行器、万能兼容包；把调试信息都画成必须加载；把ELF入口字段当成本M-profile的直接PC|05–08；通过。具体段地址、大小及数据布局后续必须由实际诊断ELF确定，当前不编造|
|Boot|已核对板级调用和Armv7-M装载逻辑。本诊断路径由QEMU宿主侧装载，CPU从配置向量建立复位执行状态；向量初始SP与Reset_Handler决定本片起步。启动代码与独立Bootloader不是同一角色|声称Bootloader解析了此次ELF，已执行ROM/BL1/BL2，或已通过安全启动；从ELF e_entry直接跳转来解释本路径|07–10、25；通过。守序参与故事但没有执行客体Bootloader代码；RAM初始化归于本片最小固件启动代码|
|CPU|TCG承载客户机指令执行及状态变化；CPU角色表现客户机架构状态。按程序发起取指、访存、MMIO，非Firmware自己执行自己|把CPU角色等同宿主实体CPU，声称逐指令真实周期精确、完整厂商ISA/cache/DVFS；以角色步频表示MHz|08–18；通过。不画性能数值；不将CPU角色与QEMU作为两套重复执行引擎|
|Memory|存储映射提供指令/数据；RAM保存可写状态，代码所在逻辑XIP区域与RAM区分。地址空间还包含设备区，不全是Memory角色可任意写入的格子|把MMIO写成RAM写；把所有固件都说成必须复制进RAM；把.data复制/.bss清零归给ELF装载器或Bootloader而不说明模式|06、08–10、16；通过。10是本片最小程序的启动代码设计，不泛指所有固件|
|MMIO|CPU的访问根据地址空间映射路由到设备MemoryRegion，设备读写由相应宿主回调实现并产生设备状态变化。地址、访问宽度和数据负载分别表达|把MMIO当一种字符网络协议、实体电流线或额外CPU指令集；未知地址自动得到合理数据；合法访问无视寄存器宽度语义|13–17；通过。UART寄存器具体偏移与合法访问宽度须在实现时查同提交设备源码，本稿不杜撰|
|UART|程序先配置受支持的功能时钟与串口条件、检查TX接收能力，再写发送寄存器；模型接纳字符、推进发送事件并交给已连接的字符后端|一次写立即等同物理波形已正确；无时钟或FIFO满也照样成功；由semihosting打印冒充UART TX；字符8位等同MMIO必须8位写|12–20；通过。0x41为低位字符负载；真实引脚比特流、 framing误差等不宣称已验证，分镜时间不代表baud|
|QEMU|系统模拟器组合选定CPU、内存/总线映射、设备模型和后端，提供支持范围内的运行环境。此固定下游项目不是全QEMU的通用能力声明|任意ELF即跑、自动补齐外设、所有时序精确、全芯片覆盖；把QEMU说成Bootloader或客体固件的一部分|04–07、16–19、22–28；通过。未建模区域无成功响应，已有UART结果不扩展成完整产品启动与硬件验收|

### 5.3 已核对的一手依据

1. **QEMU：Emulation** — <https://www.qemu.org/docs/master/about/emulation.html>。支持TCG软件模拟执行的机制说明；沿用本机已保存文档，不把master文档等同本下游固件验收。
2. **QEMU：Memory API** — <https://www.qemu.org/docs/master/devel/memory.html>。RAM与MMIO区、MemoryRegion及设备回调的区别；沿用 `.cache/qemu-remake-research/memory.txt`。
3. **固定下游机器文档** — <https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/docs/system/arm/bk7258.rst>。本机保存于 `.cache/qemu-remake-research/bk7258.rst`；本次重点核对Implemented slice、Building and running、未建模范围。直接说明诊断绕过ROM/Bootloader及向量地址。
4. **固定板级源码** — <https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/bk7258_boards.c>。本次读取固定提交源码；诊断XIP由kernel选择，板级调用 `armv7m_load_kernel()` 并传入 `boot_vector`。
5. **固定SoC源码** — <https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/bk7258.c>。本次读取；CPU0的 `init-svtor` 来自配置boot vector，默认 `0x02010000`。
6. **固定Armv7-M装载源码** — <https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/armv7m.c>，`armv7m_load_kernel()`。本次读取；先尝试 `load_elf_as()`，失败可走raw-image fallback。虽然读取ELF entry，本函数不将其直接赋为PC；M-profile reset另行进行。因此本片使用向量启动，不用“ELF entry万能起点”的隐喻。

本次下载的三个源码文件保存在 `.cache/director-plan-research/`，仅作只读研究。没有运行目标固件，没有采集真实硬件，没有验证完整ROM/Bootloader链，也没有验证无线/音视频。

### 5.4 后续若进入制作，不能跳过的检查

- 取得或编写明确匹配本模式的最小诊断固件后，核对ELF程序头、装载映射、向量、栈范围、启动初始化与UART寄存器访问；尚未取得时只保留本稿机制示意，不能伪造运行证据。
- 若加入源码或具体数值，按固定提交设备实现核对UART地址、偏移、访问宽度、时钟和TX状态；不能从字符8位自行推导总线访问宽度。
- 检查最终动作是否保持：装载≠启动、启动代码≠Bootloader、MMIO≠RAM、输出≠实体引脚验证、一条路径≠整芯片完成。
- 观看无旁白版本：若看不出谁发起、谁接纳、何时输出、哪里未实现，必须改动作或镜头，不能靠增加字幕补救。
