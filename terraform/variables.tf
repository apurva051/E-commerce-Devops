variable "ssh_allowed_cidr" {
  description = "Public IPv4 address allowed to SSH"
  type        = string
}
variable "http_allowed_cidr" {
  description = "CIDR allowed to access the ecommerce website over HTTP"
  type        = string
}