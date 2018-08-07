output "postgres_staging_fqdn" {
  value = "${azurerm_postgresql_server.staging.fqdn}"
}

output "postgres_staging_login" {
  value = "${azurerm_postgresql_server.staging.administrator_login}"
}

output "postgres_staging_password" {
  value = "${azurerm_postgresql_server.staging.administrator_login_password}"
}

output "postgres_production_fqdn" {
  value = "${azurerm_postgresql_server.production.fqdn}"
}

output "postgres_production_login" {
  value = "${azurerm_postgresql_server.production.administrator_login}"
}

output "postgres_production_password" {
  value = "${azurerm_postgresql_server.production.administrator_login_password}"
}
