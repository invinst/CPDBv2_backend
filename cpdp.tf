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
  location = "North Central US"
}

resource "azurerm_postgresql_server" "staging" {
  name                = "postgresql-server-staging"
  location            = "${azurerm_resource_group.terraformed.location}"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"

  sku {
    name = "B_Gen4_1"
    capacity = 1
    tier = "Basic"
    family = "Gen4"
  }

  storage_profile {
    storage_mb = 5120
    backup_retention_days = 7
    geo_redundant_backup = "Disabled"
  }

  administrator_login = "${var.postgres_admin_login}"
  administrator_login_password = "${var.postgres_admin_password}"
  version = "9.6"
  ssl_enforcement = "Enabled"
  tags {
    Name = "staging"
  }
}

resource "azurerm_postgresql_firewall_rule" "staging" {
  name                = "internet"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"
  server_name         = "${azurerm_postgresql_server.staging.name}"
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}

resource "azurerm_postgresql_server" "production" {
  name                = "postgresql-server-production"
  location            = "${azurerm_resource_group.terraformed.location}"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"

  sku {
    name = "GP_Gen5_2"
    capacity = 2
    tier = "GeneralPurpose"
    family = "Gen5"
  }

  storage_profile {
    storage_mb = 5120
    backup_retention_days = 35
    geo_redundant_backup = "Enabled"
  }

  administrator_login = "${var.postgres_admin_login}"
  administrator_login_password = "${var.postgres_admin_password}"
  version = "9.6"
  ssl_enforcement = "Enabled"
  tags {
    Name = "production"
  }
}

resource "azurerm_postgresql_firewall_rule" "production" {
  name                = "internet"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"
  server_name         = "${azurerm_postgresql_server.production.name}"
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}
