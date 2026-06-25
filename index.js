#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const tuikkusuDir = path.join(__dirname, 'tuikkusu');

// Check if Go is installed
const goCheck = spawnSync('go', ['version']);
if (goCheck.error) {
  console.error('\x1b[31m[ERROR]\x1b[0m Go is not installed or not in your PATH.');
  console.error('Tuikkusu requires Go to run. Please install it from: https://go.dev/doc/install');
  process.exit(1);
}

// Run the Go application directly, preserving the TUI (stdio: inherit)
console.log('\x1b[36mStarting Tuikkusu Engine...\x1b[0m');
const result = spawnSync('go', ['run', 'main.go'], {
  cwd: tuikkusuDir,
  stdio: 'inherit'
});

if (result.error) {
  console.error('\x1b[31m[ERROR]\x1b[0m Failed to execute the Tuikkusu Go application.', result.error);
  process.exit(1);
}

process.exit(result.status || 0);
