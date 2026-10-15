# QEMU：软件世界与真实边界

> 机制设计，不是本轮运行证据。完整审核见[validation.md](validation.md)。

## 本片范围

固定下游项目`qemu-bk7258@7057f179ad2a31c415053675af72027f1675fb1e`的匹配裸机诊断路径；不泛指所有QEMU平台，不宣称最新master能力。

- QEMU实例化选定机器的CPU、存储映射与设备模型，以TCG承载客户机指令执行。
- CPU0角色表现客户机架构状态，不是宿主物理CPU，也不承诺周期精确或完整厂商缓存/性能行为。
- 地址空间访问根据映射落到存储或MMIO设备区；MMIO由设备回调处理，不是普通RAM存取。
- Peripheral角色具体代表UART0：程序配置受支持的功能时钟与串口条件、检查TX能力、写发送寄存器；模型接纳字节、推进发送并交给宿主字符后端。
- 字符A/0x41是数据负载，不意味着MMIO必须8位写。寄存器偏移、合法访问宽度及具体配置需在实现时查固定提交源码。
- 本片UART字符不能用semihosting直接打印冒充；宿主输出通道不是实体TX引脚。
- 无线、音视频等未建模范围是此固定诊断模型的边界，不是“QEMU不能模拟任何无线或音视频”的通用结论。

## 不能扩大结论

一条诊断路径可执行，不等于完整产品固件、完整SoC、ROM/Bootloader、安全启动或真实硬件通过。引脚电压、波形、物理时序仍需实机证据。

## 一手来源

- [QEMU Emulation](https://www.qemu.org/docs/master/about/emulation.html)
- [QEMU Memory API](https://www.qemu.org/docs/master/devel/memory.html)
- [固定下游机器文档](https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/docs/system/arm/bk7258.rst)

本片仍为原理动画规划；没有实际运行日志、设备读数或性能结果。
