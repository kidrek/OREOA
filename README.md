# OREOA (mOnitor aRtefacts from Evidence, prOcess and Analyse them)

OREOA is a forensic data processing and analysis tool that automates the collection, processing, and analysis of digital evidence. It integrates multiple forensic tools and provides both monitoring and manual processing capabilities.

## Features

- Automated evidence processing pipeline
- Support for Velociraptor collections
- Integration with multiple analysis tools:
  - Plaso (Timeline analysis)
  - Hayabusa (Windows Event Log analysis)
  - Chainsaw (Event log analysis)
  - Zircolite (SIGMA-based detection)
  - ClamAV (Antivirus scanning)
  - RegRippy (Windows Registry analysis)
- Timesketch integration for timeline visualization
- Both monitoring and manual processing modes

## Prerequisites

- Linux (Debian/Ubuntu)
- Docker and Docker Compose
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kidrek/OREOA.git
cd OREOA
```

2. Configure environment variables:
```bash
cp .env.tpl .env
```

Edit `.env` file with your configuration:
```ini
# Evidence Processing
ARTIFACT_INPUT_PATH=/absolute/path/to/input
SCAN_OUTPUT_PATH=/absolute/path/to/output

# Timesketch Configuration
TIMESKETCH_USER=your_username
TIMESKETCH_PASSWORD=your_password
TIMESKETCH_DEFAULT_SKETCH_NAME=default_sketch
TIMESKETCH_UPLOAD_PATH=/path/to/upload

# Evidence Settings
VELOCIRAPTOR_EVIDENCE_PATTERN=collection-.*\.zip
VELOCIRAPTOR_EVIDENCE_PASSWORD=your_password
EVTX_PATTERN=.evtx,.EVTX
HASH_ALGO=sha256
```

3. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

## Usage

### Monitor Mode

Monitor mode automatically processes new evidence files as they appear in the input directory:

```bash
python3 oreoa_monitor.py
```

### Manual Mode

Process individual evidence files manually:

```bash
python3 oreoa.py -i /path/to/evidence.zip -o /path/to/output/directory
```

Options:
- `-i, --input_evidence`: Path to the evidence file or directory
- `-o, --output_analyse`: Path where analysis results will be stored

## Output Structure

The tool creates the following directory structure for each processed artifact:

```
output/
└── evidence_name_extracted/
    ├── analyse/
    │   ├── plaso/
    │   ├── hayabusa/
    │   ├── chainsaw/
    │   ├── zircolite/
    │   ├── clamav/
    │   └── regrippy/
    └── output/
```

## Integrated Tools

- **Plaso**: Creates super timelines from various artifacts
- **Hayabusa**: Advanced Windows Event Log analysis
- **Chainsaw**: High-speed Windows Event Log analysis
- **Zircolite**: SIGMA-based threat detection
- **ClamAV**: Antivirus scanning
- **RegRippy**: Windows Registry analysis
- **Timesketch**: Timeline visualization and analysis

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License.
