# Variables for AIDevOS Terraform configuration

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "kubernetes_config_path" {
  description = "Path to Kubernetes config file"
  type        = string
  default     = "~/.kube/config"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# EKS Configuration
variable "eks_instance_types" {
  description = "EC2 instance types for EKS node groups"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_node_group_size" {
  description = "Size configuration for EKS node groups"
  type = object({
    min_size     = number
    max_size     = number
    desired_size = number
  })
  default = {
    min_size     = 2
    max_size     = 5
    desired_size = 3
  }
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS instance (in GB)"
  type        = number
  default     = 20
}

variable "db_master_username" {
  description = "Master username for RDS instance"
  type        = string
  default     = "aidevos"
  sensitive   = true
}

# Redis Configuration
variable "redis_instance_type" {
  description = "ElastiCache Redis instance type"
  type        = string
  default     = "cache.t3.small"
}

# S3 Bucket Configuration
variable "s3_buckets" {
  description = "Configuration for S3 buckets"
  type = list(object({
    name        = string
    acl         = string
    versioning  = bool
  }))
  default = [
    {
      name        = "aidevos-data"
      acl         = "private"
      versioning  = true
    },
    {
      name        = "aidevos-logs"
      acl         = "private"
      versioning  = false
    },
    {
      name        = "aidevos-backups"
      acl         = "private"
      versioning  = true
    }
  ]
}

# Environment-specific configuration
variable "env_config" {
  description = "Environment-specific configuration"
  type = map(object({
    eks_instance_types  = list(string)
    db_instance_class   = string
    db_allocated_storage = number
    redis_instance_type = string
  }))
  default = {
    dev = {
      eks_instance_types  = ["t3.medium"]
      db_instance_class   = "db.t3.small"
      db_allocated_storage = 20
      redis_instance_type = "cache.t3.small"
    },
    staging = {
      eks_instance_types  = ["t3.large"]
      db_instance_class   = "db.t3.medium"
      db_allocated_storage = 50
      redis_instance_type = "cache.t3.medium"
    },
    production = {
      eks_instance_types  = ["m5.large", "m5.xlarge"]
      db_instance_class   = "db.m5.large"
      db_allocated_storage = 100
      redis_instance_type = "cache.m5.large"
    }
  }
}