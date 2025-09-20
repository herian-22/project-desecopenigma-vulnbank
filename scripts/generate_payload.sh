#!/bin/bash
# scripts/generate_payload.sh

# This script reads variables directly from the environment
# set by the GitHub Actions workflow.

# Create the JSON payload using a heredoc. This is much cleaner
# than trying to build it with jq and command-line arguments.
cat <<EOF
{
  "username": "DevSecOps Bot",
  "avatar_url": "https://i.imgur.com/fJc1mOa.png",
  "embeds": [
    {
      "title": "DevSecOps Pipeline Status: $PIPELINE_STATUS",
      "url": "$RUN_URL",
      "color": $PIPELINE_COLOR,
      "fields": [
        {
          "name": "Repository",
          "value": "$REPO_NAME",
          "inline": true
        },
        {
          "name": "Triggered by",
          "value": "$ACTOR",
          "inline": true
        },
        {
          "name": "Commit",
          "value": "\`$COMMIT_SHA\`"
        },
        {
          "name": "🛡️ Secret Scan (Gitleaks)",
          "value": "$SECRET_SUMMARY"
        },
        {
          "name": "🔬 SAST (Bandit)",
          "value": "$SAST_SUMMARY"
        },
        {
          "name": "📦 Container Scan (Trivy)",
          "value": "$CONTAINER_SUMMARY"
        },
        {
          "name": "⚙️ Misconfig Scan (Trivy)",
          "value": "$MISCONFIG_SUMMARY"
        },
        {
          "name": "🌐 DAST (OWASP ZAP)",
          "value": "$DAST_SUMMARY"
        }
      ],
      "footer": {
        "text": "Security scan results",
        "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
      },
      "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%S.000Z')"
    }
  ]
}
EOF

