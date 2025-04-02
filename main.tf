resource "google_storage_bucket" "source" {
  name          = var.bucket_name_source
  storage_class = var.storage_class
  location      = var.bucket_location
  force_destroy = true
}

resource "google_storage_bucket_iam_member" "member" {
  bucket     = google_storage_bucket.source.name
  role       = "roles/storage.admin"
  member     = "allUsers"
  depends_on = [google_storage_bucket.source]
}

resource "null_resource" "upload_folder_content" {
  depends_on = [google_storage_bucket.source, google_storage_bucket_iam_member.member]
  triggers = {
    file_hashes = jsonencode({
      for fn in fileset(var.folder_path, "**") :
      fn => filesha256("${var.folder_path}/${fn}")
    })
  }

  provisioner "local-exec" {
    command = "gsutil cp -r ${var.folder_path}/* gs://${var.bucket_name_source}/"
  }
}