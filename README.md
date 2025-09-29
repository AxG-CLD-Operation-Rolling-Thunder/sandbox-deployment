# AIX Agent Pipeline – Developer Guide

This repository is the **single source of truth** for all agent development and deployment at AxG.  
If your agent is not a branch here, it **does not exist** in the pipeline.

---

## 🚦 Pipeline Rules

1. **Single Repo Only**  
   We will **not** be making new repositories for agents. This is the only supported pipeline.

2. **Branch Naming**  
   Each agent lives on **one branch only**.  
   Format: `<dev_initials>-<agent_name>-deployment-branch`  
   Example: `se-invoice-deployment-branch`

3. **No Cross-Merging**  
   Do **not** merge into each other’s branches. Each branch = one agent.

4. **No Environment Variables**  
   Runtime constants will **not** be passed as environment variables.
   - If you need something dynamic at runtime, you must:
     - Work with Sergio or George to set up a GCP Secret, or
     - (If you have permission) create it yourself in Secret Manager and inject via Cloud Build or the Secret Manager client library.

---

## 📂 Required Structure

Every agent branch must follow this exact structure:

```
agent/
  agent.py        # must export `root_agent`
agent.yaml        # metadata/config
```

That’s it. **Three files = one working agent.**

- By branching from [`example-agent`](./tree/example-agent), you get a fully working starter agent to modify.
- If you already have an agent in a standalone repo, you can port it here by restructuring to match the contract above.

---

## 🔄 Workflow

### 1. Clone and Checkout

```bash
git clone https://github.com/AxG-AI-Exchange-GenAI-Initiative/aix-agent-pipeline.git
cd aix-agent-pipeline
git checkout -b <dev_initials>-<agent_name>-deployment-branch
```

### 2. Build Your Agent

- Add your code inside `agent/agent.py` and ensure you export `root_agent`.
- Fill in `agent.yaml` with required metadata.

### 3. Commit and Push

```bash
git add agent/agent.py agent.yaml
git commit -m "Initial agent commit"
git push origin <dev_initials>-<agent_name>-deployment-branch
```

### 4. Deployment

- Pushing to your branch triggers the Cloud Build pipeline.
- If the structure and secrets are correct, your agent is automatically deployed.

---

## ✅ Summary

- Agents only live here, in **branches**.
- **Three files only**: `agent/`, `agent.py`, `agent.yaml`.
- No env vars in code; use Secrets for anything dynamic.
- No merging across branches.
- Clone → branch → code → push → deployed.

---

## ⚠️ Important Troubleshooting Notes

1. **Authorization Conflicts**

   - You cannot use an authorization currently in use by an agent.
   - It is recommended to start with a fresh `authorization` definition in your `agent.yaml`.
   - Once created, this authorization can be reused across deployments.

2. **DisplayName-Based Lookups**

   - Lookups for **reasoning engines**, **authorizations**, and **agent spaces** are done by `displayName`.
   - Your deployment will **fail** if:
     - `agent.yaml: reasoning_engine_name` matches an existing one in GCP, or
     - There are duplicates of the same name in GCP.
   - This rule also applies to `agent.yaml: agent_space_name` and `agent.yaml: authorizations`.

3. **Renaming Reasoning Engines**

   - Updating `agent.yaml: reasoning_engine_name` does **not** update the existing engine.
   - It will always create a **new engine deployment**.

4. **Renaming Agent Spaces**
   - Updating `agent.yaml: agent_space_name` does **not** update the existing agent space.
   - It will always create a **new agent space deployment**.

---

✅ These issues are solvable, and we are actively working on more permanent solutions based on your feedback.
