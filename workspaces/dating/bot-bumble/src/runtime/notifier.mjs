import { execFile as _execFile } from "node:child_process";
import { promisify } from "node:util";

const execFile = promisify(_execFile);

const SELF_PHONE = process.env.DATING_SELF_PHONE;
const SEND_SH = "/Users/shakstzy/ULTRON/_shell/skills/imessage/send.sh";

export async function notifySelf(text) {
  if (process.env.DATING_NOTIFY_DISABLE === "1") return;
  if (!SELF_PHONE) {
    console.error("notifier: DATING_SELF_PHONE env var not set, skipping");
    return;
  }
  try {
    await execFile(SEND_SH, ["--to", SELF_PHONE, "--text", text], { timeout: 15000 });
  } catch (e) {
    console.error(`notifier: send.sh failed: ${e.stderr?.trim() || e.message}`);
  }
}
