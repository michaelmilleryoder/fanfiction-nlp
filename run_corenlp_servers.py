""" Starts a number of CoreNLP servers """
import argparse
import subprocess
import os
import pdb


def start_servers(start_port, n_servers):
    os.chdir('CoreNLP')
    processes = []
    for i in range(n_servers):
        cmd = f'sh start_corenlp_server.sh {start_port+i}'
        process = subprocess.Popen(cmd, shell=True)
        processes.append(process)

    return processes


def stop_servers(start_port, n_servers):
    # Find PIDs, kill
    for i in range(n_servers):
        try:
            pid = subprocess.check_output(["pgrep", '-f', f'port {start_port+i}'])
            pid = int(pid[:-1])
            os.kill(pid, 9)
        except subprocess.CalledProcessError as e:
            print(f'Port {start_port+i} not able to be killed')
            continue

    # Remove tmp lock
    shutdown_keypath = 'CoreNLP/tmp/corenlp.shutdown'
    if os.path.exists(shutdown_keypath):
        os.remove(shutdown_keypath)


def main():

    parser = argparse.ArgumentParser(description='Starts or stops a number of CoreNLP servers')
    parser.add_argument('start_port', nargs='?', type=int, help='an integer for the accumulator')
    parser.add_argument('n_servers', nargs='?', type=int, help='the number of servers to start or stop')
    parser.add_argument('--start', dest='start', action='store_true')
    parser.add_argument('--stop', dest='stop', action='store_true')
    parser.set_defaults(start=False)
    parser.set_defaults(stop=False)
    args = parser.parse_args()

    if args.start:
        start_servers(args.start_port, args.n_servers)
    elif args.stop:
        stop_servers(args.start_port, args.n_servers)

if __name__ == '__main__':
    main()
