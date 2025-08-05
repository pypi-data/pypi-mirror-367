# Corne Keyboard Configuration

This directory contains the configuration for the **Corne Cherry v3** keyboard, a popular 42-key split ergonomic keyboard designed by foostan.

## Keyboard Specifications

- **Name**: Corne Cherry v3
- **Designer**: foostan
- **Key Count**: 42 keys (21 per side)
- **Layout**: 3x6 column-staggered layout with 3 thumb keys per side
- **Connectivity**: Wireless (Bluetooth) via nice!nano controller

## Key Layout

```
┌─────┬─────┬─────┬─────┬─────┬─────┐       ┌─────┬─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │  5  │       │  6  │  7  │  8  │  9  │ 10  │ 11  │
├─────┼─────┼─────┼─────┼─────┼─────┤       ├─────┼─────┼─────┼─────┼─────┼─────┤
│ 12  │ 13  │ 14  │ 15  │ 16  │ 17  │       │ 18  │ 19  │ 20  │ 21  │ 22  │ 23  │
├─────┼─────┼─────┼─────┼─────┼─────┤       ├─────┼─────┼─────┼─────┼─────┼─────┤
│ 24  │ 25  │ 26  │ 27  │ 28  │ 29  │       │ 30  │ 31  │ 32  │ 33  │ 34  │ 35  │
└─────┴─────┴─────┼─────┼─────┼─────┤       ├─────┼─────┼─────┼─────┴─────┴─────┘
                  │ 36  │ 37  │ 38  │       │ 39  │ 40  │ 41  │
                  └─────┴─────┴─────┘       └─────┴─────┴─────┘
```

## Available Firmware Versions

- **main** - Latest ZMK firmware from main branch (bleeding edge)
- **v3.5** - ZMK firmware v3.5 stable release
- **v3.2** - ZMK firmware v3.2 stable release

## Flash Methods

### Primary: USB Bootloader Flash
- **Device Query**: Detects Adafruit nRF52 bootloader devices
- **Mount Timeout**: 30 seconds
- **Copy Timeout**: 60 seconds
- **Sync After Copy**: Enabled for data integrity

### Fallback: DFU Flash
- **VID**: 0x1209 (ZMK Project)
- **PID**: 0x0514 (Corne)
- **Interface**: 0
- **Timeout**: 30 seconds

## Build Configuration

- **Method**: Generic Docker compiler with ZMK west workspace
- **Build Strategy**: `west` (ZMK recommended)
- **Image**: `zmkfirmware/zmk-build-arm:stable`
- **Workspace Caching**: Enabled for faster builds (50%+ improvement)
- **Board Targets**: `corne_left`, `corne_right` for split keyboard
- **West Workspace**: ZMK main branch with automatic dependency management
- **Parallel Jobs**: 4
- **Fallback**: Docker legacy → Local compilation

## Generic Docker Compiler Features

### Modern ZMK West Workspace Build
- **West Workspace**: Full ZMK west workspace initialization and management
- **Dependency Management**: Automatic ZMK and Zephyr dependency resolution
- **Intelligent Caching**: Workspace caching for 50%+ faster subsequent builds
- **Cache Invalidation**: Automatic cache invalidation on configuration changes
- **Multi-Strategy Support**: west, cmake, make, ninja build strategies

### Performance Optimizations
- **Workspace Caching**: Reuses ZMK workspace across builds with smart invalidation
- **Parallel Builds**: Multi-core compilation support with configurable job count
- **Optimized Volumes**: Efficient Docker volume mounting and management
- **Build Strategy Selection**: Automatic selection of optimal build method

### Split Keyboard Support
- **Board Targets**: Explicit board target configuration (`corne_left`, `corne_right`)
- **Synchronized Builds**: Coordinated compilation for both keyboard halves
- **Environment Templates**: Configurable build environment variables

## Key Features

### Bluetooth Configuration
- 3 Bluetooth profiles for device switching
- Low-latency split communication (30ms)
- Power management with configurable sleep timeouts

### Combo Support
- Up to 4 simultaneously pressed combos
- Maximum 5 combos per key position
- Maximum 3 keys per combo

### Performance Optimizations
- 5ms debounce for both press and release
- 64-behavior queue size for complex macros
- N-key rollover (NKRO) enabled
- Full consumer key code support

### Split Keyboard Features
- Optimized BLE latency for split communication
- Synchronized behavior between halves
- Independent USB/BLE output selection

## Usage Examples

```bash
# Show keyboard configuration
glovebox config show-keyboard corne

# Show verbose configuration details
glovebox config show-keyboard corne --verbose

# List available firmware versions
glovebox config firmwares corne

# Create a keyboard profile
glovebox layout compile my_layout.json output/ --profile corne/main

# Build firmware with new generic docker compiler (west workspace)
glovebox firmware compile keymap.keymap config.conf --profile corne/main

# Build with workspace caching for faster subsequent builds
glovebox firmware compile keymap.keymap config.conf --profile corne/main --cache-workspace

# Build with specific board targets for split keyboard
glovebox firmware compile keymap.keymap config.conf --profile corne/main --board-targets corne_left,corne_right

# Flash firmware to keyboard
glovebox firmware flash firmware.uf2 --profile corne/main
```

## Hardware Requirements

- **Controller**: nice!nano v2 (recommended) or compatible nRF52840 board
- **Battery**: 301230 LiPo battery (110mAh recommended)
- **Switches**: MX-compatible mechanical switches
- **Case**: Corne Cherry v3 case (various materials available)

## Resources

- [Official Corne Repository](https://github.com/foostan/crkbd)
- [ZMK Firmware Documentation](https://zmk.dev/)
- [Corne Build Guide](https://github.com/foostan/crkbd/blob/master/corne-cherry/doc/buildguide_en.md)
- [Layout Editor](https://nickcoutsos.github.io/keymap-editor/)
- [Generic Docker Compiler Usage Guide](../docs/generic_docker_compiler_usage_guide.md)

## Configuration File Location

The main configuration file is located at:
```
keyboards/corne.yaml
```

This configuration includes all necessary settings for ZMK firmware compilation and flashing for the Corne keyboard.