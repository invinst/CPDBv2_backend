#!/usr/bin/env python

from subprocess import check_output
import os
import json
import argparse
import time
import sys


PENDING_CHECK_INTERVAL = 5  # seconds
PENDING_CHECK_ATTEMPS = 6
DEPLOYMENT_NAME = 'gunicorn'


dir_path = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.join(dir_path, '..')


def call_cmd(cmd):
    return check_output(
        cmd, shell=True, cwd=root_dir
    ).strip()


def get_pod_states(namespace):
    pod_output = call_cmd('kubectl get pods -l app=%s -n %s -o json' % (DEPLOYMENT_NAME, namespace))
    pod_state = json.loads(pod_output)
    return pod_state['items']


def exit_with_log(container_name, pod_name, namespace, reason):
    print(reason)
    log = call_cmd('kubectl logs %s %s -n %s' % (pod_name, container_name, namespace))
    print(log)
    sys.stdout.flush()
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check pod status!')
    parser.add_argument(
        '-n', '--namespace', nargs='?',
        default='staging',
        choices=['staging', 'production'],
        help='Namespace (staging|production)'
    )
    args = parser.parse_args()
    namespace = args.namespace

    for _ in range(PENDING_CHECK_ATTEMPS):
        waiting = False

        pods = get_pod_states(namespace)
        for pod in pods:
            pod_name = pod['metadata']['name']
            print('Checking pod %s' % pod_name)

            if pod['status']['phase'] == 'Pending':
                waiting = True
                print('Status: Pending...')
                continue

            for container_status in pod['status']['containerStatuses']:
                container_name = container_status['name']

                if container_status['ready']:
                    print('Status: Ready')
                    continue

                if 'terminated' in container_status['state']:
                    print('Status: Terminated!')
                    exit_with_log(
                        container_name, pod_name, namespace, container_status['state']['terminated']['reason']
                    )

                if 'waiting' in container_status['state']:
                    waiting = True
                    print('Status: Wating...')
                    if container_status['restartCount'] > 0:
                        exit_with_log(
                            container_name, pod_name, namespace, json.dumps(container_status['lastState'], indent=4)
                        )
                    print(container_status['state']['message'])
        if not waiting:
            break
        sys.stdout.flush()
        time.sleep(PENDING_CHECK_INTERVAL)
    else:
        print('Checking timeout!')
        sys.stdout.flush()
        sys.exit(0)

    print('Pod is ready!')
