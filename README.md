# DeploymentScaler

## Description

This project was created to make upgrading Kubernetes a faster process when 
applied to large clusters. This will store all current deployments for a 
configured namespace, then set the replica set count to zero for those
deployments. Once the Kubernetes update is complete, a subsequent run of
this script will restore the replica set count for all deployments.

Notes:
* This only stops deployments. ReplicaSets and StatefulSets are not included.
* Not tested on Windows.

## Dependencies
Package dependencies are stored in requirements.txt. Other dependencies:
* Python 3 (not tested on < 3.8.10)
* The script assumes that .kube/config will be present in the user's home directory. 


## Using the script

Set the target namespace in main.py inside main(). Open a shell session and
navigate to the script's directory.
```
python ./main.py
```
You will see a list of all available contexts from your .kube/config file. Choose
a context using up/down arrow keys, then press Enter.

Select a process. Options are:
* stop pods
* restore pods
* cancel

If you choose to stop pods, the replica count of all existing deployments will be
stored in a .json file in the same directory. If the count is zero, the scipt will
abort. This helps prevent human error (i.e. stopping a second time and recording
zero for all replica counts). 

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
* The namespace is hard-coded in the script. A future version will
allow selection from available namespaces.
* ReplicaSets and StatefulSets are not included, as Deployments reduced running pods by 90%, enough to speed up the Kubernetes upgrade. Adding these may be valuable in other situations.

## Contributing
Reach me by email if you have ideas for additional features: jeff@bitsalt.com.

## License
Licensed under AGPL 3.0. See the included file.
