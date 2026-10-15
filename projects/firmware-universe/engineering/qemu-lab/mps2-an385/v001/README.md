# QEMU工程实验｜Cortex-M3 / MPS2 AN385

**已实际建立并运行。** 当前是原创裸机受控故障实验，不是BK7258或工业相机产品固件，不是动画造出的日志。

## 为什么选这台机器

- ARM M-profile适合表现向量起步、RAM初始化与MMIO设备访问。
- `mps2-an385`是现有QEMU支持的Cortex-M3机器，不需要新建一个芯片模型或安装SDK。
- 当前WSL已具备QEMU、`arm-none-eabi-gcc`、binutils与`gdb-multiarch`，直接复用。
- 选择M3减少首轮验证的安全域/多核复杂度；这不意味着已有BK7258/M33方案已经通过或可以原样移植。
- AN385实体平台是FPGA承载的开发环境；本实验只运行其软件模型，不做FPGA硬件操作。

实际工具：QEMU `6.2.0 (Debian 1:6.2+dfsg-2ubuntu6.27)`，GCC `10.3.1`，GDB `12.1`。工具二进制SHA-256和每轮命令均记录在产物中。

## 这次实际做了什么

1. 编写原创`firmware.c`与`linker.ld`。
2. 生成故障/修订两份ELF、bin、真正的固件链接map与反汇编。
3. 从向量起步，记录初始SP/PC、RAM初始化、应用与UART状态。
4. 故意遗漏UART TX enable，复现0字节输出和发送等待。
5. 仅启用TX，重建并从复位复跑，得到42字节客体UART输出。
6. 检查ELF/bin行为对应，重复修订版；另做2次无GDB运行，确认串口结果不依赖调试器。

**最终session：** `artifacts/session-20261012T090234263613Z/`。

- [验证报告](validation_report.md)
- [问题证据与原因](issue_report.md)
- [自动检查原始汇总](artifacts/session-20261012T090234263613Z/validation.json)
- [真实UART输出](artifacts/session-20261012T090234263613Z/runs/fixed-elf-1/uart.log)
- [原版bin](artifacts/session-20261012T090234263613Z/broken/firmware.bin) / [修订版bin](artifacts/session-20261012T090234263613Z/fixed/firmware.bin)
- [修订ELF](artifacts/session-20261012T090234263613Z/fixed/firmware.elf) / [链接map](artifacts/session-20261012T090234263613Z/fixed/firmware.map)
- [实际派生映射](artifacts/session-20261012T090234263613Z/fixed/memory_map.json)
- [配置差异](artifacts/session-20261012T090234263613Z/fix.patch)

旧session包含首轮试跑，保留不覆盖。后续发现QEMU log trace后端会将反汇编与设备事件合并，已将最终脚本统一使用`trace.log`并核验真实合并流，而不是检查空的独立日志。

## 再跑一遍

从仓库根目录执行：

```bash
python3 projects/firmware-universe/engineering/qemu-lab/mps2-an385/v001/run_lab.py
```

脚本无需API密钥或网络，使用已有工具，每次创建新的session，不覆盖已有产物。输出目录包含源快照、真实构建产物、环境身份、实际映射和7次运行记录；`latest-run.json`只指向最近一次自动执行。

它仅创建/控制自己的本地QEMU进程，GDB端口限定`127.0.0.1`并在运行结束关闭，不连接真实设备、账号或用户浏览器。观测版由宿主在取得检查点后停止；无调试器版限定2秒。没有使用无限后台任务。

### 直接看正常bin输出

```bash
timeout 2s qemu-system-arm \
  -M mps2-an385 -cpu cortex-m3 \
  -kernel projects/firmware-universe/engineering/qemu-lab/mps2-an385/v001/artifacts/session-20261012T090234263613Z/fixed/firmware.bin \
  -display none -monitor none -serial stdio -no-reboot
```

该程序输出后进入WFI，宿主超时停止是预期行为；退出码124不是客体通过证据。自动脚本另行检查输出与执行状态。

## 实际机制与参考

- 代码/向量使用地址0处SSRAM的链接子集，**不是实体Flash**；RAM使用`0x20000000`处SSRAM子集。
- 复位向量建立SP及Thumb入口。测试分别实际执行ELF与其objcopy产生的raw bin；不是从ELF `e_entry`直接解释Cortex-M起步。
- UART0=`0x40004000`；DATA/STATE/CTRL/BAUDDIV偏移为0/4/8/0x10，访存宽度32位，负载字符8位。
- 故障是TX_EN未设，不是Clock gate missing。该版本模型的发送机制不能按BK7258的FIFO/时钟行为画。
- BSS预填后清零是明确的诊断钩子，使RAM变化可观察；不宣称真实上电RAM内容。

核对的上游基础版本机制来源：

- [MPS2机器文档](https://github.com/qemu/qemu/blob/v6.2.0/docs/system/arm/mps2.rst)
- [机器映射与UART连接](https://github.com/qemu/qemu/blob/v6.2.0/hw/arm/mps2.c)
- [CMSDK APB UART实现](https://github.com/qemu/qemu/blob/v6.2.0/hw/char/cmsdk-apb-uart.c)
- [M-profile镜像装载](https://github.com/qemu/qemu/blob/v6.2.0/hw/arm/armv7m.c)

缓存只读资料在仓库`.cache/qemu-mps2-research/`。上游tag源码用作机制依据，不冒充带Ubuntu补丁的本机二进制逐字对应源码；本次结论另有实际运行、状态和设备事件支撑。

## 交给导演设计的事实

已有真实工程链：**原版bin/ELF → 映射与环境 → 执行记录 → TX禁用问题 → 一项配置差异 → 修订镜像 → 新运行与有限报告**。

Shot 07–08应以UART TX enable为本次真实位置，不能保留缺门控标签。代码和MMIO可使用本session记录；画面仍必须注明受控实验，不冒充真实产品事故或多Agent独立协作。

下一阶段可据此制作机制预演；本轮没有生成视频或设计图，没有访问实板，也没有把整片登记为制作审核通过。
