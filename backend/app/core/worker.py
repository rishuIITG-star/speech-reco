import threading
import queue
import time
import traceback
from app.ml.pipeline import run_pipeline
from app.core.jobs import JobStatus

# Single-worker queue to prevent out-of-memory errors and model double-loading
_job_queue = queue.Queue()

def _worker_loop():
    while True:
        task = _job_queue.get()
        if task is None:
            break # Exit signal
            
        job, input_path, glossary_list = task
        try:
            print(f"Worker starting job {job.job_id}")
            run_pipeline(job, input_path, glossary_list)
        except Exception as e:
            print(f"Worker failed on job {job.job_id}: {e}")
            traceback.print_exc()
        finally:
            _job_queue.task_done()

_worker_thread = None

def start_worker():
    global _worker_thread
    if _worker_thread is None:
        _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
        _worker_thread.start()

def enqueue_job(job: JobStatus, input_path: str, glossary_list: list = None):
    _job_queue.put((job, input_path, glossary_list))
