import os
import sys
import pynvml as N

MB = 1024 * 1024

def get_pid_usage(device_index, my_pid):
    N.nvmlInit()

    handle = N.nvmlDeviceGetHandleByIndex(device_index)

    usage = [nv_process.usedGpuMemory // MB for nv_process in
             N.nvmlDeviceGetComputeRunningProcesses(handle) + N.nvmlDeviceGetGraphicsRunningProcesses(handle) if
             nv_process.pid == my_pid]

    if len(usage) == 1:
        usage = usage[0]
    else:
        raise KeyError("PID not found")

    return usage

def get_usage():
    N.nvmlInit()
    for dev_id in range(N.nvmlDeviceGetCount()):
        handle = N.nvmlDeviceGetHandleByIndex(dev_id)
        for proc in N.nvmlDeviceGetComputeRunningProcesses(handle):
            print(
                "pid %d using %d bytes of memory on device %d."
                % (proc.pid, proc.usedGpuMemory, dev_id)
            )

if __name__ == "__main__":
   get_usage()