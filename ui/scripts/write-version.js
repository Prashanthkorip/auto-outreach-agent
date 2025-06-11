const fs = require('fs');
const path = require('path');
const pkg = require('../package.json');

const versionFilePath = path.join(__dirname, '..', 'out', 'version.txt'); // or .next if you're using SSR

fs.writeFileSync(versionFilePath, pkg.version, 'utf-8');