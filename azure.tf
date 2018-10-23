provider "azurerm" {
  version = "~> 1.11"
}

# All resources managed by Terraform should be created under
# this resource group. Also do not put resource into this group
# by any mean other than Terraform. Failure to do so mean
# Terraform could mistakenly destroy resources that it has no
# knowledge of.
resource "azurerm_resource_group" "terraformed" {
  name     = "terraformed"
  location = "Central US"
}

resource "azurerm_storage_account" "staging" {
  name                     = "cpdpstaging"
  resource_group_name      = "${azurerm_resource_group.terraformed.name}"
  location                 = "${azurerm_resource_group.terraformed.location}"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags {
    environment = "staging"
  }
}

resource "azurerm_storage_account" "production" {
  name                     = "cpdpproduction"
  resource_group_name      = "${azurerm_resource_group.terraformed.name}"
  location                 = "${azurerm_resource_group.terraformed.location}"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags {
    environment = "production"
  }
}

resource "azurerm_virtual_network" "cpdp" {
  name                = "cpdp-vnet"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"
  location            = "${azurerm_resource_group.terraformed.location}"
  address_space       = ["10.1.0.0/16"]
}

output "staging_storage_account_name" {
  value = "${azurerm_storage_account.staging.name}"
}

output "staging_storage_account_key" {
  value = "${azurerm_storage_account.staging.primary_access_key}"
}

output "production_storage_account_name" {
  value = "${azurerm_storage_account.production.name}"
}

output "production_storage_account_key" {
  value = "${azurerm_storage_account.production.primary_access_key}"
}
