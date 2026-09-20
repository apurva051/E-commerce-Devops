resource "aws_security_group" "k3s_worker" {
  name        = "k3s-worker-sg"
  description = "Firewall rules for k3s worker"
  vpc_id      = aws_vpc.ecommerce.id

  ingress {
    description = "Allow SSH from specific IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "ecommerce-k3s-worker-sg"
  }
}

resource "aws_instance" "k3s_worker" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"
  key_name      = "apurva-key"

  subnet_id = aws_subnet.public.id

  vpc_security_group_ids = [
    aws_security_group.k3s_worker.id
  ]

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  metadata_options {
    http_tokens = "required"
  }

  depends_on = [
    aws_route_table_association.public
  ]

  tags = {
    Name = "ecommerce-k3s-worker"
  }
}

