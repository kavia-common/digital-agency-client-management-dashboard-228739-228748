#!/bin/bash
cd /home/kavia/workspace/code-generation/digital-agency-client-management-dashboard-228739-228748/project_management_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

