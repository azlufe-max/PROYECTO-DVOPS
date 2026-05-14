terraform {
  required_version = ">= 1.0.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# 1. Creamos la red privada para que los contenedores se hablen entre sí
resource "docker_network" "checkin_network" {
  name = "checkin_network"
}

# 2. Descargamos la imagen oficial de PostgreSQL
resource "docker_image" "postgres_image" {
  name = "postgres:15-alpine" # Usamos alpine por ser más ligera y rápida de descargar
}

# 3. Configuramos el contenedor de la Base de Datos
resource "docker_container" "postgres_db" {
  name  = "guest_pass_db"
  image = docker_image.postgres_image.image_id
  
  networks_advanced {
    name = docker_network.checkin_network.name
  }

  env = [
    "POSTGRES_DB=${var.db_name}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}"
  ]

  ports {
    internal = 5432
    external = 5432
  }

  restart = "unless-stopped"
}
# 4. Construir la imagen del Backend desde el Dockerfile
resource "docker_image" "backend_image" {
  name = "guest_pass_backend:latest"
  build {
    context = "../backend" # Ruta a la carpeta donde está tu Dockerfile
  }
}

# 5. Levantar el contenedor del Backend
resource "docker_container" "backend_container" {
  name  = "guest_pass_backend"
  image = docker_image.backend_image.image_id
  
  networks_advanced {
    name = docker_network.checkin_network.name
  }

  ports {
    internal = 8000
    external = 8000
  }

  # Esto asegura que el backend espere a que la DB esté lista
  depends_on = [docker_container.postgres_db]

  env = [
    "DATABASE_URL=postgresql://${var.db_user}:${var.db_password}@guest_pass_db:5432/${var.db_name}"
  ]
}
variable "db_user" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_name" {
  type = string
}