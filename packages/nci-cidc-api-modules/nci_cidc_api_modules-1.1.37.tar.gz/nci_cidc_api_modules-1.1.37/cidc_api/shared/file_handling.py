from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from ..config.settings import GOOGLE_CLINICAL_DATA_BUCKET
from ..models import PreprocessedFiles
from ..shared.auth import get_current_user
from ..shared.gcloud_client import upload_file_to_gcs


def set_current_file(file: FileStorage, file_category: str, gcs_folder: str, job_id: int = None) -> PreprocessedFiles:
    """
    Archives any existing 'current' files for the given category and job,
    then uploads the new file as the latest 'current' version.
    """
    latest_version = PreprocessedFiles.archive_current_files(file_category, job_id=job_id)
    latest_file = create_file(file, gcs_folder, file_category, job_id, latest_version + 1)
    return latest_file


def create_file(
    file: FileStorage, gcs_folder: str, file_category: str, job_id: int = None, version: int = None
) -> PreprocessedFiles:
    """Upload file to GCS and create corresponding metadata record in the database."""
    status = "pending" if gcs_folder.endswith("pending/") else "current"
    # only need timestamp for current/approved files
    append_timestamp = status == "current"
    # create file in GCS
    gcs_file_path = upload_file_to_gcs(file, GOOGLE_CLINICAL_DATA_BUCKET, gcs_folder, append_timestamp=append_timestamp)
    # create corresponding record in db
    file = PreprocessedFiles.create(
        file_name=file.filename,
        object_url=gcs_file_path,
        file_category=file_category,
        uploader_email=get_current_user().email,
        status=status,
        job_id=job_id,
        version=version,
    )
    return file


def validate_file_extension(filename: str, allowed_extensions: list[str]):
    if not filename or not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise BadRequest(f"Invalid file type. Must be one of: {allowed_extensions}")


def format_common_preprocessed_file_response(file: PreprocessedFiles):
    """Format a common response for a single PreprocessedFiles record."""
    return {
        "file_name": file.file_name,
        "gcs_uri": f"gs://{GOOGLE_CLINICAL_DATA_BUCKET}/{file.object_url}",
        "status": file.status,
        "file_category": file.file_category,
        "uploader_email": file.uploader_email,
        "date": file._created.isoformat(),
    }
