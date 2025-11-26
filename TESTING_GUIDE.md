# 🧪 本地测试指南

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd /Users/linkzhao/workspace/AI/history_book

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件（如果还没有）：

```bash
# 复制示例文件
cp env.example .env

# 编辑.env文件，填入你的DeepSeek API密钥
# DEEPSEEK_API_KEY=your_actual_api_key_here
```

或者直接设置环境变量：

```bash
export DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 3. 测试生成章节

#### 方式一：生成下一章（按顺序）

```bash
python scripts/generate_chapter.py
```

这会自动找到下一个未生成的章节并生成。

#### 方式二：生成指定章节

```bash
# 生成第1章
python scripts/generate_chapter.py 1

# 生成第3章
python scripts/generate_chapter.py 3
```

## 测试步骤详解

### 步骤1：检查环境

```bash
# 检查Python版本（需要3.7+）
python3 --version

# 检查依赖是否安装
python3 -c "import requests; print('✅ requests installed')"
```

### 步骤2：检查配置

```bash
# 检查配置文件是否存在
ls -la config/config.json

# 检查章节规划文件
ls -la chapters_plan.json

# 检查API密钥是否设置
echo $DEEPSEEK_API_KEY
```

### 步骤3：运行测试

```bash
# 生成第一章（测试）
python scripts/generate_chapter.py 1
```

### 步骤4：查看结果

```bash
# 查看生成的章节
cat chapters/chapter_01/README.md

# 查看图片目录
ls -la chapters/chapter_01/images/
```

## 测试输出说明

### 正常输出示例

```
============================================================
📚 从春秋到民国 - Chapter Generator
============================================================

📝 Generating Chapter 1: 第一章：抢戏的配角们——诸侯不"侯"，天子在打酱油
   Period: 春秋时期(前770-前476)
   Calling DeepSeek API...
   Saving chapter...
   Processing images...
   Found 2 image placeholder(s)
   Searching image for: 春秋时期的诸侯争霸场景
   ✅ Downloaded: images/chapter_01_image_1.jpg
   Searching image for: 齐桓公画像
   ✅ Downloaded: images/chapter_01_image_2.jpg
✅ Chapter 1 generated successfully!
   Saved to: chapters/chapter_01/README.md
```

### 常见错误

#### 1. API密钥未设置

```
❌ Error: API key not found in environment variable: DEEPSEEK_API_KEY
```

**解决方法：**
```bash
export DEEPSEEK_API_KEY=your_key_here
```

#### 2. 依赖未安装

```
ModuleNotFoundError: No module named 'requests'
```

**解决方法：**
```bash
pip install -r requirements.txt
```

#### 3. 配置文件不存在

```
FileNotFoundError: config/config.json
```

**解决方法：** 确保在项目根目录运行脚本

#### 4. API调用失败

```
❌ Error generating chapter: API request failed: ...
```

**解决方法：**
- 检查API密钥是否正确
- 检查网络连接
- 检查DeepSeek账户余额

## 测试不同场景

### 测试1：生成第一章

```bash
python scripts/generate_chapter.py 1
```

**预期结果：**
- 创建 `chapters/chapter_01/README.md`
- 创建 `chapters/chapter_01/images/` 目录
- 下载相关图片

### 测试2：生成下一章（如果第一章已存在）

```bash
python scripts/generate_chapter.py
```

**预期结果：**
- 自动找到下一章（第2章）
- 生成第2章内容

### 测试3：测试图片功能

```bash
# 先删除第一章的图片（如果存在）
rm -rf chapters/chapter_01/images/

# 重新生成第一章（会重新下载图片）
python scripts/generate_chapter.py 1
```

**预期结果：**
- 重新搜索并下载图片

### 测试4：禁用图片功能

编辑 `config/config.json`：
```json
{
  "images": {
    "enabled": false
  }
}
```

然后运行：
```bash
python scripts/generate_chapter.py 1
```

**预期结果：**
- 只生成文本，不下载图片

## 验证生成的内容

### 检查章节内容

```bash
# 查看章节文件
cat chapters/chapter_01/README.md

# 检查是否包含图片引用
grep -n "!\[" chapters/chapter_01/README.md
```

### 检查图片文件

```bash
# 列出所有图片
ls -lh chapters/chapter_01/images/

# 检查图片大小（应该大于0）
find chapters/chapter_01/images/ -type f -size +0
```

### 检查Markdown格式

```bash
# 检查是否有语法错误
python3 -c "
import re
with open('chapters/chapter_01/README.md', 'r') as f:
    content = f.read()
    images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    print(f'Found {len(images)} images')
    for desc, path in images:
        print(f'  - {desc}: {path}')
"
```

## 调试技巧

### 1. 查看详细日志

修改脚本添加更多调试信息，或使用Python的logging：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 测试API连接

```bash
python3 -c "
import os
import requests

api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print('❌ API key not set')
else:
    print('✅ API key found')
    # 可以测试一个简单的API调用
"
```

### 3. 测试图片搜索

```bash
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from baidu_image_search import BaiduImageSearcher

searcher = BaiduImageSearcher()
results = searcher.search('春秋时期', 0, 3)
print(f'Found {len(results)} images')
if results:
    print(f'First image URL: {results[0][\"url\"]}')
"
```

## 清理测试数据

```bash
# 删除所有生成的章节（谨慎使用）
rm -rf chapters/chapter_*

# 只删除第一章
rm -rf chapters/chapter_01
```

## 完整测试流程

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置API密钥
export DEEPSEEK_API_KEY=your_key_here

# 3. 生成第一章
python scripts/generate_chapter.py 1

# 4. 检查结果
ls -la chapters/chapter_01/
cat chapters/chapter_01/README.md | head -n 50

# 5. 更新主README
python scripts/update_main_readme.py

# 6. 查看更新后的主README
cat README.md | grep "第一章"
```

## 常见问题

### Q: 如何跳过图片下载，只生成文本？

A: 在 `config/config.json` 中设置：
```json
{
  "images": {
    "enabled": false
  }
}
```

### Q: 如何只测试图片搜索，不生成章节？

A: 使用测试脚本：
```bash
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from baidu_image_search import BaiduImageSearcher

searcher = BaiduImageSearcher()
results = searcher.search('春秋时期', 0, 5)
for i, img in enumerate(results, 1):
    print(f'{i}. {img[\"url\"]}')
"
```

### Q: 如何查看生成的章节列表？

A: 
```bash
ls -d chapters/chapter_*/ | sort -V
```

### Q: 如何重新生成某个章节？

A: 先删除该章节，然后重新生成：
```bash
rm -rf chapters/chapter_01
python scripts/generate_chapter.py 1
```

---

**提示**：首次测试建议生成第1章，内容较短，测试速度快。

