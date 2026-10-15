/* SPDX-License-Identifier: MIT
 * Original controlled diagnostic, not a BK7258/product firmware.
 * Cortex-M3 / QEMU MPS2 AN385 / CMSDK APB UART0.
 */
#include <stdint.h>

#define REG32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define UART0 0x40004000u
#define UART_DATA REG32(UART0 + 0x00u)
#define UART_STATE REG32(UART0 + 0x04u)
#define UART_CTRL REG32(UART0 + 0x08u)
#define UART_BAUDDIV REG32(UART0 + 0x10u)

extern uint32_t _data_load, _data_start, _data_end;
extern uint32_t _bss_start, _bss_end, _stack_top;
void Reset_Handler(void);
void Default_Handler(void);
int main(void);

__attribute__((section(".vectors"), used))
const uintptr_t vectors[16] = {
    (uintptr_t)&_stack_top, (uintptr_t)Reset_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, 0, 0, 0, 0,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler, 0,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler
};

volatile uint32_t initialized_marker = 0x13579bdfu;
volatile uint32_t zero_marker;
struct Diagnostic {
    uint32_t phase;
    uint32_t data_ok;
    uint32_t bss_ok;
    uint32_t tx_attempts;
    uint32_t exception_seen;
};
volatile struct Diagnostic diagnostic;

/* Debugger observation points; no semihosting or host-side UART printing. */
__attribute__((noinline)) void bss_poisoned(void) { __asm volatile("nop"); }
__attribute__((noinline)) void uart_blocked(void) { __asm volatile("nop"); }
__attribute__((noinline)) void firmware_done(void) { __asm volatile("nop"); }
__attribute__((noinline)) void startup_check_failed(void) { __asm volatile("nop"); }

void Default_Handler(void)
{
    diagnostic.exception_seen = 1;
    for (;;) { __asm volatile("wfi"); }
}

void Reset_Handler(void)
{
    volatile uint32_t *dst;
    const uint32_t *src = &_data_load;
    for (dst = &_data_start; dst < &_data_end; ++dst) { *dst = *src++; }
    /* Controlled test precondition: poison BSS so clearing is observable.
     * This is a diagnostic hook, not a claim about physical power-on RAM. */
    for (dst = &_bss_start; dst < &_bss_end; ++dst) { *dst = 0xa5a5a5a5u; }
    bss_poisoned();
    for (dst = &_bss_start; dst < &_bss_end; ++dst) { *dst = 0; }
    (void)main();
    for (;;) { __asm volatile("wfi"); }
}

static void uart_init(void)
{
    UART_BAUDDIV = 217u;
    /* The broken version intentionally omits this one operation. */
#if ENABLE_UART_TX
    UART_CTRL = 1u;
#endif
}

static void uart_putc(char ch)
{
    while (UART_STATE & 1u) {
        diagnostic.phase = 3;
        uart_blocked();
    }
    UART_DATA = (uint32_t)(uint8_t)ch; /* 32-bit MMIO, byte payload. */
    diagnostic.tx_attempts++;
}

int main(void)
{
    diagnostic.phase = 1;
    diagnostic.data_ok = initialized_marker == 0x13579bdfu;
    diagnostic.bss_ok = zero_marker == 0;
    if (!diagnostic.data_ok || !diagnostic.bss_ok) {
        diagnostic.phase = 0xe1;
        for (;;) { startup_check_failed(); }
    }
    uart_init();
    diagnostic.phase = 2;
    const char *message = "Firmware started\r\nDATA_OK BSS_OK UART_OK\r\n";
    for (const char *p = message; *p; ++p) { uart_putc(*p); }
    diagnostic.phase = 4;
    firmware_done();
    for (;;) { __asm volatile("wfi"); }
}
