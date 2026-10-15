#!/usr/bin/env python3
"""Build and exercise an original controlled Cortex-M3 UART regression.
No accounts, real-device access, firmware flashing, installs or video rendering.
"""
import argparse
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parent
MESSAGE = b"Firmware started\r\nDATA_OK BSS_OK UART_OK\r\n"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(cmd, target):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
    target.write_bytes(result.stdout)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd}; see {target}")
    return result.stdout.decode(errors="replace")


def build(out, enabled):
    folder = out / ("fixed" if enabled else "broken")
    folder.mkdir()
    (folder / "config.h").write_text(f"#define ENABLE_UART_TX {int(enabled)}\n")
    elf = folder / "firmware.elf"
    cmd = ["arm-none-eabi-gcc", "-mcpu=cortex-m3", "-mthumb", "-Og", "-g3",
           "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
           "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
           "-nostdlib", "-include", str(folder / "config.h"),
           "-T", str(out / "source/linker.ld"),
           f"-Wl,-Map={folder / 'firmware.map'},--build-id=none",
           str(out / "source/firmware.c"), "-o", str(elf)]
    capture(cmd, folder / "build.log")
    capture(["arm-none-eabi-objcopy", "-O", "binary", str(elf), str(folder / "firmware.bin")], folder / "objcopy.log")
    capture(["arm-none-eabi-readelf", "-h", "-l", "-S", "-s", str(elf)], folder / "elf-inspection.txt")
    capture(["arm-none-eabi-objdump", "-d", "-S", str(elf)], folder / "disassembly.txt")
    capture(["arm-none-eabi-gcc", "-mcpu=cortex-m3", "-mthumb", "-E", "-P", "-include",
             str(folder / "config.h"), str(out / "source/firmware.c")], folder / "preprocessed.c")
    nm = capture(["arm-none-eabi-nm", "-n", str(elf)], folder / "symbols.txt")
    symbols = {parts[2]: int(parts[0], 16) for line in nm.splitlines()
               if len(parts := line.split()) == 3 and re.fullmatch(r"[0-9a-fA-F]+", parts[0])}
    section_text = capture(["arm-none-eabi-readelf", "-SW", str(elf)], folder / "sections.txt")
    sections = [{"name": m[0], "kind": m[1], "vma": int(m[2], 16), "size": int(m[4], 16)}
                for m in re.findall(r"\[\s*\d+\]\s+(\.\S+)\s+(PROGBITS|NOBITS)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", section_text)
                if m[0] in [".vectors", ".text", ".data", ".bss"]]
    assert len(sections) == 4
    memory_map = {"source": "actual ELF sections/symbols and this linker script; not inferred by AI",
                  "elf_sha256": digest(elf), "sections": sections,
                  "data_load_address": symbols["_data_load"], "stack_top": symbols["_stack_top"],
                  "reset_handler_symbol": symbols["Reset_Handler"],
                  "linker_subsets": [{"name": "CODE SSRAM subset, not Flash", "base": 0, "bytes": 256*1024},
                                     {"name": "RAM SSRAM subset", "base": 0x20000000, "bytes": 64*1024}],
                  "uart0": {"base": 0x40004000, "data": 0x40004000, "state": 0x40004004,
                            "control": 0x40004008, "bauddiv": 0x40004010},
                  "uart_basis": "upstream v6.2.0 mps2.c and cmsdk-apb-uart.c, plus actual guest/device observations"}
    (folder / "memory_map.json").write_text(json.dumps(memory_map, indent=2))
    metadata = {"kind": "controlled diagnostic", "tx_enabled": enabled, "command": cmd,
                "files": {p.name: digest(p) for p in [elf, folder / "firmware.bin", folder / "firmware.map", folder / "config.h"]}}
    (folder / "build-manifest.json").write_text(json.dumps(metadata, indent=2))
    return folder


def snapshot(point):
    fields = [("pc", "$pc"), ("sp", "$sp"), ("xpsr", "$xpsr"),
              ("vector_sp", "*(unsigned int*)0"), ("vector_reset", "*(unsigned int*)4"),
              ("data", "initialized_marker"), ("data_source", "_data_load"),
              ("bss", "zero_marker"), ("phase", "diagnostic.phase"),
              ("data_ok", "diagnostic.data_ok"), ("bss_ok", "diagnostic.bss_ok"),
              ("tx_attempts", "diagnostic.tx_attempts"),
              ("exception_seen", "diagnostic.exception_seen"),
              ("uart_state", "*(unsigned int*)0x40004004"),
              ("uart_ctrl", "*(unsigned int*)0x40004008"),
              ("uart_bauddiv", "*(unsigned int*)0x40004010")]
    fmt = 'SNAPSHOT {"point":"' + point + '",' + ','.join('"' + k + '":%u' for k, _ in fields) + '}\n'
    return 'printf ' + json.dumps(fmt) + ', ' + ', '.join(v for _, v in fields)


def exercise(out, folder, image_kind, repeat=1):
    name = f"{folder.name}-{image_kind}-{repeat}"
    run = out / "runs" / name
    run.mkdir(parents=True)
    (run / "events.txt").write_text("cmsdk_apb_uart_write\ncmsdk_apb_uart_tx\ncmsdk_apb_uart_reset\n")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    image = folder / f"firmware.{image_kind}"
    cmd = ["qemu-system-arm", "-M", "mps2-an385", "-cpu", "cortex-m3",
           "-kernel", str(image), "-display", "none", "-monitor", "none",
           "-serial", f"file:{run / 'uart.log'}", "-S",
           "-gdb", f"tcp:127.0.0.1:{port}", "-no-reboot",
           "-trace", f"events={run / 'events.txt'},file={run / 'trace.log'}",
           "-d", "in_asm,guest_errors", "-D", str(run / "trace.log")]
    fixed = folder.name == "fixed"
    endpoint = "firmware_done" if fixed else "uart_blocked"
    script = ["set pagination off", "set confirm off", "set print pretty off",
              "set remotetimeout 5", f'file "{folder / "firmware.elf"}"',
              f"target remote 127.0.0.1:{port}", snapshot("reset"),
              "break bss_poisoned", "continue", snapshot("bss_poisoned"), "delete breakpoints",
              "break main", "continue", snapshot("main"), "delete breakpoints",
              "break uart_putc", "continue", snapshot("before_tx"), "delete breakpoints",
              f"break {endpoint}", "continue", snapshot(endpoint), "detach", "quit"]
    (run / "observe.gdb").write_text("\n".join(script) + "\n")
    (run / "command.json").write_text(json.dumps(cmd, indent=2))
    with (run / "qemu.stdout").open("wb") as stdout, (run / "qemu.stderr").open("wb") as stderr:
        process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError(f"QEMU exited early: {run}")
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=.1):
                        break
                except OSError:
                    time.sleep(.03)
            else:
                raise RuntimeError("Local QEMU debugger did not start")
            capture(["gdb-multiarch", "--quiet", "--nx", "--batch", "-x", str(run / "observe.gdb")], run / "gdb.log")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
    samples = [json.loads(line[len("SNAPSHOT "):]) for line in (run / "gdb.log").read_text().splitlines() if line.startswith("SNAPSHOT ")]
    assert [s["point"] for s in samples] == ["reset", "bss_poisoned", "main", "before_tx", endpoint], samples
    reset, poisoned, main, before, final = samples
    assert reset["pc"] | 1 == reset["vector_reset"]
    assert reset["sp"] == reset["vector_sp"] == 0x20010000
    assert reset["data_source"] == 0x13579bdf
    assert reset["data"] == 0, "Loader must not silently initialize runtime .data"
    assert poisoned["bss"] == 0xa5a5a5a5 and poisoned["data"] == 0x13579bdf
    assert main["data"] == 0x13579bdf and main["bss"] == 0
    assert before["data_ok"] == before["bss_ok"] == 1
    assert before["uart_bauddiv"] == 217 and before["uart_state"] == 0
    assert before["uart_ctrl"] == int(fixed)
    assert final["exception_seen"] == 0 and final["xpsr"] & 0x1ff == 0
    assert final["data_ok"] == final["bss_ok"] == 1
    uart = (run / "uart.log").read_bytes()
    trace = (run / "trace.log").read_text()
    writes = [line for line in trace.splitlines() if "cmsdk_apb_uart_write " in line]
    tx = [line for line in trace.splitlines() if "cmsdk_apb_uart_tx " in line]
    if fixed:
        assert uart == MESSAGE, repr(uart)
        assert final["phase"] == 4 and final["tx_attempts"] == len(MESSAGE)
        assert final["uart_state"] == 0 and final["uart_ctrl"] == 1
        assert len(tx) == len(MESSAGE), (len(tx), len(MESSAGE))
        assert len(writes) == len(MESSAGE) + 2
    else:
        assert uart == b"", repr(uart)
        assert final["phase"] == 3 and final["tx_attempts"] == 1
        assert final["uart_state"] & 1 and final["uart_ctrl"] == 0
        assert not tx and len(writes) == 2
    # This QEMU uses the log trace backend: device events and TB disassembly
    # share one real stream. Check that stream, not an empty parallel file.
    assert trace.strip()
    assert not re.search(r"invalid|unimplemented|bad offset|Lockup", trace + (run / "qemu.stderr").read_text(), re.I)
    report = {"run_id": name, "mode": "controlled fault injection", "image": str(image),
              "image_sha256": digest(image), "symbol_elf_sha256": digest(folder / "firmware.elf"),
              "snapshots": samples, "serial_bytes": len(uart), "uart_sha256": digest(run / "uart.log"),
              "device_write_events": len(writes), "device_tx_events": len(tx),
              "verification": "pass", "guest_result": "completed diagnostic" if fixed else "reproduced TX-disabled wait",
              "termination": "host terminates only its own QEMU after debugger observations",
              "trace_scope": "device write/TX events and five debugger snapshots; in_asm is TB translation disassembly, not chronological instruction trace"}
    (run / "observations.json").write_text(json.dumps(report, indent=2))
    print(f"{name}: {report['guest_result']}; UART {len(uart)} bytes; {len(tx)} TX events", flush=True)
    return report


def exercise_without_debugger(out, folder):
    run = out / "runs" / f"{folder.name}-bin-unobserved"
    run.mkdir()
    image = folder / "firmware.bin"
    cmd = ["qemu-system-arm", "-M", "mps2-an385", "-cpu", "cortex-m3",
           "-kernel", str(image), "-display", "none", "-monitor", "none",
           "-serial", "stdio", "-no-reboot"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=2)
        raise RuntimeError(f"Unexpected early QEMU exit: {process.returncode}")
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
    expected = MESSAGE if folder.name == "fixed" else b""
    assert stdout == expected, repr(stdout)
    assert not re.search(rb"invalid|unimplemented|bad offset|Lockup", stderr, re.I)
    (run / "uart.log").write_bytes(stdout)
    (run / "qemu.stderr").write_bytes(stderr)
    record = {"command": cmd, "image_sha256": digest(image), "serial_bytes": len(stdout),
              "debugger_attached": False, "host_observation_seconds": 2,
              "termination": "expected host stop after bounded observation; not a guest success exit code",
              "verification": "pass: serial output matches observed counterpart"}
    (run / "observations.json").write_text(json.dumps(record, indent=2))
    print(f"{folder.name}-bin-unobserved: UART {len(stdout)} bytes, no debugger", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = (args.output or ROOT / "artifacts" / datetime.datetime.now(datetime.timezone.utc).strftime("session-%Y%m%dT%H%M%S%fZ")).resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "source").mkdir()
    for filename in ["firmware.c", "linker.ld", "run_lab.py"]:
        shutil.copy2(ROOT / filename, out / "source" / filename)
    versions = {}
    for name, cmd in {"qemu": ["qemu-system-arm", "--version"], "gcc": ["arm-none-eabi-gcc", "--version"], "gdb": ["gdb-multiarch", "--version"]}.items():
        versions[name] = capture(cmd, out / f"{name}-version.txt").splitlines()[0]
    versions["binary_sha256"] = {tool: digest(shutil.which(tool)) for tool in ["qemu-system-arm", "arm-none-eabi-gcc", "gdb-multiarch"]}
    broken = build(out, False)
    fixed = build(out, True)
    diff = ''.join(difflib.unified_diff((broken / "config.h").read_text().splitlines(True), (fixed / "config.h").read_text().splitlines(True), fromfile="broken/config.h", tofile="fixed/config.h"))
    (out / "fix.patch").write_text(diff)
    (out / "compiled-source.patch").write_text(''.join(difflib.unified_diff((broken / "preprocessed.c").read_text().splitlines(True), (fixed / "preprocessed.c").read_text().splitlines(True), fromfile="broken/preprocessed.c", tofile="fixed/preprocessed.c")))
    runs = [exercise(out, broken, "elf"), exercise(out, fixed, "elf"),
            exercise(out, broken, "bin"), exercise(out, fixed, "bin"), exercise(out, fixed, "elf", 2)]
    unobserved = [exercise_without_debugger(out, broken), exercise_without_debugger(out, fixed)]
    summary = {"machine": "mps2-an385", "cpu": "cortex-m3", "versions": versions,
               "unobserved_runs": unobserved,
               "source_sha256": {p.name: digest(p) for p in (out / "source").iterdir()},
               "runs": runs, "result": "controlled regression passed: 5 observed runs plus 2 without debugger",
               "scope": "original diagnostic: vector entry, data copy, poisoned-BSS clearing, UART0 TX and host character backend",
               "not_verified": ["BK7258 or any product firmware", "RTEMS", "full boot chain/security", "physical board", "electrical timing/performance", "multiple independent Agents"]}
    (out / "environment_manifest.json").write_text(json.dumps({"machine": summary["machine"], "cpu": summary["cpu"],
        "versions": versions, "observed_commands": [str(p.relative_to(out)) for p in sorted((out / "runs").glob("*/command.json"))],
        "serial_backend": "UART0 host file backend for observed runs; stdio for independent runs",
        "sampling": "five GDB checkpoints; device write/TX events; TB translation disassembly",
        "scope": summary["scope"], "not_verified": summary["not_verified"]}, indent=2))
    (out / "validation.json").write_text(json.dumps(summary, indent=2))
    (ROOT / "latest-run.json").write_text(json.dumps({"path": str(out), "result": summary["result"]}, indent=2))
    print(f"ARTIFACTS={out}", flush=True)


if __name__ == "__main__":
    main()
