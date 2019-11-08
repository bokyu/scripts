import os
import psutil
import json

## Mem Usage
## pss (Linux): aka “Proportional Set Size”, is the amount of memory shared with other processes,
## accounted in a way that the amount is divided evenly between the processes that share it. 
## I.e. if a process has 10 MBs all to itself and 10 MBs shared with another process its PSS will be 15 MBs.

def get_memory_usage():
    procs = psutil.process_iter()
    total_mem_usage = 0

    for proc in procs:
        try:
            info = proc.memory_full_info()
            if info:
                total_mem_usage += info.pss
        except:
            continue
    return total_mem_usage

## uptime                = uptime of the system
## user_stime            = CPU time spent in user code
## kernel_stime          = CPU time spent in kernel code
## children_user_wtime   = Waited-for children’s CPU time spent in user code
## children_kernel_wtime = Waited-for children’s CPU time spent in kernel code
## start_time            = Time when the process started
## hertz                 = Arm: 100, Intel: 1000

## Calculation formula
## PCT = Accumulative cpu time spent by a process
## TCT = Accumulative total cpu time of host ( include IDLE mode )
## avg_cpu_usage = ( sum(current PCT) - sum (previous PCT) ) / ( current TCT - previous TCT )

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_info = f.readline().rstrip().split()
    uptime = float(uptime_info[0])
    return uptime

def get_current_proc_time():
    # Parse /proc/PID/stat and get process cpu info excetp 1
    pid_list = list(map(lambda proc: proc.pid, psutil.process_iter()))
    total_proc_cpu_time = float(0)

    for pid in pid_list:
        if pid != 1:
            with open('/proc/%d/stat' % pid, 'r') as f:
                cpu_info = f.readline().rstrip().split(' ')

            user_stime = float(cpu_info[13])
            kernel_stime = float(cpu_info[14])
            children_user_wtime = float(cpu_info[15])
            children_kernel_wtime = float(cpu_info[16])
    
            #proc_time = (user_stime + kernel_stime) / hertz
            ## To include the time from children processes. 
            proc_time = (user_stime + kernel_stime + children_user_wtime + children_kernel_wtime) / hertz
            total_proc_cpu_time += proc_time
    
    return total_proc_cpu_time

def get_current_cpu_time():
    # Parse /proc/stat and get total cpu time.

    total_cpu_time = float(0)
    used_cpu_time = float(0)
    
    with open('/proc/stat', 'r') as f:
        cpu_info = f.readline().rstrip().split()[1:8]
        # cpu column info
        # 0    1    2      3    4      5   6
        # user nice system idle iowait irq softirq
    
    index = 0
    for time in cpu_info:
        total_cpu_time += float(time)
        if not index in [3, 4]:
            used_cpu_time += float(time)

    total_cpu_time = total_cpu_time / hertz
    used_cpu_time = used_cpu_time / hertz

    return total_cpu_time, used_cpu_time

def load_pre_info():
    try:
        with open('/tmp/cpu_info.json', 'r', encoding='utf-8') as f:
            info = json.load(f)
    except FileNotFoundError:
       return None

    return info

def save_current_info(info):
    with open('/tmp/cpu_info.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)

def calculate_cpu_usage(pre_cpu_info, cur_cpu_info):
    uptime_diff = (cur_cpu_info['uptime'] - pre_cpu_info['uptime']) * 24
    proc_diff = cur_cpu_info['proc_cpu_time'] - pre_cpu_info['proc_cpu_time']
    total_diff = cur_cpu_info['total_cpu_time'] - pre_cpu_info['total_cpu_time']
    used_diff = cur_cpu_info['used_cpu_time'] - pre_cpu_info['used_cpu_time']

    avg_usage = (proc_diff * 100 / total_diff)
    avg_proc_usage = proc_diff * 100 / uptime_diff
    return avg_usage, avg_proc_usage

if __name__ == '__main__':
    hertz = float(1000)

    ## CPU
    # Get previous cpu_info
    pre_cpu_info = load_pre_info()

    # Get and save current cpu_info
    cur_uptime = get_uptime()
    cur_proc_cpu_time = get_current_proc_time()
    cur_total_cpu_time, cur_used_cpu_time = get_current_cpu_time()

    cur_cpu_info = {
        'uptime': cur_uptime,
        'proc_cpu_time': cur_proc_cpu_time,
        'total_cpu_time': cur_total_cpu_time,
        'used_cpu_time': cur_used_cpu_time,
    }
    save_current_info(cur_cpu_info)

    if pre_cpu_info:
        avg_usage, avg_proc_usage = calculate_cpu_usage(pre_cpu_info, cur_cpu_info)
    else:
        avg_usage = 0

    # Memory
    # Get Memory usage bytes
    mem_usage = get_memory_usage()
    
    with open('/tmp/cpu_memory.prom', 'w') as promfile:
        avg_usage = str(round(avg_usage, 5))
        mem_usage = str(mem_usage)
        save_data = "container_cpu_usage " + avg_usage + "\ncontainer_memory_usage " + mem_usage + "\n"
        promfile.write(save_data)
