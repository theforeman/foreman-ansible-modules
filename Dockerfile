# To build image:
#
#     % docker build --tag fam:latest .
#
# To run an existing playbook simply specify the path. Override any variables necessary using the
# --extra-vars option.
#
#     % docker run -it --rm \
#          fam:latest \
#              --extra-vars "foreman_server_url=https://192.168.122.3" \
#              /foreman-ansible-modules/test/test_playbooks/organization.yml
#
# To run a custom playbook use the --volume option to mount it in. If the playbook references
# other resources it needs to be mounted relative to those files.
#
#     % docker run -it --rm \
#          --volume `pwd`/myorg.yml:/foreman-ansible-modules/test/test_playbooks/myorg.yml \
#          fam:latest \
#              --extra-vars "foreman_server_url=https://192.168.122.3" \
#              /foreman-ansible-modules/test/test_playbooks/myorg.yml


FROM fedora

RUN dnf -y update && dnf install -y \
        git \
        python-pip

RUN set -x \
        && git clone https://github.com/theforeman/foreman-ansible-modules.git \
        && cd foreman-ansible-modules \
        && make test-setup

WORKDIR /foreman-ansible-modules
ENTRYPOINT ["ansible-playbook"]
