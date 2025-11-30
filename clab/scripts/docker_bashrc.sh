# shellcheck disable=SC2148

# This file is mounted into the network-automation docker container as ~/.bashrc

alias a="ansible-playbook play.yml"
alias ai="ansible-playbook play.yml -t interactive -l"
alias c="scripts/console.py"
alias dpl="ansible-playbook play.yml -t deploy-prefix-lists -l"
alias ii="ansible-playbook play.yml -t import-inventory"
alias ui="ansible-playbook play.yml -t update-inventory"

function ipl() {
    if [ -z "$1" ]
    then
        echo "Please specify a comma separated list of AS-SETs!"
        return
    fi
    ansible-playbook play.yml -t import-prefix-lists -e assets="$1"
}

echo "Available aliases:"
echo ""
echo "a = Run Ansible"
echo "a -l r1-lab1-de -t build"
echo ""
echo "ai = Run Ansible interactive config deploy"
echo "ai r1-lab1-de,r2-lab1-de"
echo ""
echo "Update prefix list in Git for specific AS-SETs"
echo "ipl RIPE::AS-KROOT,RIPE::AS15547:AS-NETPLUS"
echo ""
echo "Deploy prefix lists"
echo "dpl r1-lab1-de,r2-lab1-de"
echo ""
echo "ii = Trigger an Iridium import of inventory data from NetBox to Git, and git pull the data"
echo "ui = Git pull the latest inventory data"
echo ""
echo "c = Connect to console"
echo "c -h r1-lab1-de --ib"
echo ""
