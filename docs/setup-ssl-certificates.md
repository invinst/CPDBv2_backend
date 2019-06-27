# Setup SSL certificate

## Activate Certificate
- Login into https://www.ssls.com/ => Purchased certs
- Click to active the certificate for specific domain
- Save the private key ([private-key].zip)
- Active domain with DNS-based validation ([details link](https://helpdesk.ssls.com/hc/en-us/articles/206957109-How-can-I-complete-the-domain-control-validation-DCV-for-my-SSL-certificate-))
- Verify that domain become active
- Save the certificates zip file ([domain-name].zip)

## Add certificates to server
Use 2 files [private-key].zip and [domain-name].zip from [Activate Certificate](#activate-certificate) process

### Update tls secrets for *.cpdp.co
- Make sure you're on `master` branch
 
- Update secret named `tls-secret` in kubernetes/secrets-production.yml.secret
    - tls.crt: 
        - file [domain-name].crt from [domain-name].zip encode base64
        - command: `cat [domain-name].crt | base64`
    - tls.key: 
        - file [private-key].txt from [private-key].zip encode base64
        - command: `cat [private-key].crt | base64`
        
- Update new secrets to production & staging

    - IMPORTANT NOTE: 
        - make sure we delete the secret `tls-secret` before applying the new secrets.
        - The certificate will be applied immediately after we apply new secrets without any deployment.

    - Commands: 
        - `kubectl delete secret tls-secret -n $NAMESPACE`
        - `kubectl apply -f kubernetes/secrets-$NAMESPACE.yml`
    
- Commit changes and create Pull Request to `develop` and `master` branches.

### Update tls secrets for *.cpdb.co
- Make sure you're on `master` branch

- Update secret field named `cpdb-co-tls-secret` in kubernetes/secrets-production.yml.secret
    - tls.crt: 
        - file [domain-name].crt from [domain-name].zip encode base64
        - command: `cat [domain-name].crt | base64`
    - tls.key: 
        - file [private-key].txt encode base64
        - command: `cat [private-key].txt | base64`

- Update new secrets to production

    - IMPORTANT NOTE: 
        - make sure we delete the secret `cpdb-co-tls-secret` before applying the new secrets.
        - The certificate will be applied immediately after we apply new secrets without any deployment.

    - Commands: 
        - `kubectl delete secret cpdb-co-tls-secret -n $NAMESPACE`
        - `kubectl apply -f kubernetes/secrets-$NAMESPACE.yml`

- Commit changes and create Pull Request to `develop` and `master` branches.
