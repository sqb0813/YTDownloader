const fs = require('fs-extra');
const path = require('path');

// 清理构建目录
const dirsToClean = [
  'dist',
  'backend/dist',
  'backend/__pycache__',
  'node_modules'
];

dirsToClean.forEach(dir => {
  if (fs.existsSync(dir)) {
    fs.removeSync(dir);
    console.log(`Cleaned ${dir}`);
  }
}); 