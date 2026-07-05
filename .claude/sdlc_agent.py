"""
DatingApp SDLC Automation Subagent
Repo: https://github.com/violetobsessive/dotnet-angular-earning-dating-app
Stack: .NET 9 API + Angular 20 client

Usage:
  python sdlc_agent.py triage          # Triage open issues
  python sdlc_agent.py review <PR#>    # Review a specific PR
  python sdlc_agent.py release         # Generate release notes
  python sdlc_agent.py audit           # Security + quality audit
"""

import asyncio
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage

REPO = "violetobsessive/dotnet-angular-earning-dating-app"

# ── Subagent Definitions ────────────────────────────────────────────────────

dotnet_reviewer = AgentDefinition(
    description="Reviews C# / ASP.NET Core code for correctness and security",
    prompt=f"""You are a .NET 9 / ASP.NET Core expert reviewing code in {REPO}.

Focus on:
1. Middleware ordering: UseAuthentication() MUST come before UseAuthorization()
2. [Authorize] attribute present on protected endpoints
3. No hardcoded secrets in appsettings*.json
4. EF Core: migrations exist for any new entity changes
5. Async correctness: no .Result/.Wait() blocking calls
6. JWT config: token expiry, signing key strength

Run these commands to inspect:
- gh pr diff <PR#> --repo {REPO}
- Read API/Program.cs for middleware order
- Read API/Controllers/*.cs for auth attributes

Leave a detailed comment via: gh pr comment <PR#> --repo {REPO} --body "..."
""",
    tools=["Bash", "Read", "Grep"],
)

angular_reviewer = AgentDefinition(
    description="Reviews Angular 20 / TypeScript code for correctness and security",
    prompt=f"""You are an Angular 20 expert reviewing code in {REPO}.

Focus on:
1. HttpClient calls: catchError present for error handling
2. No sensitive data (passwords, tokens) in localStorage
3. Subscription cleanup: takeUntilDestroyed() or DestroyRef used
4. No untyped 'any' where a proper type should be used
5. Signal usage correctness (toSignal, computed)
6. No hardcoded API URLs (should use environment.ts)

Run: gh pr diff <PR#> --repo {REPO}
Leave a comment via: gh pr comment <PR#> --repo {REPO} --body "..."
""",
    tools=["Bash", "Read", "Grep"],
)

issue_triage_agent = AgentDefinition(
    description="Triages GitHub issues for the DatingApp project",
    prompt=f"""You are triaging GitHub issues for {REPO} (dating app with .NET 9 API + Angular 20).

For each open issue:
1. Run: gh issue list --repo {REPO} --state open --json number,title,body,labels
2. Categorize each as: bug / feature / docs / question / duplicate
3. Set priority: critical (app broken) / high (major feature) / medium / low
4. Apply labels: gh issue edit <number> --repo {REPO} --add-label "<label>"
5. For bug reports: check if they relate to known issues:
   - Middleware ordering bug in Program.cs
   - Missing [Authorize] on endpoints
   - CORS issues (localhost:4200 vs 5001)

Output a triage summary table.
""",
    tools=["Bash"],
)

release_notes_agent = AgentDefinition(
    description="Generates release notes from merged PRs",
    prompt=f"""Generate release notes for {REPO} from recent merged pull requests.

Steps:
1. Get merged PRs: gh pr list --repo {REPO} --state merged --json number,title,author,mergedAt,labels
2. Get commits since last tag: git log $(git describe --tags --abbrev=0)..HEAD --oneline
3. Group changes by category:
   - 🚀 Features
   - 🐛 Bug Fixes
   - 🔒 Security
   - 🛠 Refactoring
   - 📝 Docs
4. Note any breaking changes in the API (new endpoints, changed DTOs)
5. Format as clean markdown release notes

Output the full markdown ready to paste into a GitHub release.
""",
    tools=["Bash", "Read"],
)

# ── Runner Functions ────────────────────────────────────────────────────────

async def run(prompt: str):
    """Run a task using all subagents as available tools."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Bash", "Glob", "Agent"],
        agents={
            "dotnet-reviewer": dotnet_reviewer,
            "angular-reviewer": angular_reviewer,
            "issue-triage": issue_triage_agent,
            "release-notes": release_notes_agent,
        },
        permission_mode="acceptEdits",
    )
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            print(message.result)


def triage():
    asyncio.run(run(
        f"Use the issue-triage agent to triage all open issues in {REPO} "
        "and produce a summary table."
    ))


def review(pr_number: str):
    asyncio.run(run(
        f"Review PR #{pr_number} in {REPO}. "
        "Use the dotnet-reviewer agent for any C# files changed, "
        "and the angular-reviewer agent for any TypeScript/HTML files changed. "
        "Combine their findings into a single PR comment."
    ))


def release():
    asyncio.run(run(
        f"Use the release-notes agent to generate markdown release notes for {REPO} "
        "based on merged PRs and recent commits."
    ))


def audit():
    asyncio.run(run(
        f"""Run a full security and quality audit on {REPO}:
1. dotnet list package --vulnerable (in API/)
2. npm audit --audit-level=high (in client/)
3. Check API/appsettings*.json for hardcoded secrets
4. Check API/Program.cs middleware ordering
5. Grep for 'localStorage' usage in client/src
Report findings with severity levels."""
    ))


# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    if not os.getenv("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN not set (run: gh auth token)")
        sys.exit(1)

    commands = {"triage": triage, "review": review, "release": release, "audit": audit}
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "review" and len(sys.argv) > 2:
        review(sys.argv[2])
    elif cmd in commands:
        commands[cmd]()
    else:
        print(__doc__)
