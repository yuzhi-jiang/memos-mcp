/**
 * 安装脚本
 * 
 * 这个脚本在 npm 安装后运行，负责安装必要的 Python 依赖
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 检查 Python 是否安装
try {
  const pythonVersion = execSync('python --version').toString();
  console.log(`检测到 Python: ${pythonVersion}`);
} catch (error) {
  console.error('错误: 未检测到 Python。请确保 Python 已安装并添加到 PATH 中。');
  process.exit(1);
}

// 安装 Python 依赖
try {
  console.log('正在安装 Python 依赖...');
  const requirementsPath = path.join(__dirname, '..', 'requirements.txt');
  
  if (fs.existsSync(requirementsPath)) {
    execSync(`pip install -r "${requirementsPath}"`, { stdio: 'inherit' });
    console.log('Python 依赖安装成功！');
  } else {
    console.error(`错误: 找不到 requirements.txt 文件: ${requirementsPath}`);
    process.exit(1);
  }
} catch (error) {
  console.error(`安装 Python 依赖时出错: ${error.message}`);
  process.exit(1);
}

// 创建 .env 文件（如果不存在）
try {
  const envPath = path.join(__dirname, '..', '.env');
  const envExamplePath = path.join(__dirname, '..', '.env.example');
  
  if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
    console.log('正在创建 .env 文件...');
    fs.copyFileSync(envExamplePath, envPath);
    console.log('已创建 .env 文件，请编辑该文件并填写您的 Memos URL 和 API Key。');
  }
} catch (error) {
  console.error(`创建 .env 文件时出错: ${error.message}`);
}

console.log('安装完成！您可以通过运行 "npx memos-mcp" 来启动服务器。');
