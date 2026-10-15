# 有限验证报告｜Cortex-M3 / MPS2 AN385

状态：**原创受控诊断回归通过，不是产品或实机验收。**

本轮结果：[实际运行汇总](artifacts/session-20261012T090234263613Z/validation.json)。此前试跑保留，报告只引用最终session。

## 检查结果

|实际运行|观察方式|UART输出|结果|
|---|---|---|---|
|故障版ELF|5个GDB检查点＋设备事件|0字节 / 0个TX事件|复现TX禁用后的发送等待|
|修订版ELF|相同观察|42字节 / 42个TX事件|抵达诊断完成点|
|故障版bin|相同观察、匹配ELF提供符号|0字节 / 0个TX事件|与故障ELF一致|
|修订版bin|相同观察、匹配ELF提供符号|42字节 / 42个TX事件|与修订ELF一致|
|修订版ELF重复运行|相同观察|42字节 / 42个TX事件|输出与完成状态重复成立|
|故障版bin无调试器|正常运行，宿主限定2秒观察|0字节|独立复现沉默|
|修订版bin无调试器|相同条件|42字节|独立输出与观测版一致|

有调试器的5次运行均核对：

- 复位PC与向量Thumb入口对应，初始SP=`0x20010000`。
- `.data`运行值从0变为预期值，装载源内容可读。
- BSS经受控预填后清零，不仅依赖QEMU冷启动RAM原本是0。
- main抵达，初始化检查通过，UART配置与两版条件相符。
- 故障版记录TXFULL等待；修订版抵达完成点，线程态IPSR=0、异常观察标记=0。
- 实际trace与stderr未发现invalid/unimplemented/bad-offset/lockup诊断。

无调试器运行只检查有限时间内的真实串口输出，不声称它们提供了同样的内部状态采样。宿主主动停止自己的QEMU是预定收尾，不拿超时或退出码宣称客体通过。

## 真实输出

[修订版UART原始记录](artifacts/session-20261012T090234263613Z/runs/fixed-elf-1/uart.log)：

```text
Firmware started
DATA_OK BSS_OK UART_OK
```

来自客体32位UART MMIO写入和CMSDK设备字符后端，不使用semihosting打印，也不由宿主脚本补写结果。判定还核对内存状态、设备事件和完成点，而不是只看这句话。

## 证据身份

- [原版构建身份](artifacts/session-20261012T090234263613Z/broken/build-manifest.json)
- [修订版构建身份](artifacts/session-20261012T090234263613Z/fixed/build-manifest.json)
- [环境与工具二进制身份](artifacts/session-20261012T090234263613Z/environment_manifest.json)
- [实际源码差异](artifacts/session-20261012T090234263613Z/compiled-source.patch)
- [故障观测](artifacts/session-20261012T090234263613Z/runs/broken-elf-1/observations.json)
- [修订观测](artifacts/session-20261012T090234263613Z/runs/fixed-elf-1/observations.json)
- [实际映射派生产物](artifacts/session-20261012T090234263613Z/fixed/memory_map.json)
- [诊断解释与其他解释](issue_report.md)

ELF、bin、链接map、linker、源码快照和原始记录均保留。源路径参与ELF调试信息；不同输出目录的ELF整体哈希可能变化，未宣称跨目录/跨主机逐字节可重复构建。每次运行均绑定该次确切镜像哈希。

## 边界

本例证明本机QEMU中该原创程序的向量起步、受控RAM初始化和UART发送路径。没有执行Bootloader/ROM，没有完整RTEMS或真实产品，没有外设全覆盖、安全启动、模拟芯片物理时序或真实目标板结果。

BSS预填是为了观察清零过程的诊断钩子，不是物理上电状态。`trace.log`合并了设备事件与TB翻译反汇编，后者不是逐指令、周期精确的连续执行轨迹。GDB观测会暂停客体，不用观测时长推导性能。

未修改QEMU本身、未安装工具、未刷机、未生成视频、未提交或推送Git。后续工业CG应标注“受控工程实验/模型示意”，不能把这次注入故障包装成真实产品事故。
