import time
import psutil
import logging
import argparse
import subprocess
from logging.handlers import TimedRotatingFileHandler

from users import infer_user


def overall_cm_info():
    cpu_util = psutil.cpu_percent()
    mem_avail = psutil.virtual_memory().available / 1024**3
    mem_used = psutil.virtual_memory().used / 1024**3
    mem_total = psutil.virtual_memory().total / 1024**3
    mem_util = mem_used / mem_total * 100
    cm_info = dict(
        cpu_util=cpu_util,
        mem_avail=mem_avail,
        mem_used=mem_used,
        mem_total=mem_total,
        mem_util=mem_util)
    logging.info("全服CPU、内存使用情况：")
    logging.info("    CPU Util %.2f%%, Memory Util %.2f%%." % (cpu_util, mem_util))
    logging.info("    Memory used: %.1fGB." % (mem_used, ))
    logging.info("    Memory available: %.1fGB / %.1fGB." % (mem_avail, mem_total))
    return cm_info

def detailed_cm_info():
    """
    进程内存占用统计中的USS、PSS含义见见：
       P
    """
    user2mem_util = {}
    for proc in psutil.process_iter():
        try:
            info = proc.memory_full_info()
            uss = info.uss / 1024**3
            pss = info.pss / 1024**3
            mem_used = pss

            pid = proc.pid
            cmd = proc.cmdline()
            cwd = proc.cwd()
        except:
            # permission error or NoSuchProcess
            continue
        if mem_used < 0.010: # 10M
            continue
        if len(cmd) > 1:
            cmd[1] = cwd # get abs path of CWD
        cmd = ' '.join(cmd)
        logging.debug("%d, %.1fGB, %s" % (pid, mem_used, cmd))
        user = infer_user(cmd)
        user2mem_util[user] = user2mem_util.get(user, 0) + mem_used
    
    logging.info("每个人的内存使用情况：")
    for user, mem_util in user2mem_util.items():
        logging.info("    %s, %.1fGB RAM usage." % (user, mem_util))


def disk_info():
    # 查看临时硬盘存储信息
    try:
        output = subprocess.check_output(
            ['du', '-h', '/cache', '--max-depth=1'],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
        logging.warning("du -h出现故障！")
        
    # 解码
    try:
        output = output.decode("utf-8")
        output = output.split('\n')[:-2]
        output = [o.split('\t') for o in output]
    except:
        logging.error("du -h返回值解码错误！")
        return

    # 输出
    logging.info("每个人的临时硬盘使用情况：")
    for o in output:
        try:
            disk_util, dirname = o
            user = infer_user(dirname)
            logging.info("    %s, %s disk usage." % (user, disk_util))
        except:
            msg = ''.join(o)
            if 'No such file or directory' in msg:
                continue
            else:
                logging.warning("意外的du -h返回格式！:%s" % msg)
                logging.info()
        

def parse_args():
    description = "该脚本用于检测CPU、内存使用情况，并将内存使用情况按用户聚合。"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', action="store_true", help="是否显示临时硬盘使用情况.")
    parser.add_argument('--detail', action="store_true", help="是否显示每一个进程的内存使用情况.")
    parser.add_argument('-m', action="store_true", help="是否持续监控并打印到日志.")
    parser.add_argument('--interval', type=int, default=10, help="监控间隔（秒）.")
    parser.add_argument('--disk-rel-interval', type=int, default=30, help="存储空间的监控间隔为CPU、内存的倍率.")
    parser.add_argument('--log-path', type=str, default='', help="日志文件路径.")
    args = parser.parse_args()                               
    return args


if __name__ == "__main__":
    args = parse_args()

    logger_configs = dict(
        level=logging.INFO,
        format='%(asctime)s: %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    if args.detail:
        logger_configs['level'] = logging.DEBUG
    logging.basicConfig(**logger_configs)

    if args.m and args.log_path != '':
        disk_counter = 0
        if args.log_path == 'd':
            log_path = "/home/ma-user/work/monitor/logs/cpu_mem.log"
        log_file_handler = TimedRotatingFileHandler(
            filename=log_path, when="D", interval=1, backupCount=5)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        log_file_handler.setFormatter(formatter)
        logging.getLogger('').addHandler(log_file_handler)
        while True:
            overall_cm_info()
            detailed_cm_info()
            if disk_counter % args.disk_rel_interval == 0:
                disk_info()
                disk_counter = 1
            else:
                disk_counter += 1
            logging.info("\n")
            time.sleep(args.interval)
    else:
        cm_info = overall_cm_info()
        detailed_cm_info()
        if args.d:
            disk_info()