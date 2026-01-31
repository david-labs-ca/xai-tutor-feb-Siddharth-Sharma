# Submission / Next Steps

This repo was forked from an assessment. Follow these steps.

---

## 1. Commit and push to **your fork**

Do **not** open a Pull Request to the **original/upstream** repo. The assessment says:

> **Do not raise Pull Request in the original repo**

So you only push to your own fork (your personal GitHub account).

### Steps

```bash
# Ensure you're on your feature branch (or main)
git status
git add .
git commit -m "feat: implement auth, products, cart APIs; add tests and Docker verification"

# Push to YOUR fork (origin = your fork on GitHub)
git push -u origin feature/user-authentication
# Or, if you submit from main:
# git checkout main
# git merge feature/user-authentication
# git push origin main
```

- If `origin` is still the **original** repo, add your fork as a remote and push there:

```bash
# Add your fork (replace with your GitHub username and repo URL)
git remote add myfork https://github.com/YOUR_USERNAME/xai-tutor-feb-Siddharth-Sharma.git
git push -u myfork feature/user-authentication
```

---

## 2. Do **not** open a PR to upstream

Per the assessment instructions, **do not** create a Pull Request to the original repository.

Submit as the assessment asks (e.g. share the **link to your fork** or follow their submission form).

---

## 3. Before you push — quick check

```bash
./scripts/pre_submission_check.sh   # Docker + core APIs
pytest tests/ -v                    # All tests (use clean test DB if needed)
```

---

## Summary

| Action                                 | Do it?                    |
| -------------------------------------- | ------------------------- |
| Commit your work                       | Yes                       |
| Push to **your fork**                  | Yes                       |
| Open PR to **original repo**           | **No** (per instructions) |
| Share fork link / submit as instructed | Yes                       |
