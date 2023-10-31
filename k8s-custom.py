from kubernetes import client, config, watch
from datetime import datetime, timedelta
import time

apiversion = "snapshot.storage.k8s.io/v1beta1"
apigroup = "snapshot.storage.k8s.io"
ver="v1beta1"

class Pod:
    def __init__(self, pod):
        self.name = pod.metadata.name
        self.hostname = pod.spec.node_name
        self.resource = pod.spec.container[0].resources
        self.volumes = pod.spec.volumes
        self.pvcinfo = []

    def find_pvc_volumes(self):
        temp_pvc = []
        for i in range(len(self.volumes)):
            if self.volumes[i].persistent_volume_claim != None:
                temp_pvc.append(self.volumes[i].persistent_volume_claim.claim_name)
        self.pvcinfo = temp_pvc

    def get_pvc_detail(self):
        return self.pvcinfo

    def make_snapshot(self, v2, nalzza):
        for pvc in self.pvcinfo:
            snapshot_statement = {"apiVerion": apiversion, "kind": "VolumeSnapshot", "metadata":{"name":"{}-{}".format(pvc,nalzza)}, "spec":{"volumeSnapshotClassName":snapshotstorageclass, "source": {"persistentVolumeClaimName":"{}".format(pvc)}}}
            print(snapshot_statement)
            try:
                v2.create_namespaced_custom_object(group=apigroup, version=ver, namespace=namespace, plural="volumesnapshots", body=snapshot_statement,)
            except Exception as e:
                print("{} {} exception occur: {}".format(nalzza, pvc, e))
                continue

    def get_snapshot_info(self, v2, name):
        try:
            resp = v2.get_namespaced_custom_object(group=apigroup, version=ver, namespace=Namespace, plural="volumesnapshots", name=name)
        except Exception as e:
            print("{} {} exception occur: {}".format(nalzza, pvc, e))
            return False, e
        else:
            return True, resp

    def delete_snapshot(self, v2, daycount, nalzza):
        for pvc in self.pvcinfo:
            now = datetime.now()
            before_2day = now - timedelta(days=daycount)
            deleteday = before_2day.strftime('%Y%m%d')
            snapshot_name = "{}-{}".format(pvc, deleteday)
            print(snapshot_name)
            result, msg = self.get_snapshot_info(v2, snapshot_name)
            print(result)

            if result == True:
                try:
                    resp = v2.delete_namespaced_custom_object(group=apigroup, version=ver, namespace=namespace, plural="volumesnapshots" name=snapshot_name)
                    except Exception as e:
                        print("{} exception occur: {}".format(nalzza, e))
    
    def get_pods_value(v1, name_space):
        pod_list = []

        ret = v1.list_namespaced_pod(name_space)

        for pod in ret.items:
            pod_list.append(pod)

        return pod_list

if __name__ == "__main__":
    #nalzza = datetime.today().strftime("%Y/%m/%d %H:%M:%S.%f")
    nalzza = datetime.today().strftime("%Y/%m/%d")
    #nalzza = nalzza[:-3]

    configuration = client.Configuration()
    configuration.api_key["authorization"] = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.host = hostaddr
    configuration.ssl_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

    v1 = client.CoreV1Api(client.ApiClient(configuration))
    v2 = client.CustomObjectsApi(client.ApiClient(configuration))

    pod_list = get_pods_value(v1, namespace)
    backup_srv = []

    for pod in pod_list:
        temp = Pod(pod)

        for nm in server:
            if nm in temp.name:
                backup_srv.append(temp)
    
    print("{} start snapshot backup server count: ".format(nalzza), len(backup_srv))

    for tmp in backup_srv:
        print(tmp.name)
        tmp.find_pvc_volumes()
        tmp.make_snapshot(v2, nalzza)
        tmp.delete_snapshot(v2, 0, nalzza)