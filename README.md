# OREOA 

Here is OREOA, a project aimed at providing an automated processing solution for data collected during a digital forensics investigation.
The solution first focuses on standardizing the format of the collected data, followed by an initial analysis to detect any suspicious or malicious behavior (using tools such as Zircolite, Hayabusa, and others). Finally, the processed data is indexed into an ElasticSearch instance and visualized in Timesketch, to support and streamline the analysts' work.

## ROADMAP

* CLAMAV : https://gitlab.com/CinCan/tools/-/tree/master/stable/clamav

## Deployment

### 1. Deploy backend 

The backend is automatically deployed via Ansible.  
Here are the solutions deployed:
  
* Data processing

| Solution          | Description courte                                                          | Type d'artefact traité                            | Lien officiel/documentation                               |
| ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------- |
| **Plaso**         | Framework pour la création de chronologies à partir d’artefacts forensiques | Fichiers système, journaux, artefacts multiples   | [Plaso](https://plaso.readthedocs.io/en/latest/)          |

  
* Data analysis  

| Solution          | Description courte                                                          | Type d'artefact traité                            | Lien officiel/documentation                               |
| ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------- |
| **Chainsaw**      | Outil rapide d'analyse de logs Windows EVTX basé sur des règles Sigma       | Journaux d’événements Windows (.evtx)             | [Chainsaw](https://github.com/WithSecureLabs/chainsaw)    |
| **Hayabusa**      | Analyse rapide des journaux Windows EVTX basée sur Sigma                    | Journaux d’événements Windows (.evtx)             | [Hayabusa](https://github.com/Yamato-Security/hayabusa)   |
| **Regrippy**      | Outil d’analyse des hives de registre Windows en ligne de commande          | Hives de registre Windows (NTUSER.DAT, SYSTEM...) | [Regrippy](https://github.com/airbus-cert/regrippy)       |
| **Zircolite**     | Analyse légère et rapide de logs EVTX avec détection via règles Sigma       | Journaux d’événements Windows (.evtx)             | [Zircolite](https://github.com/wagga40/zircolite)         |


* Data indexing

| Solution          | Description courte                                                          | Type d'artefact traité                            | Lien officiel/documentation                               |
| ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------- |
| **Elastic Stack** | Suite d’outils pour la collecte, l’analyse et la visualisation de données   | Données indexées diverses (logs, JSON, etc.)      | [Elastic Stack](https://www.elastic.co/what-is/elk-stack) |
| **Timesketch**    | Outil de visualisation et d’analyse de chronologies forensiques             | Chronologies d’événements                         | [Timesketch](https://timesketch.org)                      |



Here is how to deploy backend :

```bash
$ git clone https://github.com/kidrek/OREOA.git
$ cd OREOA/backend/ansible

$ cp inventory.tpl inventory
-> Set variables in inventory file

$ ansible-playbook -i inventory -K oreoa.yaml
```

For security reasons, Timesketch credentials are stored in one keepass database in this path : ```{PATH}/OREOA/oreoa_deployed/oreoa.kdbx```.

These informations are also automaticaly added in ```OREOA/.env``` file by Ansible during installation step.

```bash
keepassxc-cli show --show-protected {PATH}/OREOA/oreoa_deployed/oreoa.kdbx timesketch 
# The default password of keepass database : oreoa
```

## Workflow


1. Set evidences path and output reports in ```.env``` file ;
2. Create a sketch in timesketch and set ```timesketch_sketch_id``` in ```.env``` file;
3. Check that ELK stack & Timesketch dockers are up and and running, if not, you can set to ```false```, ```EXPORT2TIMESKETCH``` or ```EXPORT2ELK``` variables ;
4. Start script 


```
./oreoa.sh
```

## Roadmap

- Capability to set variables paths as ```oreoa.sh``` arguments
- Capability to monitor a specific directory to process all new uploaded artifacts
- Add linux workflow 
- Add tools
  - Loki / Thor Light
  - ClamAV
  - Yara