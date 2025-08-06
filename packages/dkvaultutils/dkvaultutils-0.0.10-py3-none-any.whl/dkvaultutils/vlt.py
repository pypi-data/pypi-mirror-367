import hvac
import readline
import argparse
import sys
import json
import requests
import base64
import re
from os import listdir
from os.path import isfile, join
from getpass import getpass
from vault_lib import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

token_fh = open("src/keys/vault_unseal.keys")
tokens_content = json.load(token_fh)

vapi = dagknows_proxy_vault('https://vault:8200', tokens_content['root_token'])


def print_help():
    print(bcolors.OKGREEN + "Version 1.2" + bcolors.ENDC)
    print(bcolors.OKGREEN + "Available commands: " + bcolors.ENDC)
    print("add_role", file=sys.stdout)
    print("delete_role", file=sys.stdout)
    print("list_roles", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("add_credentials", file=sys.stdout)
    print("delete_credentials", file=sys.stdout)
    print("get_credentials", file=sys.stdout)
    print("list_credentials", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("add_inventory", file=sys.stdout)
    print("add_ip_addr", file=sys.stdout)
    print("delete_ip_addr", file=sys.stdout)
    print("get_ip_addr", file=sys.stdout)
    print("list_ip_addrs", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("add_ip_label", file=sys.stdout)
    print("add_ip_label_regex", file=sys.stdout)
    print("delete_ip_label", file=sys.stdout)
    print("get_ip_label", file=sys.stdout)
    print("list_ip_labels", file=sys.stdout)
    print("list_ip_label_regex", file=sys.stdout)
    print("delete_ip_label_regex", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("add_url_label", file=sys.stdout)
    print("delete_url_label", file=sys.stdout)
    print("get_url_label", file=sys.stdout)
    print("list_url_labels", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("create_host_group", file=sys.stdout)
    print("add_hosts_to_group", file=sys.stdout)
    print("delete_host_group", file=sys.stdout)
    print("delete_hosts_from_group", file=sys.stdout)
    print("get_host_group", file=sys.stdout)
    print("list_host_groups", file=sys.stdout)
    print("\n", file=sys.stdout)
    print("add_user", file=sys.stdout)
    print("delete_user", file=sys.stdout)
    print("get_user", file=sys.stdout)
    print("list_users", file=sys.stdout)
    print("\n", file=sys.stdout)
    




while True:

    command = input(bcolors.OKBLUE + "command (type 'help' to list or 'exit' to quit): " + bcolors.ENDC).strip()
    if command == "help":
        print_help()
    elif command == 'exit' or command == 'quit':
        break
    elif command == 'add_role':
        role = input(bcolors.OKBLUE + "name of the role: " + bcolors.ENDC).strip()
        vapi.add_role(role)
        print("Added role: ", role, file=sys.stdout)
        sys.stdout.flush()
    elif command == 'list_roles':
        print(bcolors.OKGREEN + "The available roles are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_roles()))
    elif command == "add_credentials":
        role = input(bcolors.OKBLUE + "role: " + bcolors.ENDC).strip()
        label = input(bcolors.OKBLUE + "label: " + bcolors.ENDC).strip()
        conn_type = input(bcolors.OKBLUE + "What's type of login? [ssh, winrm]: " + bcolors.ENDC).strip()
        username = input(bcolors.OKBLUE + "credential username: " + bcolors.ENDC).strip()
        typ = input(bcolors.OKBLUE + "type [ssh_key_file(S)/password(P)]: " + bcolors.ENDC).strip()
        if typ == "ssh_key_file" or typ.lower() == 's':
            
            onlyfiles = [f for f in listdir('src/keys') if isfile(join('src/keys', f)) and f.endswith(".pem")]
            if len(onlyfiles) > 0:
                print(bcolors.OKGREEN + "The available ssh private key files are: " + bcolors.ENDC)
                print('\n'.join(onlyfiles), file=sys.stdout)
            else:
                print(bcolors.FAIL + "There are no pem files in cmd_exec/src/keys. Please add a ssh private key pem file." + bcolors.ENDC)

            ssh_key_file_name = input(bcolors.OKBLUE + "ssh key filename: " + bcolors.ENDC).strip()
            vapi.add_credentials(role=role, label=label, username=username, typ=typ, ssh_key_file_name='src/keys/'+ssh_key_file_name, conn_type=conn_type)
            print("Added credentials: " + label + " for role: " + role)

        elif typ == "password" or typ.lower() == 'p':
            password = getpass(bcolors.OKBLUE + "password: " + bcolors.ENDC)
            vapi.add_credentials(role=role, label=label, username=username, typ=typ, ssh_key_file_name=None, password=password, conn_type=conn_type)
        print("Added credentials: ", label, file=sys.stdout)
        sys.stdout.flush()
    elif command == "delete_credentials":
        print(bcolors.OKGREEN + "The available roles are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_roles()))
        role = input(bcolors.OKBLUE + "Which role?: " + bcolors.ENDC).strip()
        print(bcolors.OKGREEN + "The available credentials labels for: " + role + bcolors.ENDC)
        print('\n'.join(vapi.list_credentials(role)))
        label = input(bcolors.OKBLUE + "which credentials to delete?: " + bcolors.ENDC).strip()
        vapi.delete_credentials(role, label)
        print("Deleted latest version of credentials: ", label, file=sys.stdout)
        sys.stdout.flush()
    elif command == "list_credentials":
        print(bcolors.OKGREEN + "The available roles are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_roles()))
        role = input(bcolors.OKBLUE + "Which role?: " + bcolors.ENDC).strip()
        print(bcolors.OKGREEN + "The available credentials labels for: " + role + bcolors.ENDC)
        print('\n'.join(vapi.list_credentials(role)))
    elif command == "get_credentials":
        print(bcolors.OKGREEN + "The available roles are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_roles()))
        role = input(bcolors.OKBLUE + "Which role?: " + bcolors.ENDC).strip()
        print(bcolors.OKGREEN + "The available credentials labels for: " + role + bcolors.ENDC)
        print('\n'.join(vapi.list_credentials(role)))
        cred_label = input(bcolors.OKBLUE + "which credentials to get?: " + bcolors.ENDC).strip()
        credentials = vapi.get_credentials(role, cred_label)
        print(bcolors.OKBLUE + "Here's the latest version of: " + cred_label + bcolors.ENDC)
        print(json.dumps(credentials, indent=4))
    
    elif command == "add_ip_addr":
        ips = input(bcolors.OKBLUE + "List the machine IP addresses that share the same credentials: " + bcolors.ENDC).strip()
        ip_addresses = []
        if ',' in ips:
            ip_addresses = ips.split(',')
        else:
            ip_addresses = ips.split()
        #TODO: IP adress sanity check
        roles = vapi.list_roles()
        for role in roles:
            print(bcolors.OKGREEN + "The available credentials labels for: " + role + bcolors.ENDC)
            print('\n'.join(vapi.list_credentials(role)))
        cred_label = input(bcolors.OKBLUE + "Which credentials will they use?: " + bcolors.ENDC).strip()
        #TODO: check sanity of the label, ensure it is valid
        vapi.add_ip_addr(ip_addresses, cred_label)
        print("Added IP addresses: " + ' '.join(ip_addresses))
        print("Associated credentials: " + cred_label)
    
    elif command == "add_inventory":
        filename = input(bcolors.OKBLUE + "file name: " + bcolors.ENDC).strip()
        path_filename = "src/keys/"+filename
        vapi.add_inventory(path_filename)
        print("Added inventory from file: " + path_filename)


    elif command == "delete_ip_addr":
        ips = input(bcolors.OKBLUE + "List the machine IP addresses to delete: " + bcolors.ENDC).strip()
        ip_addresses = []
        if ',' in ips:
            ip_addresses = ips.split(',')
        else:
            ip_addresses = ips.split()
        vapi.delete_ip_addr(ip_addresses)
        print("Deleted IP addresses: " + ' '.join(ip_addresses))
    elif command == "list_ip_addrs":
        print(bcolors.OKGREEN + "IP addresses stored:" + bcolors.ENDC, file=sys.stdout)
        print('\n'.join(vapi.list_ip_addrs()), file=sys.stdout)

    elif command == "get_ip_addr":
        ip_addr = input(bcolors.OKBLUE + "What is the IP address?: " + bcolors.ENDC).strip()
        cred_label = vapi.get_ip_addr(ip_addr)
        print("This IP addresse uses credential: ", cred_label, file=sys.stdout)
        sys.stdout.flush()


    elif command == "create_host_group":
        group_label = input(bcolors.OKBLUE + "What is the group label?: " + bcolors.ENDC).strip()
        hosts = input(bcolors.OKBLUE + "List the hosts to add to this group: " + bcolors.ENDC).strip()
        host_list_tmp = []
        if "," in hosts:
            #comma separated
            host_list_tmp = hosts.split(',')
        else:
            host_list_tmp = hosts.split('\s')
        host_list = [x.strip() for x in host_list_tmp]
        vapi.create_host_group(group_label, host_list)

        print("Created group label: ", group_label, file=sys.stdout)
        sys.stdout.flush()
        if host_list:
            print("Added hosts to the group: ", host_list, file=sys.stdout)
            sys.stdout.flush()

    elif command == "list_host_groups":
        print(bcolors.OKGREEN + "The available host groups are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_host_groups()))

    elif command == "delete_host_group":
        group_label = input(bcolors.OKBLUE + "What is the group label to delete?: " + bcolors.ENDC).strip()
        
        decision = input(bcolors.OKBLUE + "Delete the group: " + group_label + '? (yes/no):' + bcolors.ENDC).strip()
        if decision.lower() == 'yes':
            vapi.delete_host_group(group_label)
            print("Deleted the group: " + group_label, file=sys.stdout)
            sys.stdout.flush()
            
    elif command == "get_host_group":
        group_label = input(bcolors.OKBLUE + "What is the group label?: " + bcolors.ENDC).strip()
        hosts = vapi.get_host_group(group_label)
        print("The group label: ", group_label, " has hosts: ", hosts, file=sys.stdout)
        sys.stdout.flush()

    elif command == "add_hosts_to_group":
        cur_groups = vapi.list_host_groups()
        print(bcolors.OKGREEN + "The available host groups are: " + bcolors.ENDC)
        print('\n'.join(cur_groups))
        group_label = input(bcolors.OKBLUE + "What is the group label?: " + bcolors.ENDC).strip()
        if (group_label not in cur_groups):
            print(bcolors.FAIL + "This group does not exist: " + group_label + bcolors.ENDC, file=sys.stdout)
            sys.stdout.flush()
            continue

        hosts = input(bcolors.OKBLUE + "List the hosts to add to this group: " + bcolors.ENDC).strip()
        new_host_list = vapi.add_hosts_to_group(group_label, hosts)
        print("The group label: ", group_label, " has hosts: ", new_host_list, file=sys.stdout)
        sys.stdout.flush()

    elif command == "delete_hosts_from_group":
        group_label = input(bcolors.OKBLUE + "What is the group label?: " + bcolors.ENDC).strip()
        hosts = input(bcolors.OKBLUE + "List the hosts to add to this group: " + bcolors.ENDC).strip()
        host_list_tmp = []
        if "," in hosts:
            #comma separated
            host_list_tmp = hosts.split(',')
        else:
            host_list_tmp = hosts.split('\s')
        host_list = set([x.strip() for x in host_list_tmp])

        vapi.delete_hosts_from_group(group_label, host_list)
        print("Deleted: " + ' '.join(host_list) + " from group: " + group_label)


    elif command == "add_ip_label":
        ip_addr = input(bcolors.OKBLUE + "What is the IP address?: " + bcolors.ENDC).strip()
        label = input(bcolors.OKBLUE + "What is the label for this IP address?: " + bcolors.ENDC).strip()
        vapi.add_ip_label(ip_addr, label)
        print("Created label: ", label, " for IP address: ", ip_addr, file=sys.stdout)
        sys.stdout.flush()
    elif command == "add_ip_label_regex":
        ip_addr = input(bcolors.OKBLUE + "What is the IP address?: " + bcolors.ENDC).strip()
        label = input(bcolors.OKBLUE + "What is the regex to describe the labels for this IP address?: " + bcolors.ENDC).strip()
        vapi.add_ip_label_regex(ip_addr, label)
        print("Created label regex: ", label, " for IP address: ", ip_addr, file=sys.stdout)
        sys.stdout.flush()
    elif command == "delete_ip_label":
        label = input(bcolors.OKBLUE + "What is the label to be deleted?: " + bcolors.ENDC).strip()
        vapi.delete_ip_label(label)
        print("Deleted the label: " + label + '. The IP address is not deleted', file=sys.stdout)
        sys.stdout.flush()
    elif command == "get_ip_label":
        print(bcolors.OKGREEN + "The available IP labels are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_ip_labels()))
        label = input(bcolors.OKBLUE + "What is the label?: " + bcolors.ENDC).strip()
        ip_addr = vapi.get_ip_label(label)
        print("The label: ", label, " is pointing to: ", ip_addr, file=sys.stdout)
        sys.stdout.flush()
    elif command == "list_ip_labels":
        print(bcolors.OKGREEN + "The available IP labels are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_ip_labels()))
    elif command == "list_ip_label_regex":
        print(bcolors.OKGREEN + "The available IP labels are: " + bcolors.ENDC)
        print(json.dumps(vapi.list_ip_label_regex(), indent=4))
    elif command == "delete_ip_label_regex":
        label = input(bcolors.OKBLUE + "What is the label regex to be deleted?: " + bcolors.ENDC).strip()
        vapi.delete_ip_label_regex(label)
        print("Deleted the label regex: " + label + '. The IP address is not deleted', file=sys.stdout)
        sys.stdout.flush()
        print(bcolors.OKGREEN + "The available IP labels are: " + bcolors.ENDC)
        print(json.dumps(vapi.list_ip_label_regex(), indent=4))
    elif command == "add_url_label":
        url = input(bcolors.OKBLUE + "What is the URL?: " + bcolors.ENDC).strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            print(bcolors.FAIL + "Bad URL. Needs to start with http:// or https://" + bcolors.ENDC)
        else:
            label = input(bcolors.OKBLUE + "What is the label for this URL?: " + bcolors.ENDC).strip()
            vapi.add_url_label(url, label)
            print("Created label: ", label, " for URL: ", url, file=sys.stdout)
            sys.stdout.flush()
    elif command == "delete_url_label":
        label = input(bcolors.OKBLUE + "What is the label to be deleted?: " + bcolors.ENDC).strip()
        vapi.delete_url_label(label)
        print("Deleted the label: " + label, file=sys.stdout)
        sys.stdout.flush()
    elif command == "get_url_label":
        print(bcolors.OKGREEN + "The available URL labels are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_url_labels()))
        label = input(bcolors.OKBLUE + "What is the label?: " + bcolors.ENDC).strip()
        url = vapi.get_url_label(label)
        print("The label: ", label, " is pointing to: ", url, file=sys.stdout)
        sys.stdout.flush()
    elif command == "list_url_labels":
        print(bcolors.OKGREEN + "The available URL labels are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_url_labels()))

    elif command == "add_user":
        uname = input(bcolors.OKBLUE + "User email?: " + bcolors.ENDC).strip()
        print(bcolors.OKGREEN + "The available roles are: " + bcolors.ENDC)
        print('\n'.join(vapi.list_roles()))
        role = input(bcolors.OKBLUE + "Role to assign to the user?: " + bcolors.ENDC).strip()
        vapi.add_user(uname, role)
        print("Added user: " + uname + " to role: " + role, file=sys.stdout)
        sys.stdout.flush()
    elif command == "delete_user":
        uname = input(bcolors.OKBLUE + "User email to delete?: " + bcolors.ENDC).strip()
        vapi.delete_user(uname)
        print("Deleted user: " + uname, file=sys.stdout)
        sys.stdout.flush()
    elif command == "list_users":
        users = vapi.list_users()
        print(bcolors.OKGREEN + "Current users:" + bcolors.ENDC, file=sys.stdout)
        print('\n'.join(users), file=sys.stdout)
        sys.stdout.flush()

    elif command == "get_user":
        uname = input(bcolors.OKBLUE + "User email?: " + bcolors.ENDC).strip()
        resp = vapi.get_user(uname)
        print("User details: ", json.dumps(resp, indent=4), file=sys.stdout)
        sys.stdout.flush()
    else:
        print("Unknown command: ", command, file=sys.stdout)
        sys.stdout.flush()



    





