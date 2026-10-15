# Boot：装载、诊断起步与真实启动链

> 本片保留Bootloader角色，但不能把未执行的引导路径画成已通过。

## 本片选择的路径

1. 匹配机器与镜像约定，使用固定BK7258下游诊断环境。
2. `-kernel`选择诊断逻辑XIP路径；宿主侧装载器尝试装载ELF。本片只使用有效匹配ELF，不展示raw fallback为万能兼容机制。
3. CPU0配置向量基址为`0x02010000`；镜像须在该位置提供有效向量。
4. Cortex-M按向量建立初始栈指针和复位处理入口；不将ELF的`e_entry`字段直接作为本片起步PC。
5. 本片规划中的最小固件启动代码准备RAM运行环境，然后执行应用逻辑和UART输出。`.data`初始化、`.bss`清零属于此程序设计，不泛指所有固件都采取同一路径。

## Bootloader角色的边界

此诊断路径绕过ROM和Bootloader。守序可以在叙事中介绍封存路线、让出诊断入口、提醒未验证工作，但这些表演不表示客体Bootloader代码已运行。

ELF装载不等于完整Boot。不能出现ROM/BL1/BL2通过标记、安全验签章或产品启动完成结论。后续若改为真实NOR启动，必须重新核对整条工程路径与分镜，不沿用本模式审核。

## 已核对的固定源码

- [板级配置与装载调用](https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/bk7258_boards.c)
- [SoC向量配置](https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/bk7258.c)
- [Armv7-M装载与复位注册](https://github.com/Embracecactus/qemu-bk7258/blob/7057f179ad2a31c415053675af72027f1675fb1e/hw/arm/armv7m.c)

完整证据边界与制作前核对项见[validation.md](validation.md)。未进行本轮固件执行或实机启动验证。
