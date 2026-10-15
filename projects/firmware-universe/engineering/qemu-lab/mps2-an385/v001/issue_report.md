# Issue Report｜UART沉默：遗漏TX enable

## 身份与范围

实际证据来自[session-20261012T090234263613Z](artifacts/session-20261012T090234263613Z/validation.json)。平台为本机QEMU 6.2.0 Ubuntu构建、`mps2-an385`、Cortex-M3。

这是一份原创诊断程序的**受控故障注入与回归**：故意遗漏UART CTRL.TX_EN，再通过源码差异、执行状态与设备事件验证行为。不是从真实产品发现的事故，也不用于证明AI盲测未知故障的能力。

## 现象与证据

故障版ELF与bin均真实运行：UART宿主输出为0字节，未到达`firmware_done`，停在发送等待路径。

[故障版状态记录](artifacts/session-20261012T090234263613Z/runs/broken-elf-1/observations.json)显示：

1. 从向量建立SP=`0x20010000`、PC=`0x0000010c`；向量中的Thumb复位入口为`0x0000010d`。
2. `.data`从运行区的0变为`0x13579bdf`；受控BSS预填`0xa5a5a5a5`后清零；应用检查`data_ok=bss_ok=1`。
3. 首次发送前，UART BAUDDIV=`217`、CTRL=`0`、STATE=`0`。
4. 设备trace记录32位写`UART_DATA@0x40004000`，负载`0x46`（字符F）。
5. 首次写入后，STATE.TXFULL=`1`、CTRL.TX_EN=`0`、发送尝试数=`1`，没有设备TX事件；CPU到达`uart_blocked`，等待第二个字符的发送空间。

这不是“固件完全没有启动”。入口、内存初始化与应用路径都已前进，未完成的是对外发送。

## 解释与其他解释

上游6.2.0的CMSDK UART实现，在DATA写入时设置TXFULL，再尝试发送；`uart_transmit()`在TX_EN未置位时不向字符后端输出。该实现与实际CTRL/TXFULL状态和0个TX事件相符。

- **装载或RAM初始化错误：** 与已记录的复位入口、main抵达及数据检查不符；本例未支持这个解释。
- **宿主后端未连接：** 两版都使用同类显式UART0文件后端；修订版正常输出。后端不是此次改动变量。
- **GDB造成输出差异：** 无调试器的独立bin运行仍复现故障版0字节、修订版42字节。
- **遗漏功能时钟门控：** 本例没有此项故障证据，不能照搬BK7258候选剧情。当前直接证据是UART TX enable遗漏。

这里验证的是此QEMU模型与此诊断的行为，不声称真实硅片每个边缘条件完全相同。

## 修订与复跑

[配置差异](artifacts/session-20261012T090234263613Z/fix.patch)仅改变`ENABLE_UART_TX`从0到1；[预处理源码差异](artifacts/session-20261012T090234263613Z/compiled-source.patch)仅增加一项操作：

```c
*(volatile uint32_t *)0x40004008 = 1u;
```

即使能CTRL.TX_EN。机器、CPU、UART后端类型、分频配置、检查标准和其他诊断源码保持一致。重新构建并从复位启动新镜像，不在运行中的故障版上临时写寄存器假装修复。

修订版记录CTRL=`1`、42个DATA写入、42个设备TX事件、42字节宿主输出，并抵达`firmware_done`。初始化两项检查均通过，完成点IPSR=`0`、异常观察标记=`0`。

原版与修订版ELF独立保留；新增指令引起后续地址和装载位置变化是正常构建结果。两版通过符号与构建身份对应，不强行使用同一个数值PC描述它们。

## 结论

**受控实验支持“遗漏UART TX enable导致本例沉默；增加该使能后，同条件重建复跑恢复输出”。**

没有证明完整产品Boot、RTEMS、BK7258、实体串口波形或实机验收。故障是人为注入，AI分析/运行由本次单Agent完成，不虚构多个独立Agent协作。
