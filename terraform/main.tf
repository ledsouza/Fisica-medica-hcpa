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

variable "aws_region_value" {
  description = "The AWS region to deploy to"
  type        = string
}

variable "access_key_value" {
    description = "The AWS access key"
    type        = string
}

variable "secret_access_key_value" {
    description = "The AWS secret access key"
    type        = string
}

variable "mongodb_acess_key_value" {
    description = "The MongoDB access key"
    type        = string
}

resource "google_secret_manager_secret" "access_key" {
  secret_id = "access_key_id"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "access_key" {
  secret      = google_secret_manager_secret.access_key.id
  secret_data = var.access_key_value
}

resource "google_secret_manager_secret" "secret_access_key" {
  secret_id = "secret_access_key_id"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "secret_access_key" {
  secret      = google_secret_manager_secret.secret_access_key.id
  secret_data = var.secret_access_key_value
}

resource "google_secret_manager_secret" "default_region" {
  secret_id = "default_region_id"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "default_region" {
  secret      = google_secret_manager_secret.default_region.id
  secret_data = var.aws_region_value
}

resource "google_secret_manager_secret" "mongodb_access_key {
  secret_id = "mongodb_access_key_id"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "mongodb_access_key" {
  secret      = google_secret_manager_secret.mongodb_access_key.id
  secret_data = var.mongodb_acess_key_value
}

resource "google_service_account" "account" {
  account_id = "fisica-medica-hcpa"
  display_name = "Service account for Cloud Run"
}

resource "google_secret_manager_secret_iam_member" "access_key" {
  secret_id = google_secret_manager_secret.access_key.id
  role      = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.account.email}"
  depends_on = [google_secret_manager_secret.access_key]
}

resource "google_secret_manager_secret_iam_member" "secret_access_key" {
  secret_id = google_secret_manager_secret.secret_access_key.id
  role      = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.account.email}"
  depends_on = [google_secret_manager_secret.secret_access_key]
}

resource "google_secret_manager_secret_iam_member" "default_region" {
  secret_id = google_secret_manager_secret.default_region.id
  role      = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.account.email}"
  depends_on = [google_secret_manager_secret.default_region]
}

resource "google_secret_manager_secret_iam_member" "mongodb_access_key" {
  secret_id = google_secret_manager_secret.mongodb_access_key.id
  role      = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.account.email}"
  depends_on = [google_secret_manager_secret.mongodb_access_key]
}

resource "google_cloud_run_v2_service" "default" {
  name     = "mnmanagement"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/fisica-medica-hcpa/fisica-medica-repo/mnmanagement:1.2.0"

      ports {
        container_port = 8501
      }

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
      env {
        name = "MONGODB_ACCESS_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.mongodb_access_key.secret_id
            version = "latest"
          }
        }
      }
    service_account = google_service_account.account.email
    }
  depends_on = [google_secret_manager_secret_version.access_key, google_secret_manager_secret_version.secret_access_key, google_secret_manager_secret_version.default_region, google_secret_manager_secret_version.mongodb_access_key]
  }
}

resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}