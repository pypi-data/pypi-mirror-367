import os, hvac
import sys
import time
import json
import traceback

def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

def start_vault_client(app):
    # Start the vault first
    # TODO _ instead of sleeping one shoot - may be go on a loop to see 
    # if vault svc is up and running
    time.sleep(20)
    vault_client = hvac.Client(os.environ.get('VAULT_URL', "https://vault:8200"), verify=False)
    print("Starting vault init", file=sys.stdout)
    resp = vault_init(vault_client, app)
    print(json.dumps(resp, indent=4))
    print("Starting vault unseal", file=sys.stdout)
    resp = vault_unseal(vault_client)
    print(json.dumps(resp, indent=4), file=sys.stdout)
    sys.stdout.flush()
    return vault_client

def get_vault_client():
    fh = open("/root/.keys/vault_unseal.keys", "r")
    unseal_info = json.load(fh)
    print("read these unseal keys: ", json.dumps(unseal_info, indent=4), file=sys.stdout)
    sys.stdout.flush()
    fh.close()
    assert "root_token" in unseal_info
    vlt_cl = hvac.Client(os.environ.get('VAULT_URL', "https://vault:8200"), verify=False)
    vlt_cl.token = unseal_info['root_token']
    return vlt_cl

def vault_init(vault_client, app):
    ## public_key = app.config['PUBLIC_KEY']
    try:
        if not vault_client.sys.is_initialized():
            print("Vault not initialized yet", file=sys.stdout)
            shares = 5
            threshold = 3

            wait_count = 0
            while os.path.exists('/root/.keys/vault_unseal.keys') and wait_count < 10:
                # This is a strange situation. Vault is not initialized but the unseal keys exist.
                # Let's wait for a bit to see if it comes back up initialized
                time.sleep(1)
                wait_count += 1
                if vault_client.sys.is_initialized():
                    break
            
            if not vault_client.sys.is_initialized():
                if wait_count == 10:
                    # Hmmm.. vault is still not initialized but the unseal keys exist.
                    # If we proceed to re-init the vault, the old keys will be rendered useless.
                    # Let's just back up the old keys anyway and then try to re-init the vault.
                    import shutil
                    shutil.copy('/root/.keys/vault_unseal.keys', f'/root/.keys/vault_unseal.keys.backup.{time.time()}')                    

                result = vault_client.sys.initialize(shares, threshold)
                print("Initialized vault", file=sys.stdout)
                root_token = result['root_token']
                keys = result['keys']
                # Let's save the keys to a file.
                fh = open("/root/.keys/vault_unseal.keys", "w")
                fh.write(json.dumps(result, indent=4))
                fh.close()
                print("Saved the vault unseal keys in /root/.keys/vault_unseal.keys", file=sys.stdout)


            assert vault_client.sys.is_initialized()
            vault_client.token = root_token
            vault_unseal(vault_client)
            assert not vault_client.sys.is_sealed()
            print("Unsealed vault successfully", file=sys.stdout)


            print("Starting vault config", file=sys.stdout)
            resp = vault_config(vault_client)
            print("Done with vault config", file=sys.stdout)

            response = {}
            response['responsecode'] = "True"
            response['msg'] = "Initialized successfully"
            return response
        else:
            response = {}
            response['responsecode'] = "True"
            response['msg'] = "Already initialized"
            return response
    except Exception as e:
        log("Exception initializing vault: ", traceback.format_exc())
        response = {}
        response['responsecode'] = "False"
        response['msg'] = str(e)
        return response

def vault_unseal(vault_client):
    try:
        if vault_client.sys.is_sealed():
            # print(" ======= VAULT IS SEALED =========")
            fh = open("/root/.keys/vault_unseal.keys", "r")
            result = json.load(fh)
            unseal_response = vault_client.sys.submit_unseal_keys(result['keys'])
            # print("====== unseal response: ", json.dumps(unseal_response, indent=4))
            response = {}
            response['responsecode'] = "True"
            response['msg'] = json.dumps(unseal_response, indent=4)
            return response
        else:
            response = {}
            response['responsecode'] = "True"
            response['msg'] = "Already unsealed"
            # print("===== Vault already unsealed ======")
            return response
    except Exception as e:
        log("vault_unseal exception: ", traceback.format_exc())
        response = {}
        response['responsecode'] = "False"
        response['msg'] = str(e)
        return response



def vault_add_role(vault_client, role, rolecheck):
    #Add the role
    if rolecheck:
       vault_client.auth.jwt.create_role(
           name=role,
           role_type='jwt',
           allowed_redirect_uris=[os.environ.get('VAULT_URL', "https://vault:8200")],
           user_claim='sub',
           bound_claims={'role' : role},
           bound_audiences=['dagknows'],
           token_policies=role+'_policy'
       )
    else:
       vault_client.auth.jwt.create_role(
           name=role,
           role_type='jwt',
           allowed_redirect_uris=[os.environ.get('VAULT_URL', "https://vault:8200")],
           user_claim='sub',
           bound_audiences=['dagknows'],
           token_policies=role+'_policy'
       )
    print("Created a role", file=sys.stdout)
    #Create a secrets engine for this role
    vault_client.sys.enable_secrets_engine(
        backend_type='kv',
        path=role+'_secrets'
    )
    
    print("Created a secrets engine", file=sys.stdout)
    #add a policy so only read access is allowed
    if role == 'admin':
        policy_str='path \"' + role +  '_secrets/*\" {capabilities = [\"read\", \"list\", \"delete\", \"sudo\"]}'
    else:
        policy_str='path \"' + role +  '_secrets/*\" {capabilities = [\"read\", \"list\"]}'

    vault_client.sys.create_or_update_policy(
        name=role+'_policy',
        policy=policy_str,
    )

def vault_add_user(uname, role):
    vault_client = get_vault_client()
    vault_client.secrets.kv.v2.create_or_update_secret(
        path="user_roles/" + uname,
        mount_point="allusers_secrets",
        secret=dict(role=role)
    )

def vault_delete_user(uname):
    log("Entered vault_delete_user: ", uname, file=sys.stdout)
    vault_client = get_vault_client()
    print("Got handle to the client: ", vault_client, file=sys.stdout)
    try:
        resp = vault_client.secrets.kv.v2.delete_latest_version_of_secret(
            path="user_roles/" + uname,
            mount_point="allusers_secrets"
        )
        log("Delete response: ", json.dumps(resp, indent=4), file=sys.stdout)
    except Exception as e:
        print("Got exception ", str(e), file=sys.stderr)
        sys.stderr.flush()


def vault_config(vault_client, public_key=None):
    #Enable JWT authentication
    print("Inside vault config", file=sys.stdout)
    vault_client.sys.enable_auth_method(method_type='jwt')
    print("Enabled jwt authentication", file=sys.stdout)

    if public_key:
        vault_client.auth.jwt.configure(jwt_validation_pubkeys=public_key)
        print("Configured jwt validation public key", file=sys.stdout)

    try:
        vault_add_role(vault_client, 'allusers', rolecheck=False)
    except Exception as e:
        print("ERROR!! Got exception: ", str(e), file=sys.stderr)
        sys.stderr.flush()
    print("Created allusers role", file=sys.stdout)
