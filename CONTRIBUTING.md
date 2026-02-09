# Contributing to flux GPU

**Thank you for your interest in contributing!** 🎉

flux is a community project, and we welcome contributions of all kinds.

---

## Quick Links

- 📖 [Code of Conduct](CODE_OF_CONDUCT.md)
- 🐛 [Report a Bug](https://github.com/dibyx/flux/issues/new?template=bug_report.md)
- 💡 [Request a Feature](https://github.com/dibyx/flux/issues/new?template=feature_request.md)
- 💬 [Discussions](https://github.com/dibyx/flux/discussions)

---

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please [create an issue](https://github.com/dibyx/flux/issues/new?template=bug_report.md).

**Good bug reports include**:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or screenshots

### 2. Suggest Features

Have an idea? [Open a feature request](https://github.com/dibyx/flux/issues/new?template=feature_request.md).

**Good feature requests include**:
- Use case (why is this needed?)
- Proposed solution
- Alternatives considered
- Willingness to implement

### 3. Improve Documentation

Documentation improvements are always welcome!

**Areas that need help**:
- Fix typos and grammar
- Clarify confusing sections
- Add examples
- Translate to other languages
- Create tutorials

**To contribute docs**:
1. Edit the `.md` files in `docs/`
2. Submit a pull request
3. No code required!

### 4. Write Code

Ready to code? Great!

**Good first issues** are labeled `good-first-issue` in the issue tracker.

**Areas to contribute**:
- Bug fixes
- New instructions (ISA extensions)
- Toolchain improvements (assembler, simulator)
- RTL enhancements (hardware)
- Examples and demos
- Test coverage

---

## Development Setup

### Prerequisites

```bash
# Required
python >= 3.7
git

# Optional (for hardware)
verilator
cocotb
yosys
```

### Clone Repository

```bash
git clone https://github.com/dibyx/flux.git
cd flux
```

### Run Tests

```bash
# Software tests
python sw-toolchain/asm/assembler.py --test
python sw-toolchain/sim/simulator.py --test

# Hardware tests (if cocotb installed)
cd rtl/test
pytest test_shader_core.py -v
```

---

## Coding Standards

### Python Code

**Style**: PEP 8

```python
# Good
def assemble_instruction(opcode, rd, rs1, rs2):
    """Assemble R-type instruction.
    
    Args:
        opcode: 7-bit opcode
        rd: Destination register (0-31)
        rs1: Source register 1 (0-31)
        rs2: Source register 2 (0-31)
    
    Returns:
        32-bit encoded instruction
    """
    instruction = 0
    instruction |= (opcode & 0x7F)
    instruction |= (rd & 0x1F) << 7
    # ... etc
    return instruction
```

**Key points**:
- Docstrings for all public functions
- Type hints encouraged
- Clear variable names
- Comments for non-obvious logic

### SystemVerilog/Verilog Code

**Style**: Industry standard

```systemverilog
// Good
module shader_core (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] instruction,
    output reg  [127:0] result
);
    // Clear signal names
    wire [6:0] opcode = instruction[6:0];
    wire [4:0] rd = instruction[11:7];
    
    // Commented state machines
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            case (state)
                IDLE: // ...
                // etc
            endcase
    end
endmodule
```

**Key points**:
- Synchronous design (avoid latches)
- No blocking assignments in sequential blocks
- Clear module interfaces
- Comments for complex logic

### Documentation

**Markdown style**:
- Clear headers
- Short paragraphs (2-4 sentences)
- Code blocks with syntax highlighting
- Examples for complex concepts
- Links to related docs

---

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `test/` - Test improvements

### 2. Make Changes

- Write code
- Add tests (if applicable)
- Update documentation
- Commit with clear messages

**Commit message format**:
```
category: Short description (50 chars max)

Longer explanation if needed. Wrap at 72 characters.
Explain WHY, not just what changed.

Fixes #123
```

**Examples**:
```
asm: Add support for MAD instruction

Implement multiply-add (MAD) instruction in assembler.
Updates ISA encoding, adds tests, documents in spec.

Closes #45
```

```
docs: Fix typo in rasterization guide

Changed "verticies" to "vertices" in triangle example.
```

### 3. Run Tests

```bash
# Before submitting:
make test-all    # Run all tests
make lint        # Check code style
```

### 4. Submit Pull Request

- Push your branch
- Open PR on GitHub
- Fill out PR template
- Link related issues
- Request review

**PR title format**:
```
[Category] Short description
```

**Examples**:
- `[Feature] Add texture mapping support`
- `[Fix] Correct edge function calculation`
- `[Docs] Improve getting started guide`

### 5. Code Review

- Address reviewer comments
- Push fixes to same branch
- Be patient and respectful
- Learn from feedback!

### 6. Merge

Once approved:
- Maintainer will merge
- Branch auto-deleted
- Your contribution is live! 🎉

---

## Testing Guidelines

### Unit Tests

**Required for**:
- New features
- Bug fixes
- Modified algorithms

**Python tests**:
```python
# test_assembler.py
def test_add_instruction():
    """Test ADD instruction encoding."""
    result = encode_instruction('ADD', 3, 1, 2)
    expected = 0x002080B3
    assert result == expected, f"Got {result:08X}, expected {expected:08X}"
```

**RTL tests** (Cocotb):
```python
# test_shader_core.py
@cocotb.test()
async def test_add_operation(dut):
    """Test SIMD ADD operation."""
    # Setup
    dut.instruction.value = 0x002080B3
    await ClockCycles(dut.clk, 1)
    
    # Verify
    expected = [6.0, 8.0, 10.0, 12.0]
    assert dut.result.value == expected
```

### Integration Tests

Test complete workflows:
```bash
# Example: Full assembly workflow
python sw-toolchain/asm/assembler.py example.s
python sw-toolchain/sim/simulator.py example.hex
# Verify output matches expected
```

---

## Documentation Guidelines

### Structure

**Every feature needs**:
1. API documentation (docstrings)
2. User guide (markdown)
3. Example usage
4. Tests

### Writing Style

**Good**:
- Clear and concise
- Examples with code
- Step-by-step instructions
- Visual aids (diagrams, screenshots)

**Avoid**:
- Jargon without explanation
- Walls of text
- Missing examples
- Outdated information

### Code Examples

Always test your examples:
```python
# This should be copy-paste runnable
from firmware_driver import FluxGPU

gpu = FluxGPU(interface='simulation')
gpu.draw_triangle((100,100), (400,100), (250,300), 0xFF0000)
# Output: Triangle drawn successfully
```

---

## Community Guidelines

### Be Respectful

- Assume good intentions
- Be constructive in criticism
- Welcome newcomers
- Give credit where due

### Be Patient

- Reviewers are volunteers
- Response may take days
- Not all PRs will be merged
- Learn from rejections

### Be Collaborative

- Discuss before big changes
- Share knowledge
- Help others
- Improve existing code

---

## Recognition

**Contributors are recognized**:
- Listed in README
- Mentioned in release notes
- GitHub contributor badge
- Our eternal gratitude! 🙏

---

## License

By contributing, you agree that your contributions will be licensed under:
- Hardware: CERN-OHL-S v2
- Software: Apache 2.0
- Documentation: CC-BY-SA 4.0

See [LICENSE](LICENSE) for details.

---

## Questions?

- 📧 Email: concealment960@gmail.com
- 💬 GitHub: https://github.com/dibyx
- 🐛 Issues: https://github.com/dibyx/flux/issues
- 💻 LeetCode: https://leetcode.com/u/gahjqjjwuhujqjj/

**Thank you for making flux better!** 🚀
