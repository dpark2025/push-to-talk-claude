# Workflow Reminders

## Feature Branch Lifecycle

After completing a spec (all speckit steps through implementation):

1. **Commit** all changes with descriptive message
2. **Push** to remote repository
3. **Create PR** to merge feature branch to main
4. **Remove feature branch** after merge is complete

```bash
# After implementation complete:
git add -A && git commit -m "feat: complete <feature-name>"
git push origin <branch-name>
gh pr create --title "feat: <feature-name>" --body "..."
# After PR merged:
git checkout main && git pull
git branch -d <branch-name>
git push origin --delete <branch-name>
```

## Checkpoint Strategy

Create checkpoint commits at key milestones:
- After `/speckit.specify` - spec defined
- After `/speckit.plan` + `/speckit.tasks` - design complete
- After `/speckit.analyze` - ready for implementation
- After `/speckit.implement` - feature complete
