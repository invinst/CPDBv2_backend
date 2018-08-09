variable "kubernetes_admin_username" {}
variable "kubernetes_admin_ssh_pub_key" {}
variable "kubernetes_client_id" {}
variable "kubernetes_client_secret" {}

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
    vm_size         = "Standard_D1_v2"
    os_type         = "Linux"
    os_disk_size_gb = 30
  }

  service_principal {
    client_id     = "${var.kubernetes_client_id}"
    client_secret = "${var.kubernetes_client_secret}"
  }
}

provider "kubernetes" {
  version                = "~> 1.1"
  host                   = "${azurerm_kubernetes_cluster.cpdp.kube_config.0.host}"
  username               = "${azurerm_kubernetes_cluster.cpdp.kube_config.0.username}"
  password               = "${azurerm_kubernetes_cluster.cpdp.kube_config.0.password}"
  client_certificate     = "${base64decode(azurerm_kubernetes_cluster.cpdp.kube_config.0.client_certificate)}"
  client_key             = "${base64decode(azurerm_kubernetes_cluster.cpdp.kube_config.0.client_key)}"
  cluster_ca_certificate = "${base64decode(azurerm_kubernetes_cluster.cpdp.kube_config.0.cluster_ca_certificate)}"
}

resource "kubernetes_namespace" "staging" {
  metadata {
    name = "staging"
  }
}

output "kube_config" {
    value = "${azurerm_kubernetes_cluster.cpdp.kube_config_raw}"
}
