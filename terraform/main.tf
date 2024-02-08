terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  project = "fisica-medica-hcpa"
}

resource "google_service_account" "cloudrun_service_identity" {
  account_id = "fisica-medica-hcpa"
}

resource "google_secret_manager_secret" "default" {
  secret_id = "s3-fisica-medica-hcpa"
}

resource "google_secret_manager_secret_iam_member" "default" {
  secret_id = google_secret_manager_secret.default.id
  role      = "roles/secretmanager.secretAccessor"
  # Grant the new deployed service account access to this secret.
  member     = "serviceAccount:${google_service_account.default.email}"
  depends_on = [google_secret_manager_secret.default]
}

resource "google_cloud_run_v2_service" "mounted_secret" {
  name     = "cloudrun-srv-mounted-secret"
  location = "us-central1"

  template {
    volumes {
      name = "secrets-volume"
      secret {
        secret = google_secret_manager_secret.default.secret_id
        items {
          version = "latest"
          path    = "my-secret"
          mode    = 0 # use default 0444
        }
      }
    }
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      volume_mounts {
        name       = "secrets-volume"
        mount_path = "/secrets"
      }
    }
    service_account = google_service_account.default.email
  }
  depends_on = [google_secret_manager_secret_version.default]
}

