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
