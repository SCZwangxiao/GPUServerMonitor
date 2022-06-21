# 监控 & 管理脚本（开发中）

# 功能
- 获取当前CPU使用率、可用内存。
- 获取所有进程的CPU占用情况，归属人。
- 获取每一个GPU的进程ID、归属人、显存占用（开发中）。
- 给定PID，获取内存、CPU、GPU占用情况，归属人（开发中）。

# 使用说明
## CPU、内存
- 获得CPU使用率、可用内存，以及各个用户的内存使用情况：
```bash
python cm_util.py
```
- 监控CPU使用率、可用内存，以及各个用户的内存使用情况：
```bash
nohup python cm_util.py -d -m --log-path <path_to_log_file> 2>&1 > /dev/null &
nohup python cm_util.py -d -m --log-path d 2>&1 > /dev/null &
```

# 安装
Build the script:
```bash
pyinstaller -F cm_util.py
```

Add the program to env path.
```bash
echo -e "export PATH=\$PATH:/home/ma-user/work/monitor/dist" >> ~/.bashrc
source ~/.bashrc
```