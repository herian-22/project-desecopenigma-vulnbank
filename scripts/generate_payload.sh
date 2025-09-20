#!/bin/bash

# Script ini menggunakan jq untuk membuat payload JSON secara aman,
# menghindari error akibat karakter khusus di dalam variabel.

# Pastikan jq terinstal
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, attempting to install..." >&2
    sudo apt-get update && sudo apt-get install -y jq
fi

# Gunakan jq untuk membuat JSON.
# --arg flag akan menangani escaping secara otomatis.
jq -n \
  --arg status "$PIPELINE_STATUS" \
  --arg color "$PIPELINE_COLOR" \
  --arg repo "$REPO_NAME" \
  --arg actor "$ACTOR" \
  --arg commit_sha "$COMMIT_SHA" \
  --arg run_url "$RUN_URL" \
  --arg secret_sum "$SECRET_SUMMARY" \
  --arg sast_sum "$SAST_SUMMARY" \
  --arg container_sum "$CONTAINER_SUMMARY" \
  --arg misconfig_sum "$MISCONFIG_SUMMARY" \
  --arg dast_sum "$DAST_SUMMARY" \
  '{
    "username": "DevSecOps Bot",
    "embeds": [{
      "title": ("Laporan Pipeline: \($status)"),
      "url": $run_url,
      "color": ($color | tonumber),
      "fields": [
        {"name": "Repository", "value": $repo, "inline": true},
        {"name": "Pemicu", "value": $actor, "inline": true},
        {"name": "Commit", "value": ("`" + $commit_sha[0:7] + "`")},
        {"name": "🛡️ Secret Scan", "value": $secret_sum},
        {"name": "🔬 SAST", "value": $sast_sum},
        {"name": "📦 Container Scan", "value": $container_sum},
        {"name": "⚙️ Misconfig Scan", "value": $misconfig_sum},
        {"name": "🌐 DAST", "value": $dast_sum}
      ]
    }]
  }'