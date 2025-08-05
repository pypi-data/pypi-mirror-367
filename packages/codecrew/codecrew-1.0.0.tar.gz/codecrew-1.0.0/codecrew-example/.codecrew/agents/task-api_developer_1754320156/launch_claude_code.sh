#!/bin/bash
# Claude Code Launcher for Developer
# Agent ID: task-api_developer_1754320156

echo "🚀 Starting Claude Code session for Developer"
echo "Agent ID: task-api_developer_1754320156"
echo "Task: Implement core functionality from specification"
echo "Workspace: /Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156"
echo "Project: /Users/derekvitrano/Developer/CodeCrew/codecrew-example"
echo ""

# Change to project directory
cd "/Users/derekvitrano/Developer/CodeCrew/codecrew-example"

# Display briefing information
echo "📋 AGENT BRIEFING"
echo "=================="
echo "Role: Developer"
echo "Responsibility: Implement core functionality from specification"

echo ""
echo "📁 Important Files:"
echo "- Briefing: /Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156/briefings/role_briefing.md"
echo "- Status: /Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156/status.json"
echo "- Progress: /Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156/progress/current.md"
echo "- Blockers: /Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156/blockers.md"
echo ""
echo "🔗 GitHub Commands:"
echo "- gh issue list --assignee @me  # Your assigned issues"
echo "- gh pr list --author @me       # Your PRs"
echo "- gh repo view                  # Repository info"
echo ""
echo "⚡ Quick Start:"
echo "1. Read your briefing file"
echo "2. Check assigned GitHub issues"
echo "3. Update your status in status.json"
echo "4. Begin work following GitHub workflow"
echo ""

# Launch Claude Code
echo "Starting Claude Code..."
claude-code

# Update last access time
echo "{\"last_access\": \"2025-08-04T10:09:16.831686\", \"session_type\": \"claude_code\"}" > "/Users/derekvitrano/Developer/CodeCrew/codecrew-example/.codecrew/agents/task-api_developer_1754320156/last_session.json"
