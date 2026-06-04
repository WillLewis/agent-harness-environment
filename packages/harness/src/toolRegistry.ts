export type HarnessToolName = 'read_file' | 'search_repo' | 'edit_file' | 'run_command' | 'ask_human' | 'finalize';

export type HarnessTool = {
  name: HarnessToolName;
  description: string;
  controls: string[];
};

export const toolRegistry: HarnessTool[] = [
  {
    name: 'read_file',
    description: 'Inspect source or test files.',
    controls: ['path must exist', 'secret paths blocked']
  },
  {
    name: 'search_repo',
    description: 'Find symbols or text in the repo snapshot.',
    controls: ['query logged', 'result count capped']
  },
  {
    name: 'edit_file',
    description: 'Apply a patch and record diff.',
    controls: ['requires trace event', 'captures diff']
  },
  {
    name: 'run_command',
    description: 'Execute tests, lint, or type checks.',
    controls: ['allow-list', 'safety classifier']
  },
  {
    name: 'ask_human',
    description: 'Request clarification or steering.',
    controls: ['logged as intervention opportunity']
  },
  {
    name: 'finalize',
    description: 'Submit final answer.',
    controls: ['requires scoring-ready trace']
  }
];
