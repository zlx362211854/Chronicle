# 📚 从春秋到民国 - 项目设置说明

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/history_book.git
cd history_book
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

获取DeepSeek API密钥：
- 访问 https://platform.deepseek.com/
- 注册并获取API密钥
- 复制`.env.example`为`.env`
- 将你的API密钥填入`.env`文件

```bash
# 创建.env文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 4. 手动生成章节（测试）

```bash
# 生成下一章
python scripts/generate_chapter.py

# 生成指定章节（例如第3章）
python scripts/generate_chapter.py 3

# 更新主README
python scripts/update_main_readme.py
```

## 🔧 部署到GitHub

### 1. 创建GitHub仓库

1. 在GitHub上创建新仓库，名称如：`history_book`
2. 不要初始化README（我们已经有了）

### 2. 配置GitHub Secrets

在GitHub仓库中设置Secret：

1. 进入仓库设置：`Settings` > `Secrets and variables` > `Actions`
2. 点击 `New repository secret`
3. 添加以下Secret：
   - Name: `DEEPSEEK_API_KEY`
   - Value: 你的DeepSeek API密钥

### 3. 推送代码到GitHub

```bash
# 初始化Git仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/history_book.git

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Setup history book project"

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 4. 启用GitHub Actions

1. 进入仓库的 `Actions` 标签
2. 如果看到提示，点击 `I understand my workflows, go ahead and enable them`
3. GitHub Actions将在每天早上7点（北京时间）自动运行

### 5. 手动触发生成（可选）

1. 进入 `Actions` 标签
2. 选择 `Generate Daily Chapter` workflow
3. 点击 `Run workflow`
4. 可以选择生成下一章或指定章节号

## 📁 项目结构

```
history_book/
├── .github/
│   └── workflows/
│       └── generate_chapter.yml    # GitHub Actions自动化配置
├── chapters/                        # 存放生成的章节
│   ├── chapter_01/
│   │   └── README.md
│   ├── chapter_02/
│   │   └── README.md
│   └── ...
├── config/
│   └── config.json                 # 项目配置文件
├── scripts/
│   ├── generate_chapter.py         # 章节生成脚本
│   └── update_main_readme.py       # README更新脚本
├── chapters_plan.json              # 章节规划文件
├── requirements.txt                # Python依赖
├── .env.example                    # 环境变量示例
├── .gitignore                      # Git忽略文件
└── README.md                       # 主README文件

```

## 🔍 配置说明

### chapters_plan.json

包含所有章节的规划信息：
- 章节标题
- 历史时期
- 关键词
- 章节描述

### config/config.json

包含生成配置：
- DeepSeek API配置
- 生成参数（temperature, max_tokens等）
- 定时任务时间
- 输出目录设置

## 🎨 自定义配置

### 修改生成时间

编辑 `.github/workflows/generate_chapter.yml`:

```yaml
schedule:
  # 修改cron表达式
  # 当前设置: 每天UTC 23:00 (北京时间7:00)
  - cron: '0 23 * * *'
```

### 修改生成参数

编辑 `config/config.json`:

```json
{
  "generation_settings": {
    "temperature": 0.8,      # 创造性（0.0-1.0）
    "max_tokens": 4000,      # 最大生成长度
    "top_p": 0.95           # 采样参数
  }
}
```

### 修改章节计划

编辑 `chapters_plan.json`，添加或修改章节信息。

## 🐛 故障排查

### API调用失败

1. 检查API密钥是否正确
2. 检查DeepSeek账户余额
3. 查看GitHub Actions日志了解详细错误

### GitHub Actions不运行

1. 确保已在仓库设置中启用Actions
2. 检查YAML文件语法是否正确
3. 确保有写入权限（Settings > Actions > Workflow permissions）

### 生成内容质量问题

1. 调整`temperature`参数（降低更稳定，提高更有创意）
2. 修改系统提示词
3. 优化章节描述和关键词

## 📊 监控和维护

### 查看生成日志

1. 进入GitHub仓库的 `Actions` 标签
2. 选择最近的workflow运行
3. 查看详细日志

### 手动修正章节

如果某章节生成不理想：
1. 手动编辑 `chapters/chapter_XX/README.md`
2. 或删除该文件后重新生成：
   ```bash
   python scripts/generate_chapter.py XX
   ```

## 💡 最佳实践

1. **定期检查：** 每周检查一次生成质量
2. **备份重要内容：** 定期fork或clone备份
3. **监控API使用：** 关注DeepSeek API使用量和费用
4. **渐进改进：** 根据生成效果逐步优化提示词

## 📝 贡献指南

欢迎提交Issue和Pull Request：
- 改进提示词
- 优化生成逻辑
- 添加新功能
- 修正历史错误

## 📧 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- Email: your-email@example.com

---

祝你使用愉快！让AI帮你写一本有趣的历史书吧！📚✨


