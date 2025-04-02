variable "bucket_name_source" {
  type        = string
  description = "The name of our bucket"
}

variable "bucket_location" {
  type    = string
  default = "us-east1"
}

variable "project_id" {
  type = string
}

variable "storage_class" {
  type = string
}

variable "folder_path" {
  type        = string
  description = "Path to your folder"
}