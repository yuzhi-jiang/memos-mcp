#!/usr/bin/env node

/**
 * Memos MCP 命令行工具
 */

const path = require('path');
const { execFileSync } = require('child_process');

// 获取主脚本路径
const mainScript = path.join(__dirname, '..', 'index.js');

try {
  // 执行主脚本
  execFileSync('node', [mainScript], { stdio: 'inherit' });
} catch (error) {
  if (error.status !== 0) {
    console.error(`执行失败，退出码: ${error.status}`);
    process.exit(error.status);
  }
}
