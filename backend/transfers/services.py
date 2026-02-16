class TransferService:

    @staticmethod
    def start_transfer(job):
        # change status to in_progress
        job.status = "in_progress"
        job.save()

        # simulate processing
        job.total_tracks = 50
        job.transferred_tracks = 50
        job.failed_tracks = 0

        job.status = "completed"
        job.save()

        return job
