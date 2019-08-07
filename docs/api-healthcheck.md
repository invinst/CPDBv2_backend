In our CircleCI config, after deploying the new image to Google Kubernetes Cluster, there's a step that checks the API status of our backend service using `curl`.

Besides returning the response, `curl` also checks for the SSL certification by default (if we're using `https`). The public key list of the trusted CAs that `curl` uses is located at `openssl version -d`.

There may be cases where the SSL certificates used for our server are not in the list, one of the solution is manually adding the public key of the CA (that we bought our SSL certificates from) to the trusted CAs list:
- Find (or ask for) the public key of the CA.
- Add the key to `.circle/extra_certs.pem` with the following format:
  ```
  <ca_1_name>
  ==================
  -----BEGIN CERTIFICATE-----
  <ca_1_public_key>
  -----END CERTIFICATE-----
  <ca_2_name>
  ==================
  -----BEGIN CERTIFICATE-----
  <ca_2_public_key>
  -----END CERTIFICATE-----
  ...
  ```
- Update the corresponding secret file with `git secret hide`.
