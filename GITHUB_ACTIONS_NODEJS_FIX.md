# Fix GitHub Actions Node.js and Vite Build Errors

## Problems Identified

1. **Node.js version too old**: Using Node.js 18.20.8, but Vite requires 20.19+ or 22.12+
2. **ESM module error**: Vite config is ES module but Node.js 18 has issues with it
3. **Submodule error**: Broken submodule reference (from previous error)

## Solutions Applied

### 1. Created GitHub Actions Workflow

Created `.github/workflows/build.yml` with:
- Node.js 22 (latest LTS that supports Vite)
- Disabled submodules to fix the previous error
- Proper build and deploy steps

### 2. Update Your Existing Workflow (If You Have One)

If you already have a workflow file, update it to use Node.js 20 or 22:

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '22'  # Change from '18' to '22' or '20'
    cache: 'npm'
```

### 3. Fix package.json (If Needed)

Your `package.json` is missing the `vite` dependency. Add it:

```json
{
  "devDependencies": {
    "@vitejs/plugin-react": "^5.1.2",
    "vite": "^5.0.0",  // ADD THIS LINE
    "gh-pages": "^6.3.0"
  }
}
```

Then run:
```bash
npm install
```

### 4. Optional: Add "type": "module" to package.json

If you continue to have ESM issues, you can explicitly set the module type:

```json
{
  "name": "mushroom-ai-frontend",
  "version": "1.0.0",
  "type": "module",  // ADD THIS LINE
  "private": true,
  ...
}
```

## Quick Fix Steps

1. **Update your GitHub Actions workflow** to use Node.js 22:
   ```yaml
   - uses: actions/setup-node@v4
     with:
       node-version: '22'
   ```

2. **Add vite to package.json** (if missing):
   ```bash
   npm install -D vite@^5.0.0
   ```

3. **Commit and push**:
   ```bash
   git add .github/workflows/build.yml package.json package-lock.json
   git commit -m "Fix Node.js version and add vite dependency"
   git push
   ```

## Verify the Fix

After pushing, check your GitHub Actions:
1. Go to your repository on GitHub
2. Click on "Actions" tab
3. The build should now use Node.js 22 and succeed

## Alternative: Use Node.js 20

If you prefer Node.js 20 (also supported by Vite):
```yaml
node-version: '20'
```

## Notes

- Vite 5.x requires Node.js 20.19+ or 22.12+
- The ESM error should be resolved by upgrading Node.js
- Make sure `vite` is in your `devDependencies`

