import multiprocessing


def prepare_cases(start_ids,stop_ids,wait_time,casperinst,detailed_cases,channels_sorted_by_key,componentdict):
    from .sim_driver import read_prepare_cases
    return read_prepare_cases(start_ids,stop_ids,wait_time,casperinst,detailed_cases,channels_sorted_by_key,componentdict)
    

def parallel_process_inst(total_cases, total_cases_to_run_per_instance,no_of_psse_instances,no_of_cases_per_instance,detailed_cases,channels_sorted_by_key,componentdict):
    start_ids = [i * total_cases_to_run_per_instance for i in range(no_of_psse_instances)]
    wait_time = [(i+3) for i in range(len(start_ids))]
    casperinst = [no_of_cases_per_instance]*len(start_ids)
    stop_ids = [(i + 1) * total_cases_to_run_per_instance - 1 if ((i + 1) * total_cases_to_run_per_instance - 1) < total_cases-1 else total_cases-1 for i in range(no_of_psse_instances)]

    detailed_cases_list = [detailed_cases]*len(start_ids)
    channels_sorted_by_key_list = [channels_sorted_by_key]*len(start_ids)
    componentdict_list = [componentdict]*len(start_ids)

    init_cond = list()
    with multiprocessing.Pool(processes=no_of_psse_instances) as pool:
        init_cond.append(pool.starmap(prepare_cases,zip(start_ids,stop_ids,wait_time,casperinst,detailed_cases_list,channels_sorted_by_key_list,componentdict_list)))    
    return init_cond