variable "kubernetes_admin_username" {}
variable "kubernetes_admin_ssh_pub_key" {}
variable "kubernetes_client_id" {}
variable "kubernetes_client_secret" {}
variable "kubernetes_client_cert" {}
variable "kubernetes_client_key" {}
variable "kubernetes_client_ca_cert" {}
variable "kubernetes_host" {}

resource azurerm_network_security_group "cpdp_akc_nsg" {
  name                = "cpdp-akc-nsg"
  location            = "${azurerm_resource_group.terraformed.location}"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"
}

resource "azurerm_subnet" "cpdp_akc_subnet" {
  name                      = "cpdp-akc-subnet"
  resource_group_name       = "${azurerm_resource_group.terraformed.name}"
  network_security_group_id = "${azurerm_network_security_group.cpdp_akc_nsg.id}"
  address_prefix            = "10.1.0.0/24"
  virtual_network_name      = "${azurerm_virtual_network.cpdp.name}"
}

resource "azurerm_kubernetes_cluster" "cpdp" {
  name                = "cpdp"
  location            = "${azurerm_resource_group.terraformed.location}"
  resource_group_name = "${azurerm_resource_group.terraformed.name}"
  dns_prefix          = "cpdp"

  linux_profile {
    admin_username = "${var.kubernetes_admin_username}"

    ssh_key {
      key_data = "${var.kubernetes_admin_ssh_pub_key}"
    }
  }

  agent_pool_profile {
    name            = "default"
    count           = 1
    vm_size         = "Standard_D2_v3"
    os_type         = "Linux"
    os_disk_size_gb = 30
    vnet_subnet_id  = "${azurerm_subnet.cpdp_akc_subnet.id}"
  }

  service_principal {
    client_id     = "${var.kubernetes_client_id}"
    client_secret = "${var.kubernetes_client_secret}"
  }

  network_profile {
    network_plugin = "azure"
  }
}

provider "kubernetes" {
  version                = "~> 1.1"
  host                   = "${var.kubernetes_host}"
  client_certificate     = "${base64decode(var.kubernetes_client_cert)}"
  client_key             = "${base64decode(var.kubernetes_client_key)}"
  cluster_ca_certificate = "${base64decode(var.kubernetes_client_ca_cert)}"
}

output "kube_config" {
    value = "${azurerm_kubernetes_cluster.cpdp.kube_config_raw}"
}
