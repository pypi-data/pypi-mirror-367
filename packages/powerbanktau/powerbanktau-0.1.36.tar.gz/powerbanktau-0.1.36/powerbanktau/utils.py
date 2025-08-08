import os
import gc
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from dask_jobqueue import PBSCluster, SLURMCluster
from dask.distributed import Client, wait, LocalCluster, as_completed
from typing import Any, Callable, Dict, List, Optional, Union
import csv


# def launch_slurm_dask_cluster(memory_size="3GB", num_workers=25, queue="engineering",
#                               walltime="7200", dashboard_address=":23154", cores=1, processes=1,
#                           log_directory="~/../logging/dask-logs", working_directory=None,
#                           gpus=0, gpu_module="miniconda/miniconda3-2023-environmentally"):

# """
# :param memory_size: The amount of memory allocated for each Dask worker (default is '3GB').
# :param num_workers: The number of workers to be created in the Dask cluster (default is 25).
# :param queue: The SLURM queue/partition to use for job scheduling (default is 'engineering').
# :param walltime: The maximum wall clock time for the job in seconds (default is '7200').
# :param dashboard_address: The address for the Dask dashboard (default is ':23154').
# :param cores: The number of CPU cores to allocate for each worker (default is 1).
# :param processes: The number of processes per worker (default is 1).
# :param log_directory: The directory to store Dask worker logs (default is '~/../logging/dask-logs').
# :param working_directory: The working directory where the SLURM job will execute (default is None).
# :param gpus: The number of GPUs to allocate for each worker (default is 0).
# :param gpu_module: The module to load before execution (default is 'miniconda/miniconda3-2023-environmentally').
# :return: A tuple consisting of the Dask client and the SLURMCluster instance.
# """
# Commands to execute before worker starts
# pre_executors = []
# if working_directory is not None:
#     pre_executors.append(f"cd {working_directory}")

# # Load GPU module if GPUs are requested
# if gpus > 0:
#     pre_executors.append(f"module load {gpu_module}")
#     job_extra = {
#         "--gres": f"gpu:{gpus}",  # Request the number of GPUs
#         "-A": "gpu-general-users"  # Add account info for GPU partition
#     }
# else:
#     job_extra = {}

# # Create SLURMCluster depending on whether GPUs are requested or not
# cluster = SLURMCluster(
#     cores=cores,
#     memory=memory_size,
#     processes=processes,
#     queue=queue,
#     walltime=walltime,
#     scheduler_options={"dashboard_address": dashboard_address},
#     log_directory=log_directory,
#     job_script_prologue=pre_executors,
#     job_extra_directives=job_extra if gpus > 0 else None  # Pass `job_extra` only if GPUs are used
# )

# # Scale the cluster to the specified number of workers
# cluster.scale(num_workers)

# # Connect the Dask client to the cluster
# client = Client(cluster)

# return client, cluster

def launch_slurm_dask_cluster(memory_size="3GB", num_workers=25, queue="engineering",
                        walltime="7200", dashboard_address=":23154", cores=1, processes=1,
                        log_directory="~/../logging/dask-logs", working_directory=None,
                        gpus=0, gpu_module="miniconda/miniconda3-2023-environmentally"):
    """
    :param memory_size: The amount of memory allocated for each Dask worker (default is '3GB').
    :param num_workers: The number of workers to be created in the Dask cluster (default is 25).
    :param queue: The SLURM queue/partition to use for job scheduling (default is 'tamirQ').
    :param walltime: The maximum wall clock time for the job in seconds (default is '7200').
    :param dashboard_address: The address for the Dask dashboard (default is ':23154').
    :param cores: The number of CPU cores to allocate for each worker (default is 1).
    :param processes: The number of processes per worker (default is 1).
    :param log_directory: The directory to store Dask worker logs (default is '~/.dask-logs').
    :param working_directory: The working directory where the SLURM job will execute (default is None).
    :return: A tuple consisting of the Dask client and the SLURMCluster instance.
    """
    pre_executors = []
    if working_directory is not None:
        pre_executors.append(f"cd {working_directory}")

    if gpus > 0:
        # Load the specified GPU module before execution
        pre_executors.append(f"module load {gpu_module}")

    if gpus == 0:
        cluster = SLURMCluster(
            cores=cores,
            memory=memory_size,
            processes=processes,
            queue=queue,
            walltime=walltime,
            scheduler_options={"dashboard_address": dashboard_address},
            log_directory=log_directory,
            job_script_prologue=pre_executors
        )
    else:
        cluster = SLURMCluster(
            cores=cores,
            memory=memory_size,
            processes=processes,
            queue=queue,
            walltime=walltime,
            scheduler_options={"dashboard_address": dashboard_address},
            log_directory=log_directory,
            job_script_prologue=pre_executors,
            extra=[f"--gres=gpu:{gpus}"]
        )


    cluster.scale(num_workers)
    client = Client(cluster)
    return client, cluster


def launch_local_dask_cluster(memory_size="3GB", num_workers=25, dashboard_address=":23154", cores=1):
    cluster = LocalCluster(
        n_workers=num_workers,
        threads_per_worker=cores,
        memory_limit=memory_size,
        dashboard_address=dashboard_address,
    )
    client = Client(cluster)
    return client, cluster


def launch_pbs_dask_cluster(memory_size="3GB", num_workers=25, queue="tamirQ",
                        walltime="24:00:00", dashboard_address=":23154", cores=1, processes=1,
                        log_directory="~/.dask-logs", working_directory=None):
    """
    :param memory_size: The amount of memory to allocate for each worker node, specified as a string (e.g., "3GB").
    :param num_workers: The number of worker nodes to start in the PBS cluster.
    :param queue: The job queue to submit the PBS jobs to.
    :param walltime: The maximum walltime for each worker node, specified as a string in the format "HH:MM:SS".
    :param dashboard_address: The address where the Dask dashboard will be hosted.
    :param cores: The number of CPU cores to allocate for each worker node.
    :param processes: The number of processes to allocate for each worker node.
    :param log_directory: The directory where Dask will store log files.
    :param working_directory: The directory to change to before executing the job script on each worker node.
    :return: A tuple consisting of the Dask client and the PBS cluster objects.
    """
    pre_executors = []
    if working_directory is not None:
        pre_executors.append(f"cd {working_directory}")

    cluster = PBSCluster(
        cores=cores,
        memory=memory_size,
        processes=processes,
        queue=queue,
        walltime=walltime,
        scheduler_options={"dashboard_address": dashboard_address},
        log_directory=log_directory,
        job_script_prologue=pre_executors
    )

    cluster.scale(num_workers)
    client = Client(cluster)
    return client, cluster


def process_and_save_tasks(tasks, funct, dask_client, save_loc, file_index=0, capacity=1000, save_multiplier=10):
    def save_results(results, index):
        if results:
            df = pd.concat(results)
            df.to_csv(os.path.join(save_loc, f'results_{index}.csv'))
            return []

        return results

    futures, all_results = [], []
    for i, task in tqdm(enumerate(tasks), total=len(tasks)):
        futures.append(dask_client.submit(funct, task))
        if (i + 1) % capacity == 0:
            wait(futures)
            all_results.extend([f.result() for f in futures if f.status == 'finished' and f.result() is not None])
            futures = []

        if (i + 1) % (capacity * save_multiplier) == 0:
            all_results = save_results(all_results, file_index)
            file_index += 1
            gc.collect()

    wait(futures)
    all_results.extend([f.result() for f in futures if f.status == 'finished' and f.result() is not None])
    save_results(all_results, file_index)
    return all_results


def collect_results(result_dir):
    """
    :param result_dir: Directory containing result CSV files to be collected
    :return: A concatenated pandas DataFrame containing data from all CSV files in the result directory
    """
    result_path = Path(result_dir)
    data = [pd.read_csv(file) for file in result_path.iterdir()]
    return pd.concat(data)


def restart_checkpoint(result_dir, patern='*'):
    """
    :param patern:
    :param result_dir: Directory path where checkpoint result files are stored.
    :return: A tuple containing a list of unique mutation IDs processed from the checkpoint files and the highest checkpoint index found.
    """
    result_path = Path(result_dir)
    files = sorted(result_path.glob(patern), key=lambda x: int(x.stem.split('_')[-1]), reverse=True)

    if not files:
        return [], 0

    try:
        data = []
        latest_file = files[0]
        for file in files:
            data.append(pd.read_csv(file))
        processed_muts = pd.concat(data).mut_id.unique().tolist()
        highest_checkpoint = int(latest_file.stem.split('_')[-1])
        return processed_muts, highest_checkpoint

    except Exception as e:
        print(f"Error processing file {files}: {e}")
        return [], 0


def launch_dask_cluster(cluster_type: str = "local", **kwargs) -> tuple:
    """
    Unified function to launch different types of Dask clusters.
    
    :param cluster_type: Type of cluster ("local", "slurm", "pbs")
    :param kwargs: Arguments specific to the cluster type
    :return: A tuple of (client, cluster)
    """
    if cluster_type == "local":
        return launch_local_dask_cluster(**kwargs)
    elif cluster_type == "slurm":
        return launch_slurm_dask_cluster(**kwargs)
    elif cluster_type == "pbs":
        return launch_pbs_dask_cluster(**kwargs)
    else:
        raise ValueError(f"Unknown cluster type: {cluster_type}")


def launch_local_cluster_from_job(n_workers: Optional[int] = None, 
                                   threads_per_worker: Optional[int] = None,
                                   memory_per_worker: Optional[str] = None,
                                   dashboard_address: str = ":8787") -> tuple:
    """
    Launch a local Dask cluster optimized for running within an existing job allocation.
    Automatically detects available resources if not specified.
    
    :param n_workers: Number of workers (if None, uses available CPU cores)
    :param threads_per_worker: Threads per worker (if None, calculates based on available cores)
    :param memory_per_worker: Memory per worker (if None, divides available memory)
    :param dashboard_address: Dashboard address
    :return: A tuple of (client, cluster)
    """
    import multiprocessing
    import psutil
    
    if n_workers is None:
        n_workers = multiprocessing.cpu_count()
    
    if threads_per_worker is None:
        threads_per_worker = max(1, multiprocessing.cpu_count() // n_workers)
    
    if memory_per_worker is None:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        memory_per_worker = f"{available_memory_gb / n_workers:.1f}GB"
    
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit=memory_per_worker,
        dashboard_address=dashboard_address,
        silence_logs=40
    )
    
    client = Client(cluster)
    return client, cluster


def process_with_dask_pipeline(
    items: List[Any],
    process_func: Callable,
    output_file: str,
    cluster_config: Optional[Dict[str, Any]] = None,
    func_kwargs: Optional[Dict[str, Any]] = None,
    default_result: Any = None,
    batch_size: int = 1000,
    save_interval: int = 100,
    item_to_dict: Optional[Callable] = None,
    cluster_type: str = "local",
    append_mode: bool = True
) -> str:
    """
    Complete pipeline that spawns a Dask cluster, processes items, and saves results incrementally.
    
    :param items: List of items to process
    :param process_func: Function to apply to each item
    :param output_file: Path to save results (CSV format)
    :param cluster_config: Configuration for the cluster (passed to launch functions)
    :param func_kwargs: Additional kwargs to pass to process_func
    :param default_result: Default value to use if processing fails
    :param batch_size: Number of futures to maintain at once
    :param save_interval: Save results every N processed items
    :param item_to_dict: Optional function to convert item to dict for saving
    :param cluster_type: Type of cluster to launch ("local", "slurm", "pbs")
    :param append_mode: Whether to append to existing file or overwrite
    :return: Path to the output file
    """
    cluster_config = cluster_config or {}
    func_kwargs = func_kwargs or {}
    
    client, cluster = launch_dask_cluster(cluster_type, **cluster_config)
    
    try:
        def safe_process(item):
            try:
                return process_func(item, **func_kwargs)
            except Exception as e:
                print(f"Error processing item: {e}")
                return default_result
        
        futures = []
        results_buffer = []
        processed_count = 0
        file_exists = os.path.exists(output_file) and append_mode
        
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        for i, item in tqdm(enumerate(items), total=len(items), desc="Submitting tasks"):
            future = client.submit(safe_process, item)
            future.item = item
            futures.append(future)
            
            if len(futures) >= batch_size:
                for completed_future in as_completed(futures[:batch_size]):
                    result = completed_future.result()
                    item_data = completed_future.item
                    
                    if item_to_dict:
                        record = item_to_dict(item_data, result)
                    else:
                        record = {"item": str(item_data), "result": result}
                    
                    results_buffer.append(record)
                    processed_count += 1
                    
                    if processed_count % save_interval == 0:
                        _save_results_to_csv(results_buffer, output_file, file_exists)
                        results_buffer = []
                        file_exists = True
                
                futures = futures[batch_size:]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Collecting remaining"):
            result = future.result()
            item_data = future.item
            
            if item_to_dict:
                record = item_to_dict(item_data, result)
            else:
                record = {"item": str(item_data), "result": result}
            
            results_buffer.append(record)
            processed_count += 1
            
            if processed_count % save_interval == 0:
                _save_results_to_csv(results_buffer, output_file, file_exists)
                results_buffer = []
                file_exists = True
        
        if results_buffer:
            _save_results_to_csv(results_buffer, output_file, file_exists)
        
        print(f"Processing complete. Results saved to {output_file}")
        return output_file
        
    finally:
        client.close()
        cluster.close()


def _save_results_to_csv(records: List[Dict], output_file: str, append: bool = True):
    """Helper function to save records to CSV."""
    if not records:
        return
    
    df = pd.DataFrame(records)
    mode = 'a' if append else 'w'
    header = not append
    
    df.to_csv(output_file, mode=mode, header=header, index=False)


def process_dataframe_with_dask(
    df: pd.DataFrame,
    process_func: Callable,
    output_file: str,
    cluster_config: Optional[Dict[str, Any]] = None,
    func_kwargs: Optional[Dict[str, Any]] = None,
    default_result: Any = None,
    batch_size: int = 1000,
    save_interval: int = 100,
    cluster_type: str = "local",
    row_to_dict: Optional[Callable] = None,
    append_mode: bool = True
) -> str:
    """
    Process a DataFrame row by row using Dask, with incremental saving.
    
    :param df: DataFrame to process
    :param process_func: Function to apply to each row
    :param output_file: Path to save results
    :param cluster_config: Configuration for the cluster
    :param func_kwargs: Additional kwargs for process_func
    :param default_result: Default value if processing fails
    :param batch_size: Number of futures to maintain
    :param save_interval: Save results every N items
    :param cluster_type: Type of cluster to launch
    :param row_to_dict: Function to convert row and result to dict
    :param append_mode: Whether to append to existing file
    :return: Path to output file
    """
    
    def default_row_to_dict(row, result):
        row_dict = row.to_dict() if hasattr(row, 'to_dict') else {"row": str(row)}
        row_dict["result"] = result
        return row_dict
    
    row_to_dict = row_to_dict or default_row_to_dict
    
    rows = [row for _, row in df.iterrows()]
    
    return process_with_dask_pipeline(
        items=rows,
        process_func=process_func,
        output_file=output_file,
        cluster_config=cluster_config,
        func_kwargs=func_kwargs,
        default_result=default_result,
        batch_size=batch_size,
        save_interval=save_interval,
        item_to_dict=row_to_dict,
        cluster_type=cluster_type,
        append_mode=append_mode
    )

