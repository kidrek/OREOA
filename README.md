# OREOA (mOnitor aRtefacts from Evidence, prOcess and Analyse them)

## Requirements

```
git clone https://github.com/kidrek/OREOA.git
cd OREOA

# Set variables
cp .env.tpl .env
vi .env    <-- define the values to be used by the install.sh script

# Run installation
chmod +x install.sh
./install.sh
```

## Usage

### Monitor mode 

First of all set variables in ```.env``` file.

``` .env
# Directory monitored by this tool, to detect all new velociraptor collects stored
ARTIFACT_INPUT_PATH={ABSOLUTE_PATH}/input

# Directory where Velociraptor collects will be unarchived, process and analyse
SCAN_OUTPUT_PATH={ABSOLUTE_PATH}/output
```

Then run script ```oreoa_monitor.py```.

```
python3 oreoa_monitor.py
```

### Manual mode

```
$ python3 oreoa.py -h
usage: OREOA [-h] [-i INPUT_EVIDENCE] [-o OUTPUT_ANALYSE]

Tool to process and analyse forensic data

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_EVIDENCE, --input_evidence INPUT_EVIDENCE
  -o OUTPUT_ANALYSE, --output_analyse OUTPUT_ANALYSE



# Exemple :

python3 oreoa.py -i {ABSOLUTE_PATH}/input/collection-...-2024-08-12t12_36_13_02_00.zip -o {ABSOLUTE_PATH}/output/{EVIDENCE_ENDPOINT_NAME}
```
