#!/usr/bin/env python3
"""
Script to update the main README.md with the table of contents.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def load_chapters_plan(plan_path: str = "chapters_plan.json") -> Dict:
    """Load chapters plan from JSON file."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_generated_chapters(chapters_dir: str = "chapters") -> List[int]:
    """Get list of generated chapter IDs."""
    chapters_path = Path(chapters_dir)
    generated = []
    
    if not chapters_path.exists():
        return generated
    
    for chapter_dir in sorted(chapters_path.iterdir()):
        if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
            readme_path = chapter_dir / "README.md"
            if readme_path.exists():
                # Extract chapter number from directory name
                chapter_num = int(chapter_dir.name.split("_")[1])
                generated.append(chapter_num)
    
    return generated


def generate_readme_content(chapters_plan: Dict, generated_chapters: List[int]) -> str:
    """Generate the main README content."""
    
    content = f"""# 📚 {chapters_plan['book_title']}

> {chapters_plan['book_description']}

## 📖 关于本书

本书以风趣幽默的笔调，带你穿越中国历史长河，从春秋战国的百家争鸣，到民国时期的风云变幻。每一章都精心雕琢，既有历史的厚重感，又有故事的趣味性。

**写作风格：** 轻松幽默、通俗易懂、趣味盎然

**更新频率：** 每天早上7点自动更新一章

**技术实现：** 基于DeepSeek大模型自动生成，保持文笔一致

---

## 📑 目录

"""
    
    # Add table of contents
    total_chapters = len(chapters_plan['chapters'])
    generated_count = len(generated_chapters)
    
    content += f"**进度：** {generated_count}/{total_chapters} 章已完成\n\n"
    
    for chapter in chapters_plan['chapters']:
        chapter_id = chapter['id']
        is_generated = chapter_id in generated_chapters
        
        if is_generated:
            link = f"[{chapter['title']}](./chapters/chapter_{chapter_id:02d}/README.md)"
            status = "✅"
        else:
            link = chapter['title']
            status = "⏳"
        
        content += f"{status} **{link}**  \n"
        content += f"   *{chapter['period']}*\n"
        
        # Add core concept if available
        if 'core_concept' in chapter and chapter['core_concept']:
            content += f"   **核心梗：** {chapter['core_concept']}\n"
        
        # Add content guide if available (truncated for README)
        if 'content_guide' in chapter and chapter['content_guide']:
            guide_preview = chapter['content_guide'][:150] + "..." if len(chapter['content_guide']) > 150 else chapter['content_guide']
            content += f"   **内容导读：** {guide_preview}\n"
        elif 'description' in chapter:
            content += f"   {chapter['description']}\n"
        
        content += "\n"
    
    # Add footer
    content += f"""---

## 🤖 关于生成

本书由AI大模型（DeepSeek）生成，采用以下技术栈：

- **AI模型：** DeepSeek Chat
- **自动化：** GitHub Actions
- **语言：** Python
- **版本控制：** Git/GitHub

## 📝 系统提示词

{chapters_plan['system_prompt']}

---

## 📅 更新日志

- **最后更新：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **已完成章节：** {generated_count}/{total_chapters}
- **下一章：** {chapters_plan['chapters'][generated_count]['title'] if generated_count < total_chapters else '已完成全部章节'}

---

## ⚖️ 声明

本书内容由AI生成，仅供学习和娱乐参考。历史事实部分力求准确，但文学演绎和趣味性表达可能存在艺术加工。如发现史实错误，欢迎指正。

---

<div align="center">
  
**📚 欢迎阅读，欢迎Star！**

*Let's journey through Chinese history with humor and wisdom!*

</div>
"""
    
    return content


def main():
    """Main entry point."""
    print("📝 Updating main README.md...")
    
    try:
        # Load chapters plan
        chapters_plan = load_chapters_plan()
        
        # Get generated chapters
        generated_chapters = get_generated_chapters()
        
        # Generate README content
        content = generate_readme_content(chapters_plan, generated_chapters)
        
        # Save to file
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ README.md updated successfully!")
        print(f"   Generated chapters: {len(generated_chapters)}/{len(chapters_plan['chapters'])}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()


