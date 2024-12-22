const { execSync } = require('child_process');
const fs = require('fs-extra');

// 清理现有依赖
console.log('Cleaning existing dependencies...');
if (fs.existsSync('node_modules')) {
  fs.removeSync('node_modules');
}
if (fs.existsSync('package-lock.json')) {
  fs.removeSync('package-lock.json');
}

// 安装依赖
console.log('Installing dependencies...');
execSync('npm install', { stdio: 'inherit' });

console.log('Dependencies installed successfully!'); 