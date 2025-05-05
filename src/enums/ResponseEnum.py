from enum import Enum

class ResponseEnum(Enum):

    FILE_TYPE_NOT_SUPPORTED="file_type_not_supported"
    FILE_SIZE_EXCEEDED="file_size_exceeded"
    FILE_UPLOADED_SUCCEDED="file_uploaded_succeeded"
    FILE_UPLOADED_FAILED="file_uploaded_failed"
    FOLDER_CREATED="folder_created"
    FOLDER_EXIEST="folder_exiest"
    File_SAVED= "file_saved"
    QUERY_PROCESSING_FAILED = "Failed to process your question"

