/* SPDX-License-Identifier: MIT
 * Linker-selected subsets of the QEMU AN385 SSRAM banks, not board capacities.
 * CODE is SRAM at address zero, not physical Flash.
 */
ENTRY(Reset_Handler)
MEMORY {
    CODE (rwx) : ORIGIN = 0x00000000, LENGTH = 256K
    RAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}
_stack_top = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
    .vectors : { KEEP(*(.vectors)) } > CODE
    .text : { *(.text*) *(.rodata*) . = ALIGN(4); } > CODE
    .data : {
        . = ALIGN(4); _data_start = .;
        *(.data*) . = ALIGN(4); _data_end = .;
    } > RAM AT> CODE
    _data_load = LOADADDR(.data);
    .bss (NOLOAD) : {
        . = ALIGN(4); _bss_start = .;
        *(.bss*) *(COMMON) . = ALIGN(4); _bss_end = .;
    } > RAM
    /DISCARD/ : { *(.comment) *(.note*) *(.ARM.exidx*) *(.ARM.extab*) }
}
ASSERT(_bss_end <= _stack_top - 4096, "insufficient stack headroom")
