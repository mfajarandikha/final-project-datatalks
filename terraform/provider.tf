terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = file("../include/creds.json")
  project     = var.project_id
  region      = "us-central1"
  zone        = "us-central1-a"
}
