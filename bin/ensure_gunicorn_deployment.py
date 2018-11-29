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


def exit_with_log(container_name, pod_name, namespace):
    log = call_cmd('kubectl logs %s %s -n %s' % (pod_name, container_name, namespace))
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
                print('Pod %s Pending...' % pod_name)
                continue

            for container_status in pod['status']['containerStatuses']:
                container_name = container_status['name']

                if container_status['ready']:
                    print('Container %s %s ready' % (pod_name, container_name))
                    continue

                if 'terminated' in container_status['state']:
                    print('Container %s %s terminated with following log' % (pod_name, container_name))
                    exit_with_log(
                        container_name, pod_name, namespace
                    )

                if 'waiting' in container_status['state']:
                    if container_status['restartCount'] > 0:
                        print('Container %s %s failed with following log' % (pod_name, container_name))
                        exit_with_log(
                            container_name, pod_name, namespace
                        )
                    else:
                        waiting = True
                        print('Container %s %s waiting...' % (pod_name, container_name))
        if not waiting:
            break
        sys.stdout.flush()
        time.sleep(PENDING_CHECK_INTERVAL)
    else:
        print(
            'Deployment takes too long! Doesnt finish in %d x %d seconds' %
            (PENDING_CHECK_ATTEMPS, PENDING_CHECK_INTERVAL)
        )
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
    print('Pods from previous deploy: %s' % ', '.join(pod_names_before_deploy))

    call_cmd('cat kubernetes/gunicorn.yml | envsubst | kubectl apply -f - --namespace=%s' % namespace)

    check_pod_status(namespace, pod_names_before_deploy)
