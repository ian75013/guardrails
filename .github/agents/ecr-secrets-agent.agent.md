---
name: ecr-secrets-agent
description: >
  Agent for resolving ECR image pull failures, stale Docker registry secrets,
  and Kubernetes ImagePullBackOff issues. Covers AWS ECR token rotation (12h),
  k8s pull secret lifecycle, and multi-cluster secret synchronization.
  Use when: pods stuck in ImagePullBackOff, ECR push/pull auth failures,
  secret out-of-sync after cluster reprovisioning, or CI/CD pipeline registry errors.
tools:
  - run_in_terminal
  - read_file
  - replace_string_in_file
  - create_file
  - grep_search
---

# ECR Secrets Agent

## Purpose

Diagnose and resolve all ECR / Docker registry secret issues across local builds,
k3s/k8s clusters, and CI/CD pipelines. Operates with minimal manual intervention.

## Diagnostic Checklist

1. **Identify the failing pod / context**
2. **Check secret age** — ECR tokens expire after 12 hours
3. **Refresh token + recreate secret**
4. **Force pod restart**
5. **Verify rollout**

---

## Standard Fix: ECR Pull Secret Rotation

### Variables to set before running

```bash
ECR_REGISTRY="113301685315.dkr.ecr.eu-west-3.amazonaws.com"
ECR_REGION="eu-west-3"
K8S_NAMESPACE="doctum-trading"
SECRET_NAME="ecr-registry-secret"
```

### Step 1 — Diagnose

```bash
# Check pod status
kubectl -n $K8S_NAMESPACE get pods | grep -E "ImagePull|ErrImage|Pending"

# Inspect the failing pod
kubectl -n $K8S_NAMESPACE describe pod <pod-name> | grep -A10 "Events:"

# Check secret age
kubectl -n $K8S_NAMESPACE get secret $SECRET_NAME -o jsonpath='{.metadata.creationTimestamp}'
```

### Step 2 — Refresh ECR token and recreate secret

```bash
# Ubuntu / macOS (bash/zsh)
TOKEN=$(aws ecr get-login-password --region $ECR_REGION)
kubectl -n $K8S_NAMESPACE delete secret $SECRET_NAME --ignore-not-found
kubectl -n $K8S_NAMESPACE create secret docker-registry $SECRET_NAME \
  --docker-server=$ECR_REGISTRY \
  --docker-username=AWS \
  --docker-password="$TOKEN"
echo "Secret recreated at $(date)"
```

```powershell
# Windows (PowerShell)
$Token = aws ecr get-login-password --region $ECR_REGION
kubectl -n $K8S_NAMESPACE delete secret $SECRET_NAME --ignore-not-found
kubectl -n $K8S_NAMESPACE create secret docker-registry $SECRET_NAME `
  --docker-server=$ECR_REGISTRY `
  --docker-username=AWS `
  --docker-password="$Token"
Write-Host "Secret recreated at $(Get-Date)"
```

### Step 3 — Restart affected pods

```bash
# Delete pods to force immediate re-pull (Deployment recreates them)
kubectl -n $K8S_NAMESPACE delete pod -l app=<app-label> --ignore-not-found

# Or rolling restart (zero-downtime)
kubectl -n $K8S_NAMESPACE rollout restart deployment/<deployment-name>
```

### Step 4 — Verify

```bash
kubectl -n $K8S_NAMESPACE get pods -w
# Wait until STATUS = Running 1/1
```

---

## Full Deploy + Secret Refresh Script (tmux-safe)

Run this inside a named tmux session to protect against SSH disconnection:

```bash
# Start session
tmux new-session -A -s ecr-refresh

# --- inside tmux ---
set -euo pipefail
ECR_REGISTRY="113301685315.dkr.ecr.eu-west-3.amazonaws.com"
ECR_REGION="eu-west-3"
NS="doctum-trading"
SECRET="ecr-registry-secret"
TAG=$(date +%Y-%m-%d)

# 1. ECR login
aws ecr get-login-password --region $ECR_REGION \
  | docker login --username AWS --password-stdin $ECR_REGISTRY

# 2. Build & push (adapt image names)
# docker build -t $ECR_REGISTRY/platform/<service>:$TAG <build-context>
# docker push $ECR_REGISTRY/platform/<service>:$TAG

# 3. Rotate pull secret
TOKEN=$(aws ecr get-login-password --region $ECR_REGION)
kubectl -n $NS delete secret $SECRET --ignore-not-found
kubectl -n $NS create secret docker-registry $SECRET \
  --docker-server=$ECR_REGISTRY \
  --docker-username=AWS \
  --docker-password="$TOKEN"

# 4. Apply manifest
# kubectl apply -f <manifest-path>

# 5. Rollout status
kubectl -n $NS rollout status deployment --timeout=180s

echo "Done at $(date)"
```

---

## Cron / Automated Token Refresh (prevent expiry)

ECR tokens expire every **12 hours**. To automate rotation in-cluster:

### Option A — CronJob in k8s

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ecr-secret-refresh
  namespace: doctum-trading
spec:
  schedule: "0 */11 * * *"   # every 11h to stay ahead of 12h expiry
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: ecr-refresher-sa  # needs ClusterRole to manage secrets
          containers:
          - name: refresh
            image: amazon/aws-cli:latest
            env:
            - name: AWS_DEFAULT_REGION
              value: "eu-west-3"
            command:
            - /bin/sh
            - -c
            - |
              TOKEN=$(aws ecr get-login-password)
              kubectl delete secret ecr-registry-secret -n doctum-trading --ignore-not-found
              kubectl create secret docker-registry ecr-registry-secret \
                -n doctum-trading \
                --docker-server=113301685315.dkr.ecr.eu-west-3.amazonaws.com \
                --docker-username=AWS \
                --docker-password="$TOKEN"
          restartPolicy: OnFailure
```

### Option B — Local cron (workstation)

```bash
# Add to crontab: crontab -e
0 */11 * * * bash /path/to/refresh-ecr-secret.sh >> /var/log/ecr-refresh.log 2>&1
```

---

## Common Root Causes

| Symptom | Root Cause | Fix |
|---|---|---|
| `ImagePullBackOff` after 12h | ECR token expired in k8s secret | Step 2-4 above |
| `ImagePullBackOff` after cluster reprovision | Secret not recreated | Step 2-4 above |
| `401 Unauthorized` on `docker push` | Local docker login stale | `aws ecr get-login-password \| docker login ...` |
| `no basic auth credentials` | Secret missing in namespace | Create secret in correct namespace |
| Secret exists but pods still fail | Secret not referenced in ServiceAccount or pod spec | Patch ServiceAccount: `kubectl patch sa default -n $NS -p '{"imagePullSecrets":[{"name":"ecr-registry-secret"}]}'` |
| Works locally, fails in CI | CI pipeline lacks ECR credentials | Set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` as CI env vars |

---

## ServiceAccount Patch (one-time, persistent)

Avoid specifying `imagePullSecrets` in every Deployment by patching the default ServiceAccount:

```bash
kubectl patch serviceaccount default \
  -n $K8S_NAMESPACE \
  -p '{"imagePullSecrets":[{"name":"ecr-registry-secret"}]}'
```

After this, all pods in the namespace automatically inherit the pull secret.

---

## Rollback

```bash
# Revert to previous image tag
PREV_TAG="2026-04-16"
kubectl -n doctum-trading set image deployment/doctum-trading-rl-agent \
  rl-agent=113301685315.dkr.ecr.eu-west-3.amazonaws.com/platform/doctum-trading-rl-agent:$PREV_TAG
kubectl -n doctum-trading set image deployment/doctum-trading-realtime-api \
  realtime-api=113301685315.dkr.ecr.eu-west-3.amazonaws.com/platform/doctum-trading-realtime-api:$PREV_TAG
kubectl -n doctum-trading set image deployment/doctum-trading-realtime-web \
  realtime-web=113301685315.dkr.ecr.eu-west-3.amazonaws.com/platform/doctum-trading-realtime-web:$PREV_TAG
```
