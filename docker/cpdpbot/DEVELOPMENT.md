# Development

- Make sure you have revealed secrets (`git secret reveal`)
- Download and install [Microsoft Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer/). This is the tool to push message into queue and test that it works for your twitterbot.
- In Azure Storage Explorer, log into storage account using `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_STORAGE_ACCOUNT_KEY` in `local.env`
- `docker-compose build`
- Run the cpdpbot: `docker-compose up cpdpbot` - Logs should show up for you now.
- Run test: `docker run --rm -v "$(pwd)/docker/cpdpbot:/app" cpdbv2_backend_cpdpbot python -m cpdpbot.test`
