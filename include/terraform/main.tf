resource "google_storage_bucket" "source" {
  name          = var.bucket_name_source
  location      = var.region
  storage_class = var.storage_class
  force_destroy = true
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.source.name
  role   = "roles/storage.admin"
  member = "allUsers" # ⚠️ Consider using a service account instead for security
}

resource "google_storage_bucket_object" "upload_csv" {
  name   = basename(var.csv_file_path)
  bucket = google_storage_bucket.source.name
  source = var.csv_file_path
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_table" "table" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.table_id
  project             = var.project_id
  deletion_protection = false

  schema = jsonencode([
    { name = "video_id", type = "STRING", mode = "NULLABLE" },
    { name = "title", type = "STRING", mode = "NULLABLE" },
    { name = "video_url", type = "STRING", mode = "NULLABLE" },
    { name = "published_date", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "views", type = "INTEGER", mode = "NULLABLE" },
    { name = "likes", type = "INTEGER", mode = "NULLABLE" },
    { name = "comments", type = "INTEGER", mode = "NULLABLE" }
  ])

  time_partitioning {
    type  = "DAY"
    field = "published_date"
  }
}
