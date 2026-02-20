from celery import shared_task
import time


@shared_task(bind=True, max_retries=5)
def transfer_playlist_task(self, user_id, source_playlist_id, target_provider):
    try:
        # 1. Fetch source tracks
        # 2. Convert to UniversalTrack
        # 3. Search in target provider
        # 4. Match using engine.is_match
        # 5. Collect matched + unmatched
        # 6. Create playlist in target
        # 7. Add matched tracks

        return {"status": "completed"}

    except Exception as exc:
        # Handle 429 retry
        retry_after = getattr(exc, "retry_after", 5)
        raise self.retry(exc=exc, countdown=retry_after)