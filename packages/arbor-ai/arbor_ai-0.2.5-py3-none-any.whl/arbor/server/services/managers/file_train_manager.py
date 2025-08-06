import random
import string
from datetime import datetime
from pathlib import Path

from arbor.server.api.models.schemas import FineTuneRequest
from arbor.server.core.config import Config
from arbor.server.services.jobs.file_train_job import FileTrainJob
from arbor.server.services.jobs.job import JobEvent
from arbor.server.services.managers.file_manager import FileManager
from arbor.server.services.managers.job_manager import Job, JobStatus


class FileTrainManager:
    def __init__(self, config: Config):
        self.config = config

    def fine_tune(self, request: FineTuneRequest, job: Job, file_manager: FileManager):

        job.status = JobStatus.RUNNING
        job.add_event(
            JobEvent(level="info", message="Starting fine-tuning job", data={})
        )

        # Determine fine-tuning type from method or auto-detect from file format
        if request.method is not None:
            # cast it to sft if it's supervised
            if request.method["type"] == "supervised":
                request.method["type"] = "sft"

            fine_tune_type = request.method["type"]
            job.add_event(
                JobEvent(
                    level="info",
                    message=f"Using specified training method: {fine_tune_type}",
                    data={},
                )
            )
        else:
            # Auto-detect based on file format
            detected_format = file_manager.check_file_format(request.training_file)
            if detected_format == "unknown":
                raise ValueError(
                    f"Could not determine training method. File format is unknown. "
                    f"Please specify the method parameter with type 'sft' or 'dpo'."
                )
            fine_tune_type = detected_format
            job.add_event(
                JobEvent(
                    level="info",
                    message=f"Auto-detected training method: {fine_tune_type}",
                    data={},
                )
            )

        if fine_tune_type not in ["dpo", "sft"]:
            raise ValueError(
                f"Unsupported training method: {fine_tune_type}. Supported methods: 'sft', 'dpo'"
            )

        file_train_job = FileTrainJob(self.config)
        file_train_job.fine_tune(request, file_manager, fine_tune_type)
