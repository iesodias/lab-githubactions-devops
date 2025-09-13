Erro durante validação do terraform no github actions ao buscar a secrets.ARM_SUBSCRIPTION_ID
- name: Validar Sintaxe e Plano
  working-directory: infra
  run: |
    export ARM_SUBSCRIPTION_ID=${{ secrets.ARM_SUBSCRIPTION_ID }}
    terraform init
    terraform fmt -check
    terraform validate
    terraform plan -out=tfplan


Durante essa etapa de validação no github actions estou recebendo esse erro em negrito ao final desse código na etapa de validação :


Run export ARM_SUBSCRIPTION_ID=***

Initializing the backend...

Successfully configured the backend "azurerm"! Terraform will automatically

use this backend unless the backend configuration changes.

Initializing provider plugins...

- Finding latest version of hashicorp/azurerm...

- Installing hashicorp/azurerm v4.43.0...

- Installed hashicorp/azurerm v4.43.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider

selections it made above. Include this file in your version control repository

so that Terraform can guarantee to make the same selections by default when

you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see

any changes that are required for your infrastructure. All Terraform commands

should now work.

If you ever set or change modules or backend configuration for Terraform,

rerun this command to reinitialize your working directory. If you forget, other

commands will detect it and remind you to do so if necessary.

backend.tf

outputs.tf

variables.tf

Error: Terraform exited with code 3.

Error: Process completed with exit code 1.



===========

Quando eu valido manualmente adicionando o subscription_id no main.tf recebo o OK, mas mesmo passando meu Subscription ID para a secret ARM_SUBSCRIPTION_ID no repositório, trava nessa etapa durante o github actions.

1 respostas

Marcos Mourão Rodrigues Junior
2 dias atrás
Atualização.

Precisei fazer algumas adições e alterações nos arquivos deploy.yml, main.tf e variables.tf para que o código executasse.



variables.tf: (adição)

variable "subscription_id" {
  type = string
}


main.tf: (alteração)

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.subscription_id  
}


E em cada local do arquivo deploy.yml precisei substituir  export ARM_SUBSCRIPTION_ID=${{ secrets.ARM_SUBSCRIPTION_ID }} por:

env:
  ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
  TF_VAR_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}


deploy.yml: (alteração)

- name: Aplicar Terraform
    working-directory: infra
    env:
      ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      TF_VAR_subscription_id: ${{ secrets.ARM_SUBSCRIPTION_ID }}
    run: |          
      terraform init
      terraform state rm azurerm_resource_group.rg || true
      terraform import azurerm_resource_group.rg /subscriptions/${{ secrets.ARM_SUBSCRIPTION_ID }}/resourceGroups/rg-tfstate 
      terraform apply -auto-approve


Precisei adicionar tbm a importação do resource group já que o tfstate reconhece que já existe um resource group criado.  Isto é, de acordo com o tfstate que faz o reconhecimento da infraestutura atual caso ele já tenha criado algum recurso ele não criará novamente por causa da sua indempotência, também caso o recurso tenha sido criado por outra fonte ele não reconhece, então é preciso importar para o tfstate, ou remover do tfstate para adicionar novamente em cada vez que o pipeline for executado.

terraform state rm azurerm_resource_group.rg || true
terraform import azurerm_resource_group.rg /subscriptions/${{ secrets.ARM_SUBSCRIPTION_ID }}/resourceGroups/rg-tfstate 