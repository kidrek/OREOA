# OREOA 



## Deployment

### 1. Deploy backend 

The backend contains the following dockers : 
- Chainsaw
- Elastic Stack (Elasticsearch / Kibana with dashboards & Logstash with pipelines) without authentication
- Hayabusa
- KeepassXC to store Timesketch password
- Plaso
- Regrippy
- Timesketch
- Zircolite


It will be deployed automaticaly by Ansible.

```
git clone https://github.com/kidrek/OREOA.git
cd OREOA/backend/ansible

cp inventory.tpl inventory
-> Set variables in inventory file

ansible-playbook -i inventory -K oreoa.yaml
```

You can access in keepass database to the ```Timesketch``` informations like url/username/password. 
These informations are also automaticaly added in ```.env``` file by Ansible during installation step.

```
keepassxc-cli show --show-protected {PATH}/oreoa.kdbx timesketch 
# The default password of keepass database : oreoa
```

## Workflow

1. Set evidences path and output reports in .env file ;
2. Check that ELK stack & Timesketch dockers are up and and running, if not, you can set to ```false```, ```EXPORT2TIMESKETCH``` or ```EXPORT2ELK``` variables ;
3. Start script ```oreoa.sh```

## Usage

```
./oreoa.sh
```

## Roadmap

- Capability to set variables paths as ```oreoa.sh``` arguments
- Capability to monitor a specific directory to process all new uploaded artifacts
- Add linux workflow 