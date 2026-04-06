# Cloud-computing

2026-01 학기 클라우드컴퓨팅 수업을 위한 repository.

# IaC(Infrastructure as Code) 구축

## Vagrant

Vagrant란 가상 머신 개발 환경을 코드로 정의하고 재현하는 도구로, 개발사인 HashiCorp에선 "가상 머신의 생명주기를 관리하는 CLI 유틸리티"로 설명한다.

### Installation

``` bash
# 최신 버전(2.4.9) 기준 설치방법
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vagrant
```

### Create Vagrantfile

노드명, 네트워크(NAT + Host-only, Port forwarding), VM 프로바이더 및 하드웨어 자원 설정, Vagrant SSH 설정 등을 명시

### Exec Vagrant CLI

``` bash
# 노드 생성 및 설정
vagrant up

# 생성된 노드 정보 확인
vagrant status

# 노드 접속
vagrant ssh ${node_name}

# 생성된 노드 제거
vagrant destroy
```

### Trouble Shooting

노드 내에서 다른 노드로의 ssh 접속 시, `permission denied` 발생

host에서 `id_ed25519 -> cluster_key`를 생성하여 vagrant 공용 키로 사용

Vagrantfile을 수정하여 `/home/vagrant/.ssh` 디렉터리 생성 후, public, private, authorized key 삽입 후 권한 설정

`/home/vagrant/.ssh/authorized_key`를 `sudo tee`로 덮어씌우면 `vagrant ssh`의 ssh 정보가 사라져 `Permission denined` 발생

append 방식으로 추가만 해야 `vagrant ssh`, `ssh node1/node2/node3` 가능
