import time
import multiprocessing

from logcatter import Log


def dynamic_worker_task(task_id: int):
    """A worker task that logs at different levels."""
    Log.v(f"Worker {task_id}: Verbose logging")
    Log.d(f"Worker {task_id}: Detailed debug information.")
    time.sleep(0.2)
    Log.i(f"Worker {task_id}: Regular progress update.")
    time.sleep(0.2)
    Log.w(f"Worker {task_id}: Some warning.")


if __name__ == '__main__':
    Log.init()
    Log.i("Main process starting...")
    try:
        with multiprocessing.Pool(processes=2, initializer=Log.init_worker()) as pool:
            pool.map_async(dynamic_worker_task, range(2))
            time.sleep(1)
            Log.i("\n" + "=" * 50)
            Log.w(">>> CHANGING LOG LEVEL TO DEBUG <<<")
            Log.set_level(Log.INFO)
            Log.v("This log must be ignored\n")
            time.sleep(1)
            pool.map_async(dynamic_worker_task, range(2, 4))
            pool.close()
            pool.join()
    finally:
        Log.i("Application finished.")
        Log.dispose()