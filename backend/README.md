
# OREOA

## Deployment

```
git clone https://github.com/kidrek/OREOA.git
cd OREOA/backend/ansible

cp inventory.tpl inventory
-> Set variables in inventory file

ansible-playbook -i inventory -K oreoa.yaml
```

