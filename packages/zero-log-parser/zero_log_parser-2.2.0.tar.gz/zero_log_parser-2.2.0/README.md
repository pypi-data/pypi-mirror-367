# Zero Log Parser

A modern Python package for parsing Zero Motorcycle log files with structured data extraction and multiple output formats.

This tool parses binary-encoded event logs from Zero Motorcycles' main bike board (MBB) and battery management system (BMS) into human-readable formats, emulating Zero's official log parser functionality with enhanced structured data extraction.

## Features

- **Multiple Output Formats**: Text, CSV, TSV, and JSON
- **Interactive Data Visualization**: Generate rich HTML plots for data analysis
- **Structured Data Extraction**: Automatically converts telemetry data to structured JSON format
- **Timezone Support**: Configurable timezone handling with system default
- **Modern Python Package**: Built for Python 3.10+ with type hints and modern packaging
- **CLI and Library**: Use as command-line tool or import as Python library
- **Enhanced Parsing**: Improved message parsing with descriptive event names and structured sensor data

## Installation

### From PyPI (recommended)

```bash
# Basic installation
pip install zero-log-parser

# With plotting dependencies
pip install zero-log-parser[plotting]
```

### From Source

```bash
git clone https://github.com/ilja-radusch/zero-log-parser.git
cd zero-log-parser

# Basic installation
pip install -e .

# With plotting dependencies
pip install -e ".[plotting]"
```

### For Development

```bash
git clone https://github.com/ilja-radusch/zero-log-parser.git
cd zero-log-parser
pip install -e ".[dev]"
```

## Requirements

- Python 3.10 or higher
- No external dependencies (uses only Python standard library)
- Optional: `plotly` and `pandas` for interactive plotting features

## Usage

### Getting Logs

You can extract logs from your Zero motorcycle using the [Zero mobile app](http://www.zeromotorcycles.com/app/help/ios/):

1. Download the Zero mobile app
2. Pair your motorcycle with it via Bluetooth
3. Select `Support` > `Email bike logs`
4. Enter your email address to send the logs to yourself
5. Download the attachment from the email

### Command Line Interface

The package provides multiple CLI commands: `zero-log-parser` and `zlp` (short alias) for parsing, and `zero-plotting` for interactive visualizations.

**Note**: Interactive plotting is available through the `zero-plotting` command. The main CLI (`zero-log-parser`/`zlp`) and standalone script (`zero_log_parser.py`) provide parsing functionality only.

#### Basic Usage

```bash
# Parse to text format (default)
zero-log-parser logfile.bin

# Specify output file
zero-log-parser logfile.bin -o output.txt

# Different output formats
zero-log-parser logfile.bin -f csv -o output.csv
zero-log-parser logfile.bin -f tsv -o output.tsv
zero-log-parser logfile.bin -f json -o output.json
```

#### Advanced Options

```bash
# Custom timezone (UTC offset in hours)
zero-log-parser logfile.bin --timezone -8  # PST
zero-log-parser logfile.bin --timezone 1   # CET

# Verbose output
zero-log-parser logfile.bin --verbose

# Short alias
zlp logfile.bin -f json -o structured_data.json
```

#### Interactive Plotting

Generate rich HTML visualizations of your motorcycle data using the `zero-plotting` command:

```bash
# Make sure you have plotting dependencies installed
# Either: pip install zero-log-parser[plotting]
# Or: pip install plotly pandas

# Generate all available plots
zero-plotting logfile.bin --plot all

# Generate specific plot types
zero-plotting logfile.bin --plot battery      # Battery SOC and health
zero-plotting logfile.bin --plot power       # Power consumption analysis
zero-plotting logfile.bin --plot range       # Range estimation and efficiency
zero-plotting logfile.bin --plot performance # RPM vs efficiency analysis
zero-plotting logfile.bin --plot thermal     # Temperature monitoring
zero-plotting logfile.bin --plot voltage     # Voltage analysis
zero-plotting logfile.bin --plot charging    # Charging session & recuperation analysis
zero-plotting logfile.bin --plot balance     # Cell balance health

# Specify output directory for HTML plots
zero-plotting logfile.bin --plot all --plot-output-dir ./plots

# Time filtering examples
zero-plotting logfile.bin --plot thermal --start "last month"
zero-plotting logfile.bin --plot battery --start "June 2025" --end "July 2025"
zero-plotting logfile.bin --plot power --start "2025-06-15" --end "2025-06-20"
zero-plotting logfile.bin --plot range --start "last 30 days"
```

#### Time Filtering

The `zero-plotting` command supports flexible time filtering using `--start` and `--end` parameters:

**Relative Time Formats:**
- `"last week"`, `"last month"`, `"last year"`
- `"last 7 days"`, `"last 30 days"`, `"last 3 months"`

**Specific Date Formats:**
- `"June 2025"`, `"December 2024"` (month and year)
- `"2025-06-15"`, `"2025-06-15 14:30"` (ISO format)
- `"06/15/2025"`, `"15/06/2025"` (US/EU date formats)
- `"June 15, 2025"` (natural language)

**Usage Examples:**
```bash
# Filter data from the last month only
zero-plotting logs.bin --plot thermal --start "last month"

# Filter data for a specific month
zero-plotting logs.bin --plot battery --start "June 2025" --end "July 2025"

# Filter data for a specific date range
zero-plotting logs.bin --plot power --start "2025-06-15" --end "2025-06-20"

# Filter data from a specific date until now
zero-plotting logs.bin --plot range --start "2025-06-01"
```

#### Help

```bash
zero-log-parser --help
```

### Python Library

```python
from zero_log_parser import LogData, parse_log

# Parse a log file
log_data = LogData("path/to/logfile.bin")

# Access parsed data
print(f"Entries: {log_data.entries_count}")
print(f"Header: {log_data.header_info}")

# Generate different output formats
text_output = log_data.emit_text_decoding()
json_output = log_data.emit_json_decoding()

# Or use the high-level function
parse_log(
    log_file="input.bin",
    output_file="output.json",
    output_format="json",
    timezone_offset=-8  # PST
)
```

### Output Formats

#### Text Format (default)
Human-readable format similar to Zero's official parser:
```
Entry     Timestamp            Level     Event                    Conditions
6490      2025-08-03 12:34:32  DATA      Firmware Version         {"revision": 48, ...}
```

#### CSV Format
Comma-separated values for spreadsheet import:
```csv
Entry,Timestamp,LogLevel,Event,Conditions
6490,2025-08-03 12:34:32,DATA,Firmware Version,"{""revision"": 48, ...}"
```

#### TSV Format  
Tab-separated values for data analysis:
```tsv
Entry	Timestamp	LogLevel	Event	Conditions
6490	2025-08-03 12:34:32	DATA	Firmware Version	{"revision": 48, ...}
```

#### JSON Format
Structured JSON with metadata and parsed telemetry:
```json
{
  "metadata": {
    "source_file": "logfile.bin",
    "log_type": "MBB",
    "total_entries": 6603
  },
  "entries": [
    {
      "entry_number": 6490,
      "timestamp": "2025-08-03 12:34:32",
      "log_level": "DATA",
      "event": "Firmware Version",
      "is_structured_data": true,
      "structured_data": {
        "revision": 48,
        "build_date": "2024-11-17",
        "build_time": "14:19:50"
      }
    }
  ]
}
```

## Structured Data Features

The parser automatically detects and converts various message types to structured JSON:

- **Firmware Version**: Build info, revision, timestamps
- **Battery Pack Configuration**: Pack type, brick count, specifications  
- **Discharge Level**: SOC, current, voltage, temperature data
- **SOC Data**: State of charge with voltage and current readings
- **Voltage Readings**: Contactor and cell voltage measurements
- **Charging/Riding Status**: Comprehensive telemetry during operation
- **Tipover Detection**: Sensor data with roll/pitch measurements
- **Error Conditions**: Structured fault and diagnostic information

## Data Visualization

The plotting feature provides comprehensive analysis capabilities:

### Range Analysis (`--plot range`)
Analyze riding efficiency and range estimation:
- Energy consumption rate (Wh/mile or Wh/km) over time
- Remaining range estimates based on current battery SOC and consumption history
- Speed vs efficiency correlation to identify optimal riding speeds
- Trip segment analysis showing consumption patterns for different riding conditions

### Performance vs Efficiency (`--plot performance`)
Correlate motor performance with energy efficiency:
- RPM vs power consumption scatter plots to identify efficient operating ranges
- Motor efficiency curves showing optimal RPM bands for different power levels
- Speed vs energy consumption analysis for performance tuning
- Torque delivery efficiency across different riding scenarios

### Battery Health Monitoring (`--plot battery`)
Comprehensive battery state tracking:
- State of Charge (SOC) progression over ride sessions
- Battery voltage curves under load and at rest
- Temperature impact on battery performance
- Charge/discharge cycle analysis for battery health assessment

### Power Analysis (`--plot power`)
Detailed energy usage pattern analysis:
- Real-time power draw visualization with regenerative braking events
- Acceleration vs consumption correlation for riding style analysis
- Peak power events and their impact on overall efficiency
- Power distribution analysis across different riding modes

### Charging & Recuperation Analysis (`--plot charging`)
Comprehensive charging session and energy recovery analysis:
- AC voltage monitoring during charging sessions
- EVSE (Electric Vehicle Supply Equipment) current tracking
- State of charge progression during charging
- **Recuperation analysis**: Energy recovery during regenerative braking (negative battery current)
- Regenerative braking efficiency and frequency analysis
- Energy flow visualization showing both consumption and recovery

**Example Output**: All plots are generated as interactive HTML files that can be opened in any web browser, featuring zoom, pan, and hover capabilities for detailed data exploration.

### Example Plots

Here are some example visualizations generated from Zero Motorcycle log data:

#### Thermal Management - Temperature Deltas from Ambient
Shows component temperatures relative to ambient conditions, with gaps indicating when the motorcycle was switched off.

![Thermal Management](plots/thermal_management.png)

#### Performance vs Efficiency Analysis  
Correlates motor RPM with battery current consumption, colored by state of charge for performance optimization insights.

![Performance Efficiency](plots/performance_efficiency.png)

#### Range Analysis - Odometer vs State of Charge
Analyzes energy consumption patterns across distance traveled, with current draw indicators for riding efficiency assessment.

![Range Analysis](plots/range_analysis.png)

## Development

### Setup Development Environment

```bash
git clone https://github.com/ilja-radusch/zero-log-parser.git
cd zero-log-parser
pip install -e ".[dev]"
```

## Log File Formats

The parser supports multiple Zero motorcycle log formats:

- **MBB Logs**: Main bike board event logs
- **BMS Logs**: Battery management system logs  
- **Legacy Format**: Static addresses for older firmware
- **Ring Buffer Format**: Dynamic format for 2024+ firmware

For detailed format documentation, see [LOG STRUCTURE](LOG_STRUCTURE.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and code quality tools
6. Submit a pull request

## Authors

- **Ilja Radusch** - *Current Maintainer* - [@ilja-radusch](https://github.com/ilja-radusch/)
- **Kim Burgess** - *Original Author* - [@KimBurgess](https://github.com/KimBurgess/)
- **Brian T. Rice** - *Previous Maintainer* - [@BrianTRice](https://github.com/BrianTRice/)
- **Keith Thomas** - *Contributor* - [@keithxemi](https://github.com/keithxemi)

## License

This project is licensed under the MIT License

## Acknowledgments

Originally developed at https://github.com/KimBurgess/zero-log-parser, this is a modernized fork with enhanced structured data extraction and modern Python packaging.

## Support

- Report issues: [GitHub Issues](https://github.com/ilja-radusch/zero-log-parser/issues)
- Documentation: [GitHub Repository](https://github.com/ilja-radusch/zero-log-parser)
