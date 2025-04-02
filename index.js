#!/usr/bin/env node

/**
 * Memos MCP 服务器启动器
 * 
 * 这个脚本负责启动 Python MCP 服务器
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 获取 Python 脚本的路径
const scriptPath = path.join(__dirname, 'memos_mcp_server.py');

// 检查 Python 脚本是否存在
if (!fs.existsSync(scriptPath)) {
  console.error(`错误: 找不到 MCP 服务器脚本: ${scriptPath}`);
  process.exit(1);
}

// 启动 Python 进程
console.log('启动 Memos MCP 服务器...');
const pythonProcess = spawn('python', [scriptPath], {
  stdio: 'inherit'
});

// 处理进程事件
pythonProcess.on('error', (err) => {
  console.error(`启动 Python 进程时出错: ${err.message}`);
  process.exit(1);
});

pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.error(`Python 进程异常退出，退出码: ${code}`);
    process.exit(code);
  }
});

// 处理 SIGINT 信号 (Ctrl+C)
process.on('SIGINT', () => {
  console.log('接收到中断信号，正在关闭服务器...');
  pythonProcess.kill('SIGINT');
});
