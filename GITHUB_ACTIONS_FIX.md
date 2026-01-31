# Fix GitHub Actions Submodule Error

## Problem

GitHub Actions is failing with:
```
Error: fatal: No url found for submodule path 'node_modules/.cache/gh-pages/https!github.com!dhanush134!mush.git' in .gitmodules
```

This happens when a cache directory (likely from GitHub Pages deployment) was accidentally added as a submodule without a proper URL.

## Solution

### Option 1: Remove the Problematic Submodule (Recommended)

1. **Clone your repository locally** (if not already):
   ```bash
   git clone https://github.com/dhanush134/mush.git
   cd mush
   ```

2. **Check for `.gitmodules` file**:
   ```bash
   cat .gitmodules
   ```

3. **Remove the problematic submodule entry**:
   - If `.gitmodules` exists and contains the problematic entry, edit it to remove the line referencing `node_modules/.cache/gh-pages/...`
   - Or delete the entire `.gitmodules` file if it only contains this entry

4. **Remove the submodule from Git index**:
   ```bash
   git rm --cached node_modules/.cache/gh-pages/https!github.com!dhanush134!mush.git
   ```

5. **Remove the submodule directory** (if it exists):
   ```bash
   rm -rf node_modules/.cache/gh-pages
   ```

6. **Add `node_modules/` to `.gitignore`** (if not already):
   ```bash
   echo "node_modules/" >> .gitignore
   ```

7. **Commit and push**:
   ```bash
   git add .gitmodules .gitignore
   git commit -m "Remove broken submodule reference"
   git push
   ```

### Option 2: Fix the Submodule URL

If you actually need this as a submodule:

1. **Edit `.gitmodules`** to add a proper URL:
   ```ini
   [submodule "node_modules/.cache/gh-pages/https!github.com!dhanush134!mush.git"]
       path = node_modules/.cache/gh-pages/https!github.com!dhanush134!mush.git
       url = https://github.com/dhanush134/mush.git
   ```

2. **Update submodule**:
   ```bash
   git submodule sync
   git submodule update --init --recursive
   ```

### Option 3: Disable Submodule Fetching in GitHub Actions

If you don't need submodules at all, update your GitHub Actions workflow:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: false  # Add this line
```

Or:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
    submodules: false  # Disable submodules
```

## Quick Fix (If you have access to the repository)

1. Go to your repository on GitHub: `https://github.com/dhanush134/mush`
2. Navigate to the `.gitmodules` file (if it exists)
3. Delete the problematic entry or the entire file
4. Commit the change

## Prevention

To prevent this in the future:

1. **Add to `.gitignore`**:
   ```
   node_modules/
   .cache/
   **/node_modules/
   **/.cache/
   ```

2. **Check before committing**:
   ```bash
   git status
   ```
   Make sure you're not committing cache directories or `node_modules/`

3. **Use `.gitignore` properly** for your project type

## Verify the Fix

After applying the fix, your GitHub Actions should run successfully. The checkout step should complete without submodule errors.

