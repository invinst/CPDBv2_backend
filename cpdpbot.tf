variable "staging_twitter_consumer_key" {}
variable "staging_twitter_consumer_secret" {}
variable "staging_twitter_app_token_key" {}
variable "staging_twitter_app_token_secret" {}
variable "production_twitter_consumer_key" {}
variable "production_twitter_consumer_secret" {}
variable "production_twitter_app_token_key" {}
variable "production_twitter_app_token_secret" {}
variable "papertrail_endpoint" {}
variable "papertrail_port" {}
variable "cpdpbot_version" {
  default = "0.1.2"
}

resource "kubernetes_replication_controller" "cpdpbot_staging" {
  metadata {
    name = "cpdpbot"
    labels = {
      app = "cpdpbot"
    }
    namespace = "${kubernetes_namespace.staging.metadata.0.name}"
  }

  spec {
    selector {
      app = "cpdpbot"
    }
    template {
      container {
        image = "cpdbdev/cpdpbot:${var.cpdpbot_version}"
        name  = "cpdpbot"
        image_pull_policy = "Always"
        env   = [
          {
            name  = "AZURE_QUEUE_NAME"
            value = "cpdpbot"
          },
          {
            name  = "TWITTER_CONSUMER_KEY"
            value = "${var.staging_twitter_consumer_key}"
          },
          {
            name  = "TWITTER_CONSUMER_SECRET"
            value = "${var.staging_twitter_consumer_secret}"
          },
          {
            name  = "TWITTER_APP_TOKEN_KEY"
            value = "${var.staging_twitter_app_token_key}"
          },
          {
            name  = "TWITTER_APP_TOKEN_SECRET"
            value = "${var.staging_twitter_app_token_secret}"
          },
          {
            name  = "AZURE_STORAGE_ACCOUNT_NAME"
            value = "${azurerm_storage_account.staging.name}"
          },
          {
            name  = "AZURE_STORAGE_ACCOUNT_KEY"
            value = "${azurerm_storage_account.staging.primary_access_key}"
          },
          {
            name  = "PAPERTRAIL_ENDPOINT"
            value = "${var.papertrail_endpoint}"
          },
          {
            name  = "PAPERTRAIL_PORT"
            value = "${var.papertrail_port}"
          },
        ]
      }
    }
  }
}

resource "kubernetes_replication_controller" "cpdpbot_master" {
  metadata {
    name = "cpdpbot"
    labels = {
      app = "cpdpbot"
    }
    namespace = "${kubernetes_namespace.production.metadata.0.name}"
  }

  spec {
    selector {
      app = "cpdpbot"
    }
    template {
      container {
        image = "cpdbdev/cpdpbot:${var.cpdpbot_version}"
        name  = "cpdpbot"
        image_pull_policy = "Always"
        env   = [
          {
            name  = "AZURE_QUEUE_NAME"
            value = "cpdpbot"
          },
          {
            name  = "TWITTER_CONSUMER_KEY"
            value = "${var.production_twitter_consumer_key}"
          },
          {
            name  = "TWITTER_CONSUMER_SECRET"
            value = "${var.production_twitter_consumer_secret}"
          },
          {
            name  = "TWITTER_APP_TOKEN_KEY"
            value = "${var.production_twitter_app_token_key}"
          },
          {
            name  = "TWITTER_APP_TOKEN_SECRET"
            value = "${var.production_twitter_app_token_secret}"
          },
          {
            name  = "AZURE_STORAGE_ACCOUNT_NAME"
            value = "${azurerm_storage_account.production.name}"
          },
          {
            name  = "AZURE_STORAGE_ACCOUNT_KEY"
            value = "${azurerm_storage_account.production.primary_access_key}"
          },
          {
            name  = "PAPERTRAIL_ENDPOINT"
            value = "${var.papertrail_endpoint}"
          },
          {
            name  = "PAPERTRAIL_PORT"
            value = "${var.papertrail_port}"
          },
        ]
      }
    }
  }
}
