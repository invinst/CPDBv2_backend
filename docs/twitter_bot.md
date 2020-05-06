# Twitter bot

Twitter bot (@CPDPbot) is made of 2 parts: webhook run in Django and cpdpbot worker. Below is guidance for webhook. To know how to change cpdpbot worker, look at `docker/cpdpbot/DEVELOPMENT.md`.

## Development
Please make sure you have correct development tokens on local environment (.env file)
- Install `ngrok` to expose webhook to twitter.
- Run backend server
- `ngrok http 8000`.
- Run command `manage.py register_webhook --url=<ngrok_url>/api/v2/twitter/webhook/` to register webhook.
- Run command `manage.py add_account_subscription` and follow the instruction to subscribe twitter account.

## Deployment
This only needs to be done once unless the webhook url or subscrition was changed.
- Run command `manage.py register_webhook --url=https://cpdp.co/api/v2/twitter/webhook/` to register webhook.
- Run command `manage.py add_account_subscription`.
- Go to the provided authenticaton url and login using CPDPBot account (get from 1Password) to get PIN number.
- Input PIN number to continue.

Some other available commands:
- `remove_webhook --id=<webhook_id>` to remove a webhook and all subscriptions.
- `list_webhooks` to list added webhooks.
- `list_subscriptions` to list all subscription accounts.
- `add_owner_subscription` quick command to subscribe the owner of the twitter app.
- `remove_subscription` to remove subscription account.
