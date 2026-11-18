# Publish Comfy Days from GitHub

Review and merge application changes in this GitHub repository. GitHub main is the development source after the migration is merged. ChatGPT Sites hosts production at https://comfy.lfsadigital.com/.

1. Start from the reviewed GitHub SHA. Run npm ci, node world/query-service/check.mjs and npm run build.
2. Open the existing Comfy Days Sites source repository via its Sites connector. Keep its hosting manifest and project identity. Copy the reviewed frontend and query-service sources and their required dependencies into a clean checkout of that repository. Check for release-only files and review the diff.
3. Build and package the resulting Sites revision. Push it to the Sites source repository, save its version and deploy it through the existing project. Record both the GitHub source SHA and Sites deployment receipt.
4. Verify HTTPS and the updated feature at https://comfy.lfsadigital.com/.

This is a manual release workflow. A GitHub push alone does not publish. Keep developer credentials and local hook settings out of Git.
