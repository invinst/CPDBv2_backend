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
    pod_output = call_cmd(f'kubectl get pods -l app={DEPLOYMENT_NAME} -n {namespace} -o json')
    pod_state = json.loads(pod_output)
    return pod_state['items']


def exit_with_log(container_name, pod_name, namespace):
    log = call_cmd(f'kubectl logs {pod_name} {container_name} -n {namespace}')
    print(log)
    sys.stdout.flush()
    sys.exit(1)


def get_pod_names(namespace):
    pods = get_pod_states(namespace)
    return [pod['metadata']['name'] for pod in pods]


def check_pod_status(namespace, pod_names_before_deploy):
    for _ in range(PENDING_CHECK_ATTEMPS):
        waiting = False

        pods = get_pod_states(namespace)
        for pod in pods:
            pod_name = pod['metadata']['name']
            if pod_name in pod_names_before_deploy:
                continue

            if pod['status']['phase'] == 'Pending':
                waiting = True
                print(f'Pod {pod_name} Pending...')
                continue

            for container_status in pod['status']['containerStatuses']:
                container_name = container_status['name']

                if container_status['ready']:
                    print(f'Container {pod_name} {container_name} ready')
                    continue

                if 'terminated' in container_status['state']:
                    print(f'Container {pod_name} {container_name} terminated with following log')
                    exit_with_log(container_name, pod_name, namespace)

                if 'waiting' in container_status['state']:
                    if container_status['restartCount'] > 0:
                        print(f'Container {pod_name} {container_name} failed with following log')
                        exit_with_log(container_name, pod_name, namespace)
                    else:
                        waiting = True
                        print(f'Container {pod_name} {container_name} waiting...')
        if not waiting:
            break
        sys.stdout.flush()
        time.sleep(PENDING_CHECK_INTERVAL)
    else:
        print(f'Deployment takes too long! Doesnt finish in {PENDING_CHECK_ATTEMPS} x {PENDING_CHECK_INTERVAL} seconds')
        sys.stdout.flush()
        sys.exit(1)

    print('Deployment succeed!')


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

    pod_names_before_deploy = get_pod_names(namespace)
    print(f"Pods from previous deploy: {', '.join(pod_names_before_deploy)}")

    call_cmd(f'cat kubernetes/gunicorn.yml | envsubst | kubectl apply -f - --namespace={namespace}')

    check_pod_status(namespace, pod_names_before_deploy)
