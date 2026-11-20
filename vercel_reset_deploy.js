const { execSync } = require("child_process");

const CONFIG = {
  TOKEN: process.env.VERCEL_TOKEN || "YOUR_VERCEL_TOKEN",
  PROJECT_ID: process.env.VERCEL_PROJECT_ID || "",
  TEAM_ID: process.env.VERCEL_TEAM_ID || "",
  DRY_RUN: process.env.DRY_RUN !== "false",
  TRIGGER_NEW_DEPLOY: process.env.TRIGGER_NEW_DEPLOY === "true",
};

const HEADERS = {
  Authorization: `Bearer ${CONFIG.TOKEN}`,
  "Content-Type": "application/json",
};

async function getAllDeployments() {
  const deployments = [];
  let until = null;

  while (true) {
    const url = new URL("https://api.vercel.com/v6/deployments");
    url.searchParams.set("limit", "100");
    if (CONFIG.PROJECT_ID) url.searchParams.set("projectId", CONFIG.PROJECT_ID);
    if (CONFIG.TEAM_ID) url.searchParams.set("teamId", CONFIG.TEAM_ID);
    if (until) url.searchParams.set("until", String(until));

    const response = await fetch(url.toString(), { headers: HEADERS });
    if (!response.ok) {
      throw new Error(`Failed to fetch (HTTP ${response.status}): ${await response.text()}`);
    }

    const data = await response.json();
    const batch = data.deployments || [];
    if (batch.length === 0) break;

    deployments.push(...batch);
    until = data.pagination?.next || null;
    if (!until) break;
  }

  return deployments;
}

async function deleteDeployment(deployment) {
  const label = `${deployment.name || "unknown"} -> https://${deployment.url}`;

  if (CONFIG.DRY_RUN) {
    console.log(`[DRY RUN] Would delete: ${label}`);
    return;
  }

  const delUrl = new URL(`https://api.vercel.com/v13/deployments/${deployment.uid}`);
  if (CONFIG.TEAM_ID) delUrl.searchParams.set("teamId", CONFIG.TEAM_ID);

  const response = await fetch(delUrl.toString(), { method: "DELETE", headers: HEADERS });
  if (response.ok) {
    console.log(`[DELETED] ${label} (HTTP ${response.status})`);
  } else {
    console.error(`[FAILED]  ${label} (HTTP ${response.status}): ${await response.text()}`);
  }
}

async function main() {
  if (!CONFIG.TOKEN || CONFIG.TOKEN === "YOUR_VERCEL_TOKEN") {
    throw new Error("Missing VERCEL_TOKEN.");
  }

  console.log("Fetching existing deployments...");
  const deployments = await getAllDeployments();
  console.log(`Found ${deployments.length} deployment(s).\n`);

  for (const deployment of deployments) {
    await deleteDeployment(deployment);
  }

  if (CONFIG.DRY_RUN) {
    console.log("\nDry run complete. Run with DRY_RUN=false to actually delete.");
  } else {
    console.log("\nCleanup complete!");
    if (CONFIG.TRIGGER_NEW_DEPLOY) {
      execSync(`vercel --prod --yes --token ${CONFIG.TOKEN}`, { stdio: "inherit" });
    }
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
