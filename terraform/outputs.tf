output "k3s_server_public_ip" {
  description = "Public IP address of the k3s server"
  value       = aws_instance.k3s_server.public_ip
}


output "k3s_server_private_ip" {
  description = "Private IP used for communication inside the VPC"
  value       = aws_instance.k3s_server.private_ip
}

output "k3s_server_instance_id" {
  value = aws_instance.k3s_server.id
}