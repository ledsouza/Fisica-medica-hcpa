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

resource "google_cloud_run_v2_service" "env_variable_secret" {
  name     = "cloudrun-srv-env-var-secret"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      env {
        name = "MY_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.default.secret_id
            version = "latest"
          }
        }
      }
    }
    service_account = google_service_account.default.email
  }
  depends_on = [google_secret_manager_secret_version.default]
}

