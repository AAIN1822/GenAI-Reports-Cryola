locals {
  # Project name (must match bootstrap/locals.tf)
  project_name = "fsdu"         # Name of the project
  owner        = "fsdu"         # Owner of the project
  region       = "eastus2"      # Default Azure region

  tags = {
    Project = local.project_name # Tag for project name
    Owner   = local.owner        # Tag for owner
  }
}

