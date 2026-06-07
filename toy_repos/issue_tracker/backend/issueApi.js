// DEFAULT STATE IS UNSOLVED: the API payload omits the shared field the contract
// requires. The task is to add it (backend subagent), aligned with the frontend.
function createIssuePayload({ title }) {
  return { title };
}

module.exports = { createIssuePayload };
