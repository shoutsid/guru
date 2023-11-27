# distributed_computation_debug.py

import multiprocessing
import time


def ai_task(data):
    # Simulate a time-consuming AI computation
    result = data * 2
    return result


def worker(node_id, tasks, results, monitor):
    print(f"Node {node_id} is ready.")
    try:
        while True:
            task = tasks.get()  # Get a task from the queue
            if task is None:
                break  # Exit when no more tasks are available
            result = ai_task(task)
            results.put(result)  # Put the result in the results queue
    except Exception as e:
        print(f"Node {node_id} encountered an error:", e)
        monitor.put(node_id)  # Notify the monitor of the failure
    finally:
        print(f"Node {node_id} is done.")


def monitor_nodes(monitor, num_nodes, processes):
    failed_nodes = set()
    try:
        while len(failed_nodes) < num_nodes:
            failed_node = monitor.get()  # Wait for a failed node notification
            failed_nodes.add(failed_node)
            print(f"Node {failed_node} is marked as failed.")
            # Replace the failed node with a new one
            new_process = multiprocessing.Process(
                target=worker, args=(failed_node, tasks, results, monitor))
            processes.append(new_process)
            new_process.start()
    except Exception as e:
        print("Monitor encountered an error:", e)
    finally:
        print("Monitor is done.")


if __name__ == "__main__":
    num_nodes = 3
    num_tasks = 10

    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()
    monitor = multiprocessing.Queue()

    processes = []

    # Create worker processes
    for i in range(num_nodes):
        process = multiprocessing.Process(
            target=worker, args=(i, tasks, results, monitor))
        processes.append(process)
        process.start()

    # Create a monitoring process
    monitor_process = multiprocessing.Process(
        target=monitor_nodes, args=(monitor, num_nodes, processes))
    monitor_process.start()

    # Distribute tasks
    for i in range(num_tasks):
        tasks.put(i)

    # Add sentinel values to indicate the end of tasks
    for i in range(num_nodes):
        tasks.put(None)

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Wait for the monitoring process to finish
    monitor_process.join()

    # Collect and print results
    while not results.empty():
        result = results.get()
        print("Result:", result)

    print("All processes have exited.")
