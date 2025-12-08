
push sur la branche main ---> déploie vers la webapp "monwebgratuit123-linux"

push sur la branche PPRD ---> déploie vers la webapp "monwebgratuit123-linux-PPRD"

===========================

Créer une Webapp linux sur azure liée avec le push sur la branche PPRD de mon REPO : 

az group create --name rg-webpp-gratuit-linux-PPRD --location "France Central"

az appservice plan create \
    --name PlanLinuxPython-PPRD \
    --resource-group rg-webpp-gratuit-linux-PPRD \
    --sku B1 \
    --is-linux

az webapp create \
    --resource-group rg-webpp-gratuit-linux-PPRD \
    --plan PlanLinuxPython-PPRD \
    --name monwebgratuit123-linux-PPRD \
    --runtime "PYTHON:3.12"

az webapp deployment source config \
    --name monwebgratuit123-linux-PPRD \
    --resource-group rg-webpp-gratuit-linux-PPRD \
    --repo-url https://github.com/soufianetalibi/monwebgratuit123-linux \
    --branch PPRD \
    --manual-integration

Et vérifier le déploiement : 
az webapp browse --name monwebgratuit123-linux-PPRD --resource-group rg-webpp-gratuit-linux-PPRD
