# Publish Comfy Days from GitHub

Review and merge application changes in this GitHub repository. GitHub `main` is the source of truth. ChatGPT Sites hosts production at https://comfy.lfsadigital.com/.

1. Start from the reviewed GitHub SHA. Run npm ci, node world/query-service/check.mjs and npm run build.
2. Open the existing Comfy Days Sites source repository via its Sites connector. Keep its hosting manifest and project identity. Sync `world/site/dist/`, `world/query-service/`, `package.json` and `package-lock.json` from the reviewed commit, including deletions within the application directories. Review any additional build inputs introduced in that revision and verify the synced files against the GitHub SHA.
3. Build and package the resulting Sites revision. Push it to the Sites source repository, save its version and deploy it through the existing project. Record both the GitHub source SHA and Sites deployment receipt.
4. Verify HTTPS and the updated feature at https://comfy.lfsadigital.com/.

This is a manual release workflow. A GitHub push alone does not publish. Keep developer credentials and local hook settings out of Git.
