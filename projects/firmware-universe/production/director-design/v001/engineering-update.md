# 导演设计的工程落点更新

用户已授权选择合适架构开始QEMU工程。现已实际运行[ARM Cortex-M3 / mps2-an385实验](../../../engineering/qemu-lab/mps2-an385/v001/README.md)。原三份导演设计保留；下列事实替换其中尚未验证的工程占位，不继承旧BK7258机制审核。

## 本次可用的工程对象

[最终session](../../../engineering/qemu-lab/mps2-an385/v001/artifacts/session-20261012T090234263613Z/validation.json)已包含：

- 故障版与修订版：bin、ELF、真正的链接map、构建身份及源快照。
- 分析依据：从ELF实际提取的`memory_map.json`、段/符号记录、linker。
- 环境：QEMU/GCC/GDB版本与二进制哈希、机器/后端与实际命令。
- 运行：设备事件＋TB翻译反汇编的`trace.log`、5点GDB状态、UART原始输出。
- 改动：配置与预处理源码diff。
- 解释与结果：[issue_report.md](../../../engineering/qemu-lab/mps2-an385/v001/issue_report.md)、[validation_report.md](../../../engineering/qemu-lab/mps2-an385/v001/validation_report.md)。

没有真实产品固件、RTEMS、实板素材或多Agent独立协作证据。

## 镜头落点

- **Shot 01–03：** 使用本例真实产物与MPS2机器配置。代码在SSRAM地址0的链接子集，不标为物理Flash；不展示BK7258、M33或其门控寄存器。
- **Shot 04：** 依据本例实际向量/SP/PC和RAM变化。BSS预填是诊断钩子，明确受控；不冒充物理上电状态。
- **Shot 05–07：** 真实问题是UART TX_EN遗漏：应用已抵达，第一次DATA写入后TXFULL保持1，TX事件0，宿主输出0字节。不是Clock gate missing，也不是程序完全未启动。
- **Shot 08–10：** 改动只启用CTRL.TX_EN；重新构建并复位运行。该CMSDK模型的单缓冲/字符后端行为不能照搬旧BK7258 FIFO、时钟或发送时序动画。
- **Shot 11：** 42个设备TX事件与42字节输出、入口和RAM状态共同支持有限诊断。ELF/bin及无GDB运行均做过对应检查。
- **Shot 12：** 本实验确实未接入目标板，但没有MPS2订购/到货证据。使用“未接入目标板，先做软件验证”更准确；原“开发板未到”任务前提只有对应真实项目资料成立时才用于纪录表达。

整段明确标注“原创受控工程实验 / 模型示意”，不把已知注入故障包装成真实产品事故或AI未知问题自主诊断。

## 当前门禁

工程实验已有证据。用户随后授权开始制作，现已生成[原创工业CG开场v003](../../../output/engineering-opening-v003.html)，见[制作与核验](opening-production.md)：12秒/1080p/24fps，输入字节、向量、派生报告及模型示意绑定最终session，尚未表现客体执行。基础核验完成，但正式视觉终审与试听未过；没有访问真实设备。后续机制镜头仍须绑定实际状态、TX_EN遗漏和独立版本复跑，不沿旧角色样段扩片。
