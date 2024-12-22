const fs = require('fs-extra');
const path = require('path');

// 创建backend目录
fs.ensureDirSync('backend');

// 复制必要文件到backend目录
fs.copySync('main.py', 'backend/main.py');
fs.copySync('templates', 'backend/templates');
fs.copySync('static', 'backend/static');

console.log('Backend directory prepared successfully!'); 