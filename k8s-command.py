#!/usr/bin/python3
from kubernetes import client, config, watch
from kubernetes.stream import stream
import subprocess
from datetime import datetime

hostaddr = "https://192.168.79.245:6443"
namespace = "default"

def get_dir_location(server, v1):
    exec_command=['/bin/bash','-c','df -h | grep home']

    try:
        resp = stream(v1.connect_get_namespaced_pod_exec, server, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False, _preload_content=True)
    except Exception as e:
        msg = "{} exception occur, guess pod is not running or pod use two container".format(e)
        return False, msg
    else:
        directory = resp.split()
        if directory == []:
            msg = "command result nothing"
            return False, msg
        else:
            print("{} command result:".format(server), directory[5]);
            return True, directory[5]

def get_ls_dir(server, directory, v1):
    cmd = ['/bin/bash', '-c', 'ls {}'.format(directory)]

    try:
        resp = stream(v1.connect_get_namespaced_pod_exec, server, namespace, command=cmd, stderr=True, stdin=False, stdout=True, tty=False)
    except Exception as e:
        msg = "{} exception occur".format(e)
        print(msg)
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

    server_list = {}
    restart_server_list = []

    for svr in podes:
        result, msg = get_dir_location(svr, v1)
        if result == False:
            message = "{} {} {}".format(nalzza, svr, msg)
            print(message)
        else:
            server_list[svr] = msg

    print("home directory exist server list: ", server_list)

    with open(log_name, 'a') as f:
        for svr, dirname in server_list.items():
            print(svr, dirname)
            pandan, result = get_ls_dir(svr, dirname, v1)
            print(result)
            allmsg = "{} {} {}\n".format(nalzza, svr, pandan, result)
            print(allmsg)
            f.write(allmsg)

            if "Input/output error" in result:
                err_msg = "{} {} {}".format(nalzza, svr, result)
                f.write(err_msg)
                print(err_msg)
                restart_server_list.append(svr)

        print("restart server list:", restart_server_list)
        temp_server_list = []
        temp_op_list = []

        for svr in restart_server_list:
            if 'xxxx' in svr:
                temp_op_list.append(svr)
            else:
                temp_server_list.append(svr)

        for svr in temp_op_list:
            temp_server_list.append(svr)
        f.write("restart server list:\n")
        f.write("".join(restart_server_list))
        f.write("\n")

        print("orderded server list: ", temp_server_list)
        print("delete pod start")

        for svr in temp_server_list:
            try:
                api_response = v1.delete_namespaced_pod(svr, namespace)
                print(api_response)
                msg = "{} {} delete pod\n".format(nalzza, svr)
                f.write(msg)
            except ApiException as e:
                msg = "Exception when calling CoreV1Api->delete_namespaced_pod:{}\n".format(e)
                f.write(msg)
                continue