# Runtime Kernels

## Free PlanqTN Cloud Runtime

!!! Info

    Running this service is a highly experimental effort, and is subject to change.

The cloud runtime requires no setup on the user's end, and is intended for
educational, small-scale research use cases and experimentation. It is using
Google Cloud Run to spin up weight enumerator calculation jobs that are subject
to the following limitations:

-   Memory: 1 GB RAM
-   Execution time: 5 minutes

Network creation is executed through API calls to the Python framework using a
Cloud Run Service, and is similarly subject to constraints:

-   Memory: 512 MB RAM
-   Execution time: 5 minutes

When the user runs into any of these limits, the job or API call will fail.

The current quota system is very simple:

-   Every user gets 500 "Cloud minutes" per month.
-   Each job execution costs 5 minutes (independent of the actual runtime
    length).
-   Each API call costs 0.5 minutes.

<center>
<img src="/docs/fig/quotas_modal.png" width="50%">
</center>

Please reach out to planqtn@planqtn.com if you need to raise your quota, we'd
love to hear your use case and thoughts on this.

## Local Runtime

Using the same public planqtn.com UI, it is possible to switch to a local
runtime.

System requirements:

-   Docker (Desktop)
-   NodeJS 22+
-   minimum 12 GB Hard disk
-   minimum 8 GB RAM

Installation steps:

1. Setup `htn` the local tool for PlanqTN (the name is `h` for Planck's constant
   and TN for tensor network)

```
pip install planqtn-cli
```

2. Run the kernel

```
htn kernel start
```

This should spin up via the Docker container a Kubernetes cluster that will run
and monitor the workloads for the jobs and the Supabase installation.

```
Checking Docker installation...
Running in dev mode, skipping directory/config setup, using existing files in repo
Job image: planqtn/planqtn_jobs:v0.1.13
API image: planqtn/planqtn_api:v0.1.13
Checking Supabase status...
Starting Supabase in working directory: ~/.planqtn/
Running database migrations...
Checking Docker network...
Setting up k3d cluster...
Setting up k8sproxy...
Testing k8sproxy...
Setting up job-monitor-rbac...
Setting up API service...
PlanqTN kernel setup completed successfully!
```

Now, on the PlanqTN Tensor Studio, use the
[Canvas menu](./ui-controls.md/#canvas-menu) to switch to a local runtime.

If `htn kernel status` command should provide something similar:

```
$ htn kernel status
Supabase: Running
k3d cluster: Running
k8sproxy: Running
API service: Running

Connection details:
{
  "API_URL": "http://127.0.0.1:54321",
  "ANON_KEY": "your anon key"
}
```

Copy-paste the JSON part, i.e. the lines below ``Connection details:''.

## Self-hosted PlanqTN Cloud

As PlanqTN is fully open source, it is also possible to set up your own cloud
instance, however, this is beyond the scope of the end-user documentation. For
details, please check out the personal cloud setup details in
[DEVELOPMENT.md](https://github.com/planqtn/planqtn/blob/main/DEVELOPMENT.md#personal-cloud-setup).
