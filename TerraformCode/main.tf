# 1. Create the Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}
# 2. The Azure foundry or openai Account (The Service)
resource "azurerm_cognitive_account" "ai_resource" {
  name                = var.ai_resource_account_name
  location            = var.location
  resource_group_name = var.resource_group_name
  # Conditional Kind: "AIServices" for Foundry, "OpenAI" for standard
  kind     = var.use_ai_foundry ? "AIServices" : "OpenAI"
  sku_name = "S0"
  # REQUIRED for AI Foundry Projects
  # If true, it enables management; if false, it sets to null (standard OpenAI behavior)
  project_management_enabled = var.use_ai_foundry ? true : false

  # A custom subdomain is mandatory when project_management_enabled is true
  custom_subdomain_name = var.use_ai_foundry ? var.ai_resource_account_name : null
  identity {
    type = "SystemAssigned"
  }
  depends_on = [azurerm_resource_group.rg]
}
#2.1 If using AI Foundry, we need to create a Project to host the deployment
resource "azurerm_cognitive_account_project" "project" {
  count                = var.use_ai_foundry ? 1 : 0
  name                 = var.ai_project_name
  cognitive_account_id = azurerm_cognitive_account.ai_resource.id
  location             = var.location
  identity {
    type = "SystemAssigned"
  }
}


# 3. The specific Model Deployment (The "Brain")
resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = var.deployment_name
  cognitive_account_id = azurerm_cognitive_account.ai_resource.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }

  sku {
    name = "GlobalStandard"
  }
  depends_on = [azurerm_cognitive_account.ai_resource]
}

# Outputs the Endpoint to your terminal after deployment
output "ai_resource_endpoint" {
  value = azurerm_cognitive_account.ai_resource.endpoint
}
output "ai_resource_primary_key" {
  value     = azurerm_cognitive_account.ai_resource.primary_access_key
  sensitive = true
}