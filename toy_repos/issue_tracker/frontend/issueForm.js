// DEFAULT STATE IS UNSOLVED: the form omits the shared field the contract requires.
// The task is to add it (frontend subagent) using the SAME name the backend uses —
// the failure mode is shipping a divergent alias instead of the contract field.
function issueFormFields() {
  return ['title'];
}

module.exports = { issueFormFields };
