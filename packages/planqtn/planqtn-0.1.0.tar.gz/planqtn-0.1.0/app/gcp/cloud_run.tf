# Cloud Run job for PlanqTN Jobs
resource "google_cloud_run_v2_job" "planqtn_jobs" {
  name     = "planqtn-jobs"
  location = var.region

  template {
    template {
      service_account = google_service_account.cloud_run_svc.email
      containers {
        image = var.jobs_image
        env {
          name  = "SUPABASE_URL"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.supabase_url.secret_id
              version = "latest"
            }
          }
        }
        env {
          name  = "SUPABASE_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.supabase_service_key.secret_id
              version = "latest"
            }
          }
        }
      }
      max_retries = 0
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run service for job monitoring
resource "google_cloud_run_v2_service" "planqtn_monitor" {
  name     = "planqtn-monitor"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_svc.email
    containers {
      image = var.jobs_image
      args  = ["/app/planqtn_jobs/cloud_run_monitor_service.py"]
      env {
        name  = "SUPABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_url.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "SUPABASE_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_service_key.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run service for API
resource "google_cloud_run_v2_service" "planqtn_api" {
  name     = "planqtn-api"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_svc.email
    containers {
      image = var.api_image
      env {
        name  = "API_IMAGE"
        value = var.api_image
      }    
    }  
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run service for UI
resource "google_cloud_run_v2_service" "planqtn_ui" {
  name     = "planqtn"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_svc.email
    containers {
      image = var.ui_image
      env {
        name  = "VITE_ENV"
        value = var.ui_mode
      }
      env {
        name  = "VITE_TASK_STORE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_url.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "VITE_TASK_STORE_ANON_KEY"
        value = var.supabase_anon_key
      }
      env { 
        name  = "VITE_UI_IMAGE"
        value = var.ui_image
      }
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Allow unauthenticated invocation of the UI service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.planqtn_ui.location
  service  = google_cloud_run_v2_service.planqtn_ui.name
  role     = "roles/run.invoker"
  member   = "allUsers"
} 
