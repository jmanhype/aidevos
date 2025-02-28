# AIDevOS Infrastructure as Code with Terraform
# This is the main Terraform configuration for the AIDevOS infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm" 
      version = "~> 2.0"
    }
  }
  
  # Configure backend for state storage - in a real environment,
  # this would use a remote backend like S3
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "AIDevOS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubernetes_config_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubernetes_config_path
  }
}

# Networking
module "vpc" {
  source = "./modules/vpc"
  
  environment     = var.environment
  vpc_cidr        = var.vpc_cidr
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
}

# EKS Cluster for running the AIDevOS system
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "aidevos-${var.environment}"
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  instance_types  = var.eks_instance_types
  node_group_size = var.eks_node_group_size
  
  depends_on = [module.vpc]
}

# Database (RDS PostgreSQL)
module "database" {
  source = "./modules/database"
  
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  instance_class     = var.db_instance_class
  allocated_storage  = var.db_allocated_storage
  database_name      = "aidevos"
  master_username    = var.db_master_username
  skip_final_snapshot = var.environment != "production"
  
  depends_on = [module.vpc]
}

# Redis for caching and pub/sub
module "redis" {
  source = "./modules/redis"
  
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  instance_type  = var.redis_instance_type
  
  depends_on = [module.vpc]
}

# S3 buckets for storage
module "storage" {
  source = "./modules/storage"
  
  environment = var.environment
  buckets     = var.s3_buckets
}

# Monitoring and logging infrastructure
module "monitoring" {
  source = "./modules/monitoring"
  
  environment       = var.environment
  eks_cluster_name  = module.eks.cluster_name
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  
  depends_on = [module.eks]
}

# Helm charts for deploying application components
module "applications" {
  source = "./modules/applications"
  
  environment       = var.environment
  eks_cluster_name  = module.eks.cluster_name
  
  depends_on = [
    module.eks,
    module.database,
    module.redis,
    module.monitoring
  ]
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "The endpoint for the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "database_endpoint" {
  description = "The endpoint for the database"
  value       = module.database.endpoint
}

output "redis_endpoint" {
  description = "The endpoint for Redis"
  value       = module.redis.endpoint
}

output "monitoring_dashboard_url" {
  description = "URL for the monitoring dashboard"
  value       = module.monitoring.dashboard_url
}