const fs = require('fs');

const build = fs.readFileSync('docs/build.md', 'utf8');
if (!build.includes('status: ok')) {
  throw new Error('Expected docs/build.md to include status: ok');
}

console.log('PASS tests/docs.test.js');
