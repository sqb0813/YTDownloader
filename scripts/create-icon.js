const fs = require('fs-extra');
const path = require('path');

// 创建build目录
fs.ensureDirSync('build');

// 如果没有图标文件，可以复制一个默认图标或创建一个空图标
if (!fs.existsSync('build/icon.ico')) {
  // 这里可以添加创建/复制图标的逻辑
  console.log('Please add an icon.ico file to the build directory');
} 