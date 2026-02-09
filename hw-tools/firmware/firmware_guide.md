# GPU Firmware Basics

**Programming the flux GPU at the lowest level**

---

## What is Firmware?

**Definition**: Software that directly controls hardware, stored in ROM/Flash on the device.

**In GPUs**:
- **BIOS/VBIOS**: Basic initialization code
- **Microcode**: Low-level instruction sequences
- **Driver firmware**: Commands sent from CPU to GPU

---

## The Boot Process

### What Happens When GPU Powers On?

```
1. Power-on → Reset signal
   ↓
2. ROM bootloader executes
   ↓
3. Initialize memory controller
   ↓
4. Load firmware from Flash/VRAM
   ↓
5. Initialize shader cores
   ↓
6. Wait for commands from CPU
```

**In flux GPU**: Simplified (no BIOS needed for now)

---

## Firmware Architecture

### Layers

```
┌────────────────────────────┐
│   Application (User)       │  ← Python/C++ code
├────────────────────────────┤
│   Driver (Kernel module)   │  ← OS interface
├────────────────────────────┤
│   Command Processor        │  ← Parse commands
├────────────────────────────┤
│   Microcode / Firmware     │  ← This guide!
├────────────────────────────┤
│   Hardware (RTL)           │  ← flux shader core
└────────────────────────────┘
```

---

## flux Firmware Examples

### Example 1: Load Program to Instruction Memory

**Task**: Write assembly program to GPU memory

```python
# load_program.py
import struct

def load_program(program_hex, base_addr=0x0000):
    """
    Load assembled program into GPU instruction memory
    
    Args:
        program_hex: Path to .hex file from assembler
        base_addr: Starting address in instruction memory
    """
    instructions = []
    
    # Read hex file
    with open(program_hex, 'r') as f:
        for line in f:
            instr = int(line.strip(), 16)
            instructions.append(instr)
    
    # Create memory image (little-endian)
    mem_image = bytearray()
    for instr in instructions:
        mem_image.extend(instr.to_bytes(4, byteorder='little'))
    
    # In real GPU: Send via PCIe to device memory
    # For flux: Load into simulation/FPGA BRAM
    return mem_image

def write_to_fpga(mem_image, uart_port='/dev/ttyUSB0'):
    """Send program to FPGA via UART"""
    import serial
    
    ser = serial.Serial(uart_port, 115200, timeout=1)
    
    # Protocol: <START><LENGTH><DATA><CHECKSUM>
    packet = bytearray()
    packet.append(0xAA)  # Start marker
    packet.extend(len(mem_image).to_bytes(4, 'little'))
    packet.extend(mem_image)
    
    # Simple checksum
    checksum = sum(mem_image) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    
    # Wait for ACK
    ack = ser.read(1)
    if ack == b'\x06':
        print("✓ Program loaded successfully")
    else:
        print("✗ Error loading program")
    
    ser.close()

# Usage
if __name__ == "__main__":
    mem = load_program("vecadd.hex")
    write_to_fpga(mem)
```

---

### Example 2: Initialize Registers

**Task**: Set up initial register state before execution

```python
# init_registers.py

def init_register_file(thread_id=0):
    """
    Initialize registers for a thread
    Returns list of register values (32 regs × 128 bits)
    """
    registers = []
    
    # R0 = 0 (hardwired)
    registers.append([0.0, 0.0, 0.0, 0.0])
    
    # R10, R11, R12 = pointers to A, B, C arrays
    registers += [[0.0]*4] * 9  # R1-R9 unused
    registers.append([0x1000, 0, 0, 0])  # R10 = &A
    registers.append([0x2000, 0, 0, 0])  # R11 = &B
    registers.append([0x3000, 0, 0, 0])  # R12 = &C
    
    # R13-R31 = 0
    registers += [[0.0]*4] * 19
    
    return registers

def pack_register_value(float_vec):
    """Pack 4× FP32 into 128-bit value"""
    packed = bytearray()
    for f in float_vec:
        packed.extend(struct.pack('f', f))
    return packed

def send_register_init(thread_id, registers):
    """Send register initialization commands"""
    for reg_idx, value in enumerate(registers):
        cmd = bytearray()
        cmd.append(0xA0)  # WRITE_REG command
        cmd.append(thread_id)
        cmd.append(reg_idx)
        cmd.extend(pack_register_value(value))
        # Send cmd via UART/PCIe
        print(f"T{thread_id} R{reg_idx} = {value}")
```

---

### Example 3: Start Execution

**Task**: Tell GPU to start executing loaded program

```python
# execute.py

def start_execution(thread_mask=0x00000001):
    """
    Start shader core execution
    
    Args:
        thread_mask: Bitmap of which threads to run (bit 0 = thread 0)
    """
    cmd = bytearray()
    cmd.append(0xB0)  # START command
    cmd.extend(thread_mask.to_bytes(4, 'little'))
    
    # Send command
    send_command(cmd)
    
    print(f"✓ Started threads: {bin(thread_mask)}")

def wait_for_halt():
    """Poll until GPU signals HALT"""
    import time
    
    while True:
        status = read_status_register()
        if status & 0x01:  # Halt bit
            print("✓ Execution complete")
            break
        time.sleep(0.001)  # 1ms poll

def read_results():
    """Read back results from memory"""
    # Read memory region 0x3000 (where output is stored)
    cmd = bytearray()
    cmd.append(0xC0)  # READ_MEM command
    cmd.extend((0x3000).to_bytes(4, 'little'))
    cmd.extend((16).to_bytes(2, 'little'))  # 16 bytes
    
    send_command(cmd)
    data = receive_response(16)
    
    # Unpack 4× FP32
    result = struct.unpack('ffff', data)
    print(f"Results: {result}")
    return result
```

---

### Example 4: Complete Workflow

```python
# run_program.py

def run_gpu_program(assembly_file):
    """
    Complete workflow: Assemble → Load → Execute → Read Results
    """
    # 1. Assemble
    os.system(f"python sw-toolchain/asm/assembler.py {assembly_file}")
    hex_file = assembly_file.replace('.s', '.hex')
    
    # 2. Load program
    mem_image = load_program(hex_file)
    write_to_fpga(mem_image)
    
    # 3. Initialize registers  
    regs = init_register_file(thread_id=0)
    send_register_init(0, regs)
    
    # 4. Load input data to memory
    init_memory(0x1000, [1.0, 2.0, 3.0, 4.0])  # Array A
    init_memory(0x2000, [5.0, 6.0, 7.0, 8.0])  # Array B
    
    # 5. Start execution
    start_execution(thread_mask=0x01)  # Just thread 0
    
    # 6. Wait for completion
    wait_for_halt()
    
    # 7. Read results
    results = read_results()
    print(f"Final output: {results}")
    
    return results

# Usage
if __name__ == "__main__":
    run_gpu_program("sw-toolchain/examples/vecadd.s")
    # Expected output: [6.0, 8.0, 10.0, 12.0]
```

---

## Command Protocol

### Minimal GPU Command Set

| Command | Code | Args | Description |
|---------|------|------|-------------|
| WRITE_MEM | 0x90 | addr, len, data | Write to memory |
| READ_MEM | 0xC0 | addr, len | Read from memory |
| WRITE_REG | 0xA0 | tid, rid, value | Write register |
| READ_REG | 0xA1 | tid, rid | Read register |
| LOAD_PROG | 0x80 | addr, len, code | Load instructions |
| START | 0xB0 | thread_mask | Start execution |
| HALT_CHECK | 0xB1 | - | Check if halted |
| RESET | 0xFF | - | Reset GPU |

**Packet Format**:
```
[START] [CMD] [LENGTH] [DATA...] [CHECKSUM]
  0xAA   1B      2B      N bytes     1B
```

---

## FPGA UART Firmware Handler

**Verilog module to receive firmware commands**:

```systemverilog
// uart_command_handler.sv
module uart_command_handler (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  rx_data,
    input  wire        rx_valid,
    output reg  [31:0] mem_addr,
    output reg  [127:0] mem_data,
    output reg         mem_write
);

    typedef enum {
        IDLE, CMD, LEN, DATA, EXEC
    } state_t;
    
    state_t state;
    reg [7:0] command;
    reg [15:0] length;
    reg [15:0] count;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else if (rx_valid) begin
            case (state)
                IDLE: if (rx_data == 8'hAA) state <= CMD;
                CMD:  begin
                    command <= rx_data;
                    state <= LEN;
                end
                LEN: begin
                    length <= {length[7:0], rx_data};
                    state <= DATA;
                    count <= 0;
                end
                DATA: begin
                    // Store data based on command
                    if (command == 8'h90) begin  // WRITE_MEM
                        mem_data <= {mem_data[119:0], rx_data};
                        if (count == 15) mem_write <= 1;
                    end
                    count <= count + 1;
                    if (count == length - 1) state <= IDLE;
                end
            endcase
        end else begin
            mem_write <= 0;
        end
    end

endmodule
```

---

## Debugging Firmware

### Common Issues

**1. Program doesn't start**
- Check: Program loaded correctly?
- Check: PC initialized to 0?
- Debug: Read back instruction memory

**2. Wrong results**
- Check: Input data loaded?
- Check: Register pointers correct?
- Debug: Single-step execution

**3. GPU hangs**
- Check: Infinite loop in program?
- Check: HALT instruction present?
- Debug: Add timeout

### Debug Commands

```python
def dump_registers(thread_id):
    """Read all 32 registers for debugging"""
    for i in range(32):
        cmd = make_cmd(0xA1, thread_id, i)
        val = send_and_receive(cmd)
        print(f"R{i} = {val}")

def dump_memory(addr, size):
    """Dump memory region"""
    cmd = make_cmd(0xC0, addr, size)
    data = send_and_receive(cmd)
    for i in range(0, len(data), 16):
        print(f"0x{addr+i:04x}: {data[i:i+16].hex()}")
```

---

## Performance Monitoring

### Add Counters

```python
def read_perf_counters():
    """Read performance statistics"""
    counters = {
        'instructions': read_counter(0x1000),
        'mem_reads': read_counter(0x1004),
        'mem_writes': read_counter(0x1008),
        'cycles': read_counter(0x100C),
    }
    return counters

def print_stats(counters):
    ipc = counters['instructions'] / counters['cycles']
    print(f"Instructions: {counters['instructions']}")
    print(f"Cycles: {counters['cycles']}")
    print(f"IPC: {ipc:.2f}")
```

---

## Putting It All Together

### Simple Test Program

**1. Write assembly**:
```assembly
# test.s
LI R1, 42
HALT
```

**2. Assemble**:
```bash
python sw-toolchain/asm/assembler.py test.s
```

**3. Run firmware**:
```python
from firmware import *
run_gpu_program("test.s")
dump_registers(0)  # Should show R1 = 42
```

---

## Next Steps

1. **Implement Command Handler**: Add to `gpu_top.sv`
2. **Create Python Driver**: Complete firmware library
3. **Add UART/PCIe Interface**: Hardware communication
4. **Test on FPGA**: Load bitstream, run programs
5. **Profile Performance**: Measure actual IPC

---

## Key Takeaways

✅ **Firmware** = Low-level software controlling hardware  
✅ **Commands**: Load, execute, read results  
✅ **Protocol**: Simple packet format  
✅ **Debugging**: Dump registers/memory  
✅ **Integration**: Python → UART → FPGA → GPU  

---

**Further Reading**:
- NVIDIA CUDA Driver API
- Vulkan Command Buffers
- flux codebase: `rtl/src/gpu_top.sv` (add command interface here!)
