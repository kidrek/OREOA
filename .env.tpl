ARTIFACT_INPUT_PATH=/{ABSOLUTE_PATH}/artifacts_input   # Ne pas spécifier le dernier /
SCAN_OUTPUT_PATH=/{ABSOLUTE_PATH}/scans_output         # Ne pas spécifier le dernier /
HASH_ALGO="sha256"
## VELOCIRAPTOR SETTINGS
VELOCIRAPTOR_EVIDENCE_PATTERN="^Collection-[^.]+\.zip"
VELOCIRAPTOR_EVIDENCE_PASSWORD=''
## TIMESKETCH INSTANCE
TIMESKETCH_DEFAULT_SKETCH_NAME=""
TIMESKETCH_USER=""
TIMESKETCH_PASSWORD=""
TIMESKETCH_UPLOAD_PATH="/{ABSOLUTE_PATH}/{TIMESKETCH_DOCKER}/upload"
## ARTIFACTS PATTERN
EVTX_PATTERN=".evtx"   ## Possible to have multi extension separate by comma ".evtx,.evtx.backup"
