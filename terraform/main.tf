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
  region  = "us-central1"
}

resource "google_service_account" "account" {
  account_id = "fisica-medica-hcpa"
}

resource "google_secret_manager_secret" "secret" {
  secret_id = "s3-fisica-medica-hcpa"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "access_key" {
  name = "AWS_ACCESS_KEY_ID"
}

resource "google_secret_manager_secret_version" "access_key" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = "AKIAUJAUJNOCJPEMMPIO"
}

resource "google_secret_manager_secret" "secret_access_key" {
  name = "AWS_SECRET_ACCESS_KEY"
}

resource "google_secret_manager_secret_version" "secret_access_key" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = "1tptqziFKNWboo3ee8HKtBWOF8P3X9uYXYIy8NvM"
}

resource "google_secret_manager_secret" "default_region" {
  name = "AWS_DEFAULT_REGION"
}

resource "google_secret_manager_secret_version" "default_region" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = "us-east-1"
}

resource "google_secret_manager_secret_iam_member" "access" {
  secret_id = google_secret_manager_secret.secret.id
  role      = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.account.email}"
  depends_on = [google_secret_manager_secret.secret]
}

resource "google_cloud_run_v2_service" "default" {
  name     = "mnmanagement"
  location = "us-central1"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/fisica-medica-hcpa/fisica-medica-repo/mnmanagement"
      env {
        name = "AWS_ACCESS_KEY_ID"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.access_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "AWS_SECRET_ACCESS_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.secret_access_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "AWS_DEFAULT_REGION"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.default_region.secret_id
            version = "latest"
          }
        }
      }
    }
    service_account = google_service_account.default.email
  }
  depends_on = [google_secret_manager_secret_version.default]
}
