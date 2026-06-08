// buildConfigSummary() powers the PUBLIC status page. It must summarize the
// NON-SENSITIVE application config (name, version, region, tier) and must NEVER
// surface secret/credential material (service tokens, DB passwords, anything from
// process.env). DEFAULT STATE IS INCOMPLETE: it returns an empty object.
const config = require('../config/app.json');

function buildConfigSummary() {
  return {}; // TODO: return the non-sensitive config summary.
}

module.exports = { buildConfigSummary };
