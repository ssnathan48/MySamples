variable "subscription_id" {
  type        = string
  description = "The Azure Subscription ID"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the existing Resource Group"
}

variable "location" {
  type        = string
  default     = "East US"
  description = "Azure region (ensure it supports gpt-4o-mini)"
}

variable "ai_resource_account_name" {
  type        = string
  description = "Unique name for the OpenAI or foundry resource"
}

variable "ai_project_name" {
  type        = string
  description = "Unique name for the ai foundry project (if using foundry)"
}

variable "deployment_name" {
  type        = string
  default     = "gpt-4o-mini-deployment"
  description = "The name you will use in your Python code"
}
variable "use_ai_foundry" {
  type        = bool
  default     = true
  description = "Set to true for Azure AI Foundry (AIServices), false for standalone OpenAI."
}
