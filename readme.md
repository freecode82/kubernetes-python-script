# kcmd.py
kubernetes commnad tool

-s podname

If you enter a common pod name, all pods belonging to that name will be subject to command execution.

-c command

## ex) kcmd.py -s abc-pod -c "ls -l"


# k8s-custom.py
Create a snapshot using the kubernetes python API

 # k8s-command.py 
This is an example of deleting a pod using the kubernetes python API.
Passes a command to print the directory list to the pod. If the delivered result contains an input/output error, the pod is restarted.
