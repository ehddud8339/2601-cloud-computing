# 2025126653 이동영 - Lab 02 (IaC)

# vagrant ssh로 접속할 경우, user는 vagrant로 설정
# 미리 만들어 둔 ed25519 public, private key를 각 노드에 배포
# vagrant user가 접근할 수 있도록 하여 다른 노드로의 ssh 접근이 가능하도록 한다.
cluster_private_key = File.read(File.expand_path("cluster_key", __dir__)).strip
cluster_public_key = File.read(File.expand_path("cluster_key.pub", __dir__)).strip

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  
  # node 갯수와 ip, ssh 형식 지정
  node_count = 3
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
        sudo apt install -y git net-tools vim openssh-client openssh-server
        
        sudo install -d -m 700 -o vagrant -g vagrant /home/vagrant/.ssh

        cat <<'EOF' | sudo tee /home/vagrant/.ssh/id_ed25519 >/dev/null
#{cluster_private_key}
EOF
        cat <<'EOF' | sudo tee /home/vagrant/.ssh/id_ed25519.pub >/dev/null
#{cluster_public_key}
EOF
        echo '#{cluster_public_key}' | sudo tee -a /home/vagrant/.ssh/authorized_keys >/dev/null

        cat <<'EOF' | sudo tee /home/vagrant/.ssh/config >/dev/null
Host node*
  User vagrant
  IdentityFile /home/vagrant/.ssh/id_ed25519
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
EOF

        sudo chown -R vagrant:vagrant /home/vagrant/.ssh
        sudo chmod 700 /home/vagrant/.ssh
        sudo chmod 600 /home/vagrant/.ssh/id_ed25519
        sudo chmod 644 /home/vagrant/.ssh/id_ed25519.pub
        sudo chmod 600 /home/vagrant/.ssh/authorized_keys
        sudo chmod 600 /home/vagrant/.ssh/config

        sudo sed -i '/node[0-9]\\+/d' /etc/hosts
        cat <<'EOF' | sudo tee -a /etc/hosts >/dev/null
#{hosts_entries}
EOF
      SHELL
    end
  end
end
