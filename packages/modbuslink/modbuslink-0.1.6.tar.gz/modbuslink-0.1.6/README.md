# ModbusLink

English [中文版](README-zh_CN.md)

A modern, powerful, developer-friendly and highly extensible Python Modbus library.

## Features

- **Layered Architecture**: Strict separation of transport layer, client and utility layers
- **Interface-Oriented Programming**: Use abstract base classes to define unified interfaces
- **Dependency Injection**: Client receives transport layer instances through constructor
- **User-Friendly**: All external interfaces use Python native data types
- **Synchronous Support**: Complete synchronous Modbus client implementation
- **Multiple Transport Methods**: Support RTU (serial port) and TCP transport

## Quick Start

### Installation

```bash
pip install modbuslink
```

### RTU Example

```python
from modbuslink import ModbusClient, RtuTransport

# Create RTU transport layer
transport = RtuTransport(
    port='COM1',        # Windows
    # port='/dev/ttyUSB0',  # Linux
    baudrate=9600,
    timeout=1.0
)

# Create client
client = ModbusClient(transport)

# Use context manager to automatically manage connections
with client:
    # Read holding registers
    registers = client.read_holding_registers(
        slave_id=1,
        start_address=0,
        quantity=4
    )
    print(f"Register values: {registers}")
    
    # Write single register
    client.write_single_register(
        slave_id=1,
        address=0,
        value=1234
    )
    
    # Read coil status
    coils = client.read_coils(
        slave_id=1,
        start_address=0,
        quantity=8
    )
    print(f"Coil status: {coils}")
```

### TCP Example

```python
from modbuslink import ModbusClient, TcpTransport

# Create TCP transport layer
transport = TcpTransport(
    host='192.168.1.100',
    port=502,
    timeout=10.0
)

# Create client
client = ModbusClient(transport)

# Use context manager to automatically manage connections
with client:
    # Read input registers
    registers = client.read_input_registers(
        slave_id=1,
        start_address=0,
        quantity=10
    )
    print(f"Input registers: {registers}")
    
    # Write multiple registers
    client.write_multiple_registers(
        slave_id=1,
        start_address=0,
        values=[100, 200, 300, 400]
    )
```

## Supported Function Codes

- **0x01**: Read Coil Status
- **0x02**: Read Discrete Input Status
- **0x03**: Read Holding Registers
- **0x04**: Read Input Registers
- **0x05**: Write Single Coil
- **0x06**: Write Single Register
- **0x0F**: Write Multiple Coils
- **0x10**: Write Multiple Registers

## Exception Handling

```python
from modbuslink import (
    ModbusClient, RtuTransport,
    ConnectionError, TimeoutError, CRCError, ModbusException
)

transport = RtuTransport('COM1')
client = ModbusClient(transport)

try:
    with client:
        registers = client.read_holding_registers(1, 0, 4)
except ConnectionError as e:
    print(f"Connection error: {e}")
except TimeoutError as e:
    print(f"Timeout error: {e}")
except CRCError as e:
    print(f"CRC validation error: {e}")
except ModbusException as e:
    print(f"Modbus protocol exception: {e}")
```

## Project Structure

```
ModbusLink/
├── src/modbuslink/          # Main source code
│   ├── __init__.py          # Main export interface
│   ├── client/              # Client module
│   │   ├── __init__.py
│   │   ├── sync_client.py   # Synchronous client implementation
│   │   └── async_client.py  # Asynchronous client implementation
│   ├── transport/           # Transport layer module
│   │   ├── __init__.py
│   │   ├── base.py         # Transport layer abstract base class
│   │   ├── async_base.py   # Async transport layer abstract base class
│   │   ├── rtu.py          # RTU transport layer implementation
│   │   ├── tcp.py          # TCP transport layer implementation
│   │   └── async_tcp.py    # Async TCP transport layer implementation
│   ├── utils/               # Utility module
│   │   ├── __init__.py
│   │   ├── crc.py          # CRC16 validation tool
│   │   ├── payload_coder.py # Data encoding/decoding utilities
│   │   └── logger.py       # Unified logging system
│   └── common/              # Common module
│       ├── __init__.py
│       └── exceptions.py    # Exception definitions
├── examples/                # Usage examples
│   ├── __init__.py
│   ├── rtu_example.py       # RTU usage example
│   ├── tcp_example.py       # TCP usage example
│   └── async_tcp_example.py # Async TCP example
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation
└── LICENSE.txt              # License
```

## Development Notes

The project adopts a layered architecture design, strictly separating transport layer, client and utility layers, providing clear interfaces and good extensibility.

## Stage 2 Features

Stage 2 primarily enhances the usability and developer experience of ModbusLink library, adding advanced data type support and a unified logging system.

### Advanced Data Type Support

#### Data Encoder/Decoder

Added `PayloadCoder` class providing encoding/decoding functionality for various data types:

```python
from modbuslink.utils import PayloadCoder

# 32-bit float
registers = PayloadCoder.encode_float32(3.14159, 'big', 'high')
value = PayloadCoder.decode_float32(registers, 'big', 'high')

# 32-bit integer
registers = PayloadCoder.encode_int32(123456789, 'big', 'high')
value = PayloadCoder.decode_int32(registers, 'big', 'high')

# String
registers = PayloadCoder.encode_string("Hello ModbusLink")
value = PayloadCoder.decode_string(registers, 16)
```

#### Supported Data Types

- **32-bit float** `float32`: IEEE 754 single precision floating point
- **32-bit signed integer** `int32`: -2,147,483,648 to 2,147,483,647
- **32-bit unsigned integer** `uint32`: 0 to 4,294,967,295
- **64-bit signed integer** `int64`: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
- **64-bit unsigned integer** `uint64`: 0 to 18,446,744,073,709,551,615
- **String** `string`: UTF-8 encoded text data

#### Byte Order and Word Order Support

Supports different byte order (endianness) and word order:

- **Byte Order**: `'big'` (big-endian) or `'little'` (little-endian)
- **Word Order**: `'high'` (high word first) or `'low'` (low word first)

### Client Advanced API

Added advanced data type read/write methods to `ModbusClient` class:

```python
from modbuslink.client import ModbusClient
from modbuslink.transport import TcpTransport

client = ModbusClient(TcpTransport('192.168.1.100', 502))

with client:
    # Read/write 32-bit float
    client.write_float32(slave_id=1, start_address=100, value=25.6)
    temperature = client.read_float32(slave_id=1, start_address=100)
    
    # Read/write 32-bit integer
    client.write_int32(slave_id=1, start_address=102, value=123456789)
    counter = client.read_int32(slave_id=1, start_address=102)
    
    # Read/write string
    client.write_string(slave_id=1, start_address=110, value="ModbusLink")
    device_name = client.read_string(slave_id=1, start_address=110, length=10)
```

#### Available Advanced API Methods

- `read_float32()` / `write_float32()`: 32-bit float
- `read_int32()` / `write_int32()`: 32-bit signed integer
- `read_uint32()` / `write_uint32()`: 32-bit unsigned integer
- `read_int64()` / `write_int64()`: 64-bit signed integer
- `read_uint64()` / `write_uint64()`: 64-bit unsigned integer
- `read_string()` / `write_string()`: String

### Unified Logging System

#### Logging Configuration

Added `ModbusLogger` class providing unified logging configuration:

```python
from modbuslink.utils import ModbusLogger
import logging

# Configure logging system
ModbusLogger.setup_logging(
    level=logging.INFO,     # Log level
    enable_debug=True,      # Enable debug mode
    log_file='modbus.log'   # Optional: output to file
)

# Enable protocol-level debugging
ModbusLogger.enable_protocol_debug()

# Get logger
logger = ModbusLogger.get_logger('my_module')
logger.info("This is an info log")
```

#### Log Levels

- `DEBUG`: Detailed debugging information, including protocol-level raw data
- `INFO`: General information, such as connection status, operation results
- `WARNING`: Warning information, such as timeout retries
- `ERROR`: Error information, such as connection failures, protocol errors

#### Protocol Debugging

When protocol debugging is enabled, you can view raw Modbus messages:

```
2024-01-15 10:30:15,123 - transport.tcp - DEBUG - Sending: 00 01 00 00 00 06 01 03 00 00 00 0A
2024-01-15 10:30:15,125 - transport.tcp - DEBUG - Received: 00 01 00 00 00 17 01 03 14 00 01 00 02 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A
```

### Compatibility Notes

- All new features are backward compatible
- Existing basic APIs remain unchanged
- New advanced APIs are optional
- Logging system is disabled by default

## Stage 3 Features

Stage 3 introduces modern asynchronous programming support, callback mechanisms, and Modbus slave simulation capabilities.

### Async Transport and Client

#### Async TCP Transport

```python
from modbuslink import AsyncModbusClient, AsyncTcpTransport
import asyncio

# Create async TCP transport
transport = AsyncTcpTransport(
    host='192.168.1.100',
    port=502,
    timeout=10.0
)

# Create async client
client = AsyncModbusClient(transport)

async def main():
    async with client:
        # Async read holding registers
        registers = await client.read_holding_registers(
            slave_id=1,
            start_address=0,
            quantity=10
        )
        print(f"Registers: {registers}")
        
        # Async write multiple registers
        await client.write_multiple_registers(
            slave_id=1,
            start_address=0,
            values=[100, 200, 300, 400]
        )

asyncio.run(main())
```

#### Async Advanced Data Types

```python
async def advanced_operations():
    async with client:
        # Async 32-bit float operations
        await client.write_float32(slave_id=1, start_address=100, value=3.14159)
        temperature = await client.read_float32(slave_id=1, start_address=100)
        
        # Async 32-bit integer operations
        await client.write_int32(slave_id=1, start_address=102, value=-123456)
        counter = await client.read_int32(slave_id=1, start_address=102)
```

### Callback Mechanism

Async client supports callback functions for operation completion notifications:

```python
def on_registers_read(registers):
    print(f"Callback: Read {len(registers)} registers")

def on_write_completed():
    print("Callback: Write operation completed")

async def callback_demo():
    async with client:
        # Read with callback
        registers = await client.read_holding_registers(
            slave_id=1,
            start_address=0,
            quantity=5,
            callback=on_registers_read
        )
        
        # Write with callback
        await client.write_single_register(
            slave_id=1,
            address=0,
            value=1234,
            callback=on_write_completed
        )
```

### Concurrent Operations

Async client supports concurrent operations for improved performance:

```python
async def concurrent_operations():
    async with client:
        # Create multiple concurrent tasks
        tasks = [
            client.read_holding_registers(slave_id=1, start_address=0, quantity=5),
            client.read_coils(slave_id=1, start_address=0, quantity=8),
            client.read_input_registers(slave_id=1, start_address=0, quantity=5),
            client.write_single_register(slave_id=1, address=100, value=9999),
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        print(f"Concurrent results: {results}")
```

### Async Client Features Summary

The async client provides the following key features:

- **Asynchronous Operations**: All Modbus operations support asynchronous execution
- **Callback Mechanism**: Support for callback notifications after operation completion
- **Concurrent Processing**: Can execute multiple Modbus operations simultaneously
- **Advanced Data Types**: Support for asynchronous operations with 32-bit floats, integers and other advanced data types
- **Context Management**: Support for async with syntax for automatic connection management

## Development Plan

- [x] **Phase 1**: Build a solid and reliable core foundation (synchronous MVP)
- [x] **Phase 2**: Improve usability and developer experience
- [x] **Phase 3**: Embrace modernization: asynchronous programming support
- [ ] **Phase 4**: Release, optimization and community ecosystem

## License

MIT License - See [LICENSE.txt](LICENSE.txt) for details

## Contributing

Issues and Pull Requests are welcome!