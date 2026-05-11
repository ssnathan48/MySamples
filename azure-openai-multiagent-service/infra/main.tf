terraform {
  required_providers {
    azapi = {
      source = "azure/azapi"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "azapi" {}

# Reference your existing Resource Group
data "azurerm_resource_group" "existing" {
  name = "rg-multiagent" 
}

# Reference your existing Foundry Project
data "azapi_resource" "foundry_project" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01-preview"
  name      = "proj-foundry-multiagent"
  parent_id = data.azurerm_resource_group.existing.id
}

output "foundry_project_id" {
  value = data.azapi_resource.foundry_project.id
}
