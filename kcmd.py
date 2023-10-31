#!/usr/bin/python3
from kubernetes import client, config, watch
from kubernetes.stream import stream
import sys
import argparse
from datetime import datetime

hostaddr = "https://192.168.79.245:6443" #change your kubernetes ip and port
namespace = "default" #change your namespace

parser = argparse.ArgumentParser();
parser.add_argument("-s", help="server name")
parser.add_argument("-c", help="command")
args = parser.parse_args()

def get_cmd(server, cmdstr, v1):
    exec_command=['/bin/bash','-c', cmdstr]

    try:
        resp = stream(v1.connect_get_namespaced_pod_exec, server, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False, _preload_content=True)
    except Exception as e:
        msg = "{} exception occur".format(e)
        return False, msg
    else:
        return True, resp


def get_pods_value(v1, name_space):
    pod_value = {}

    ret = v1.list_namespaced_pod(name_space)

    for pod in ret.items:
        pod_value[pod.metadata.name] = {'hostname':pod.spec.node_name, 'resource': pod.spec.containers[0].resources}

    return pod_value

def get_pod(pod_list):
    pod_names = []

    for k, _ in pod_list.items():
        pod_names.append(k)

    return pod_names

if __name__ == "__main__":
    nalzza = datetime.today().strftime("%Y/%m/%d %H:%M:%S.%f")
    nalzza = nalzza[:-3]

    configuration = client.Configuration()
    configuration.api_key["authorization"] = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.host = hostaddr
    configuration.ssl_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

    v1 = client.CoreV1Api(client.ApiClient(configuration))

    pod_list = get_pods_value(v1, namespace)
    podes = get_pod(pod_list)

    newpodes = []
    for pod in podes:
        if args.s in pod:
            newpodes.append(pod)

    for svr in newpodes:
        result, msg = get_cmd(svr, argc.c, v1)
        print("================== {} ==================".format(svr))
        print(msg)
        print("========================================")