import logging
from prefect import flow
from tasks import utility

@flow(name="common")
def flow_common(original_path, original_filename, hash_algo):
    logging.info('Flow Common : Starting')

    # Sanitize name
    sanitized_name = utility.sanitize_file_name(original_filename)
    if original_filename != sanitized_name:
        utility.move_file(f"{original_path}/{original_filename}", f"{original_path}/{sanitized_name}",)

    # Generate Hash
    utility.generate_hash(hash=hash_algo, filepath=f"{original_path}/{sanitized_name}")

    # Determine evidence type
    evidence_type = utility.determine_evidence_type(original_filename)


    return sanitized_name, evidence_type
