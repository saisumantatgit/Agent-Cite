#!/bin/bash
# Agent-Cite Installer
# Detects your CLI tool and installs the right adapter.

set -e

echo "📑  Agent-Cite Installer"
echo "========================"
echo ""

# Detect CLI tool
if [ -d ".claude" ]; then
    CLI="claude-code"
    echo "Detected: Claude Code"
elif [ -d ".cursor" ]; then
    CLI="cursor"
    echo "Detected: Cursor"
elif [ -f ".aider.conf.yml" ]; then
    CLI="aider"
    echo "Detected: Aider"
elif [ -f "AGENTS.md" ]; then
    CLI="codex"
    echo "Detected: Codex"
else
    CLI="generic"
    echo "No specific CLI detected — installing generic prompts"
fi

echo ""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Copy core prompts
echo "Installing prompts..."
cp -r "$SCRIPT_DIR/prompts" .

# Copy references
echo "Installing references..."
cp -r "$SCRIPT_DIR/references" .

# Copy evidence protocol template
echo "Installing evidence protocol template..."
if [ ! -f "evidence-protocol.yaml" ] && [ ! -f ".cite/evidence-protocol.yaml" ]; then
    cp "$SCRIPT_DIR/templates/evidence-protocol.yaml" .
    echo "  Created evidence-protocol.yaml (customize for your project)"
else
    echo "  Skipped (evidence-protocol.yaml already exists)"
fi

# Install CLI-specific adapter
echo ""
echo "Installing $CLI adapter..."
case $CLI in
    claude-code)
        mkdir -p .claude/commands .claude/agents .claude/skills/{evidence-audit,citation-fix,evidence-report}
        cp "$SCRIPT_DIR/adapters/claude-code/commands/"*.md .claude/commands/
        cp "$SCRIPT_DIR/.claude/agents/"*.md .claude/agents/
        cp "$SCRIPT_DIR/.claude/skills/evidence-audit/SKILL.md" .claude/skills/evidence-audit/
        cp "$SCRIPT_DIR/.claude/skills/citation-fix/SKILL.md" .claude/skills/citation-fix/
        cp "$SCRIPT_DIR/.claude/skills/evidence-report/SKILL.md" .claude/skills/evidence-report/
        echo ""
        echo "Plugin hook: Add this to your .claude/settings.json hooks:"
        echo '  "hooks": { "SessionStart": [{ "command": "echo 📑 Agent-Cite loaded. Commands: /cite-audit, /cite-fix, /cite-report" }] }'
        ;;
    codex)
        if [ -f "AGENTS.md" ]; then
            echo "" >> AGENTS.md
            cat "$SCRIPT_DIR/adapters/codex/AGENTS.md" >> AGENTS.md
            echo "Appended evidence protocol to existing AGENTS.md"
        else
            cp "$SCRIPT_DIR/adapters/codex/AGENTS.md" .
        fi
        ;;
    cursor)
        mkdir -p .cursor/rules
        cp "$SCRIPT_DIR/adapters/cursor/.cursor/rules/cite.md" .cursor/rules/
        ;;
    aider)
        if [ -f ".aider.conf.yml" ]; then
            echo "" >> .aider.conf.yml
            cat "$SCRIPT_DIR/adapters/aider/.aider.conf.yml" >> .aider.conf.yml
            echo "Appended evidence protocol to existing .aider.conf.yml"
        else
            cp "$SCRIPT_DIR/adapters/aider/.aider.conf.yml" .
        fi
        ;;
    generic)
        echo "Prompts and references installed. See prompts/ for usage."
        ;;
esac

echo ""
echo "✅ Agent-Cite installed for $CLI"
echo ""
echo "Commands available:"
echo "  /cite-audit <file>   — Audit for evidence protocol compliance"
echo "  /cite-fix <file>     — Fix violations with real citations"
echo "  /cite-report         — Project-wide evidence health report"
echo ""
echo "Next steps:"
echo "  1. Run /cite-audit on your latest AI-generated output"
echo "  2. Customize evidence-protocol.yaml for your project"
echo "  3. Run /cite-report for project-wide health score"
