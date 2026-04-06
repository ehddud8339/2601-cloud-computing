# 2025126653 이동영 - Lab 02 (IaC)
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  
  # node 갯수와 ip, ssh 형식 지정
  node_count = 5
  ip_base = "192.168.56."
  ip_offset = 10

  # 생성할 node의 ip와 명칭을 정의
  hosts_entries = (1..node_count).map do |i|
    "#{ip_base}#{ip_offset + i} node#{i}"
  end.join("\n")

  # 반복문으로 전체 노드를 생성
  (1..node_count).each do |iter|
    # node 이름, ip 정의
    node_name = "node#{iter}"
    node_ip = "#{ip_base}#{ip_offset + iter}"

    # node 설정
    config.vm.define node_name do |node|
      # vm 내 노드 명칭 및 host-only 설정
      node.vm.hostname = node_name
      node.vm.network "private_network", ip: node_ip

      # vb 하드웨어 설정
      node.vm.provider "virtualbox" do |vb|
        vb.name = node_name
        vb.memory = 4096
        vb.cpus = 2
      end

      # vm 생성 이후 자동으로 실행될 shell 명령
      node.vm.provision "shell", inline: <<-SHELL
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y curl wget git net-tools vim

        sudo sed -i '/node[0-9]\\+/d' /etc/hosts

        cat <<EOF | sudo tee -a /etc/hosts >/dev/null
#{hosts_entries}
EOF
      SHELL
    end
  end
end
