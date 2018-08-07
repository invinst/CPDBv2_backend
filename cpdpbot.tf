variable "staging_twitter_consumer_key" {}
variable "staging_twitter_consumer_secret" {}
variable "staging_twitter_app_token_key" {}
variable "staging_twitter_app_token_secret" {}

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
        image = "cpdbdev/cpdpbot:latest"
        name  = "cpdpbot"
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
        ]
      }
    }
  }
}

# resource "kubernetes_pod" "cpdpbot_staging" {
#   metadata {
#     name      = "cpdpbot"
#     namespace = "${kubernetes_namespace.staging.metadata.0.name}"
#   }

#   spec {
#     container {
#       image = "cpdbdev/cpdpbot:0.1.0"
#       name  = "cpdpbot"
#       env   = [
#         {
#           name  = "AZURE_QUEUE_NAME"
#           value = "cpdpbot"
#         },
#         {
#           name  = "TWITTER_CONSUMER_KEY"
#           value = "${var.staging_twitter_consumer_key}"
#         },
#         {
#           name  = "TWITTER_CONSUMER_SECRET"
#           value = "${var.staging_twitter_consumer_secret}"
#         },
#         {
#           name  = "TWITTER_APP_TOKEN_KEY"
#           value = "${var.staging_twitter_app_token_key}"
#         },
#         {
#           name  = "TWITTER_APP_TOKEN_SECRET"
#           value = "${var.staging_twitter_app_token_secret}"
#         },
#         {
#           name  = "AZURE_STORAGE_ACCOUNT_NAME"
#           value = "${azurerm_storage_account.staging.name}"
#         },
#         {
#           name  = "AZURE_STORAGE_ACCOUNT_KEY"
#           value = "${azurerm_storage_account.staging.primary_access_key}"
#         },
#       ]
#     }
#   }
# }
