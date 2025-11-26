#!/usr/bin/env python3
"""
历史书章节生成脚本。
使用 DeepSeek API 生成新章节。
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import requests

# 如果存在 .env 文件，则加载环境变量
def load_env_file():
    """从 .env 文件加载环境变量。"""
    # Try multiple possible paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    possible_paths = [
        Path(".env"),  # Current working directory
        project_root / ".env",  # Project root
        script_dir / ".env",  # Scripts directory
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ.setdefault(key, value)
                # Debug: print loaded status
                if os.getenv('DEEPSEEK_API_KEY'):
                    print(f"✅ Loaded API key from {env_path}")
                return True
            except Exception as e:
                print(f"⚠️  Error loading .env from {env_path}: {str(e)}")
                continue
    return False

# Load .env file at module import
load_env_file()

# Import Baidu image search
try:
    from .baidu_image_search import BaiduImageSearcher, extract_image_placeholders
except ImportError:
    try:
        from baidu_image_search import BaiduImageSearcher, extract_image_placeholders
    except ImportError:
        BaiduImageSearcher = None
        extract_image_placeholders = None


class ChapterGenerator:
    """使用 DeepSeek API 处理章节生成。"""
    
    def __init__(self, config_path: str = "config/config.json", plan_path: str = "chapters_plan.json"):
        """
        初始化章节生成器。
        
        参数:
            config_path: 配置文件路径
            plan_path: 章节规划文件路径
        """
        # Load .env file before reading config
        self._load_env_file()
        
        self.config = self._load_config(config_path)
        self.chapters_plan = self._load_chapters_plan(plan_path)
        
        # Check API key
        api_key_env_name = self.config["deepseek_api"]["api_key_env"]
        self.api_key = os.getenv(api_key_env_name)
        
        if not self.api_key:
            # Try to provide helpful error message
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            env_file_found = any([
                Path(".env").exists(),
                (project_root / ".env").exists(),
            ])
            error_msg = f"API key not found in environment variable: {api_key_env_name}"
            if env_file_found:
                error_msg += "\n.env file exists but API key was not loaded. Please check .env file format."
                error_msg += f"\nTried paths: {Path.cwd() / '.env'}, {project_root / '.env'}"
            else:
                error_msg += f"\nPlease create .env file with: {api_key_env_name}=your_api_key"
            raise ValueError(error_msg)
    
    def _load_env_file(self):
        """从 .env 文件加载环境变量。"""
        # Try multiple possible paths
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        current_dir = Path.cwd()
        
        possible_paths = [
            current_dir / ".env",  # Current working directory
            project_root / ".env",  # Project root
            script_dir / ".env",  # Scripts directory
        ]
        
        loaded = False
        for env_path in possible_paths:
            if env_path.exists():
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if key and value:
                                    os.environ.setdefault(key, value)
                                    if key == 'DEEPSEEK_API_KEY':
                                        loaded = True
                    if loaded:
                        print(f"✅ Loaded API key from {env_path}")
                    return
                except Exception as e:
                    print(f"⚠️  Failed to load .env file from {env_path}: {str(e)}")
    
    def _load_config(self, config_path: str) -> Dict:
        """从 JSON 文件加载配置。"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_chapters_plan(self, plan_path: str) -> Dict:
        """从 JSON 文件加载章节规划。"""
        with open(plan_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_next_chapter_to_generate(self) -> Optional[Dict]:
        """
        查找下一个需要生成的章节。
        
        返回:
            章节字典，如果所有章节都已生成则返回 None
        """
        chapters_dir = Path(self.config["output"]["chapters_dir"])
        
        for chapter in self.chapters_plan["chapters"]:
            chapter_dir = chapters_dir / f"chapter_{chapter['id']:02d}"
            readme_path = chapter_dir / self.config["output"]["readme_filename"]
            
            if not readme_path.exists():
                return chapter
        
        return None
    
    def _load_prompt_template(self) -> str:
        """
        加载提示词模板文件。
        
        返回:
            提示词模板字符串
        """
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        template_path = project_root / "prompts" / "chapter_prompt_template.txt"
        
        if not template_path.exists():
            raise FileNotFoundError(f"提示词模板文件不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _create_chapter_prompt(self, chapter: Dict) -> str:
        """
        创建生成章节的提示词。
        
        参数:
            chapter: 章节信息字典
            
        返回:
            完整的提示词字符串
        """
        # 加载提示词模板
        template = self._load_prompt_template()
        
        # 准备变量
        book_title = self.chapters_plan['book_title']
        chapter_title = chapter['title']
        chapter_period = chapter['period']
        chapter_keywords = ', '.join(chapter['keywords'])
        
        # 处理核心梗
        core_concept = chapter.get('core_concept', '')
        core_concept_section = f"- 核心梗：{core_concept}" if core_concept else ""
        
        # 处理内容导读
        content_guide = chapter.get('content_guide', '')
        content_guide_section = f"\n\n**内容导读：**\n{content_guide}" if content_guide else ""
        
        # 使用模板格式化
        prompt = template.format(
            book_title=book_title,
            chapter_title=chapter_title,
            chapter_period=chapter_period,
            chapter_keywords=chapter_keywords,
            core_concept_section=core_concept_section,
            content_guide_section=content_guide_section
        )
        
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用 DeepSeek API 生成内容。
        
        参数:
            prompt: 发送给 API 的提示词
            
        返回:
            生成的内容字符串
        """
        api_config = self.config["deepseek_api"]
        gen_settings = self.config["generation_settings"]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": api_config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": self.chapters_plan["system_prompt"]
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": gen_settings["temperature"],
            "max_tokens": gen_settings["max_tokens"],
            "top_p": gen_settings["top_p"],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{api_config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _save_chapter(self, chapter: Dict, content: str) -> str:
        """
        将生成的章节保存到文件。
        
        参数:
            chapter: 章节信息字典
            content: 生成的内容
            
        返回:
            保存的文件路径
        """
        chapters_dir = Path(self.config["output"]["chapters_dir"])
        chapter_dir = chapters_dir / f"chapter_{chapter['id']:02d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        # Create images directory if images are enabled
        if self.config.get("images", {}).get("enabled", False):
            images_dir = chapter_dir / self.config["images"]["image_dir"]
            images_dir.mkdir(parents=True, exist_ok=True)
        
        readme_path = chapter_dir / self.config["output"]["readme_filename"]
        
        # Add metadata header
        metadata = f"""---
chapter: {chapter['id']}
title: {chapter['title']}
period: {chapter['period']}
generated_at: {datetime.now().isoformat()}
---

"""
        
        full_content = metadata + content
        
        with open(readme_path, 'w', encoding=self.config["output"]["encoding"]) as f:
            f.write(full_content)
        
        return str(readme_path)
    
    def _process_images(self, chapter: Dict, content: str, chapter_dir: Path) -> str:
        """
        使用百度图片搜索处理生成内容中的图像。
        
        支持格式:
            - Markdown: ![description](images/path.jpg)
        
        参数:
            chapter: 章节信息字典
            content: 生成的内容
            chapter_dir: 章节目录路径
            
        返回:
            已处理的内容（替换了图像URL）
        """
        if not extract_image_placeholders or not BaiduImageSearcher:
            return content
        
        placeholders = extract_image_placeholders(content)
        if not placeholders:
            return content
        
        image_config = self.config.get("images", {})
        if not image_config.get("enabled", False):
            return content
        
        print(f"   找到 {len(placeholders)} 个图片占位符")
        
        if image_config.get("enabled", True) and image_config.get("search_source") == "baidu":
            searcher = BaiduImageSearcher()
            images_dir = image_config.get("image_dir", "images")
            
            # 按占位符的 index 顺序排序，确保按正文中的先后顺序处理
            placeholders_sorted = sorted(placeholders, key=lambda x: x["index"])
            
            print(f"   按顺序处理图片占位符...")
            
            for i, placeholder in enumerate(placeholders_sorted, 1):
                print(f"\n   [{i}/{len(placeholders_sorted)}] 处理第 {placeholder['index']} 个图片占位符")
                
                # 直接使用占位符中的关键字进行搜索
                search_keyword = placeholder.get("keyword", "").strip()
                
                if not search_keyword:
                    # 如果没有关键字，尝试使用章节关键词
                    chapter_keywords = chapter.get("keywords", [])
                    if chapter_keywords:
                        keyword_index = (placeholder["index"] - 1) % len(chapter_keywords)
                        search_keyword = chapter_keywords[keyword_index]
                    else:
                        search_keyword = "历史"
                
                print(f"      搜索关键词: {search_keyword} (占位符: {placeholder['path']})")
                
                # 搜索图片URL（不下载，只获取URL）
                image_url = searcher.search_and_get_url(search_keyword)
                
                if image_url:
                    # 替换占位符为实际图片URL（使用Markdown格式）
                    old_placeholder = placeholder["path"]
                    # 将 __关键字__ 替换为 ![关键字](图片URL)
                    new_markdown = f"![{search_keyword}]({image_url})"
                    content = content.replace(old_placeholder, new_markdown, 1)  # 只替换第一个匹配项
                    
                    print(f"      ✅ 已替换: {old_placeholder} -> {image_url[:80]}...")
                else:
                    # 如果搜索失败，保留原始占位符
                    print(f"      ⚠️  未找到图片，保留占位符: {search_keyword}")
            
            print(f"\n   ✅ 图片处理完成，共处理 {len(placeholders_sorted)} 个占位符")
        else:
            # Convert https://images/xxx.jpg to images/xxx.jpg format
            import re
            url_pattern = r'https://images/([^\s\n]+\.(jpg|jpeg|png|gif|webp))'
            def replace_url(match):
                filename = match.group(1)
                return f"{image_config.get('image_dir', 'images')}/{filename}"
            content = re.sub(url_pattern, replace_url, content, flags=re.IGNORECASE)
            print(f"   ℹ️  Image placeholders converted to local paths. You can add images manually to {chapter_dir / image_config.get('image_dir', 'images')}")
        
        return content
    
    def generate_next_chapter(self) -> bool:
        """
        按顺序生成下一章。
        
        返回:
            如果生成了章节则返回 True，如果所有章节都已完成则返回 False
        """
        chapter = self._get_next_chapter_to_generate()
        
        if chapter is None:
            print("✅ All chapters have been generated!")
            return False
        
        print(f"📝 Generating Chapter {chapter['id']}: {chapter['title']}")
        print(f"   Period: {chapter['period']}")
        
        # Create prompt
        prompt = self._create_chapter_prompt(chapter)
        
        # Call API
        print("   Calling DeepSeek API...")
        try:
            content = self._call_deepseek_api(prompt)
        except Exception as e:
            print(f"❌ Error generating chapter: {str(e)}")
            return False
        
        # Process images first (may modify content)
        processed_content = content
        if self.config.get("images", {}).get("enabled", False):
            print("   Processing images...")
            chapter_dir = Path(self.config["output"]["chapters_dir"]) / f"chapter_{chapter['id']:02d}"
            processed_content = self._process_images(chapter, content, chapter_dir)
        
        # Save chapter
        print("   Saving chapter...")
        file_path = self._save_chapter(chapter, processed_content)
        
        print(f"✅ Chapter {chapter['id']} generated successfully!")
        print(f"   Saved to: {file_path}")
        
        return True
    
    def generate_specific_chapter(self, chapter_id: int) -> bool:
        """
        按ID生成指定章节。
        
        参数:
            chapter_id: 要生成的章节ID
            
        返回:
            如果成功则返回 True，否则返回 False
        """
        chapter = None
        for ch in self.chapters_plan["chapters"]:
            if ch["id"] == chapter_id:
                chapter = ch
                break
        
        if chapter is None:
            print(f"❌ Chapter {chapter_id} not found in plan!")
            return False
        
        print(f"📝 Generating Chapter {chapter['id']}: {chapter['title']}")
        print(f"   Period: {chapter['period']}")
        
        # Create prompt
        prompt = self._create_chapter_prompt(chapter)
        
        # Call API
        print("   Calling DeepSeek API...")
        try:
            content = self._call_deepseek_api(prompt)
        except Exception as e:
            print(f"❌ Error generating chapter: {str(e)}")
            return False
        
        # Process images first (may modify content)
        processed_content = content
        if self.config.get("images", {}).get("enabled", False):
            print("   Processing images...")
            chapter_dir = Path(self.config["output"]["chapters_dir"]) / f"chapter_{chapter['id']:02d}"
            processed_content = self._process_images(chapter, content, chapter_dir)
        
        # Save chapter
        print("   Saving chapter...")
        file_path = self._save_chapter(chapter, processed_content)
        
        print(f"✅ Chapter {chapter['id']} generated successfully!")
        print(f"   Saved to: {file_path}")
        
        return True


def main():
    """脚本的主入口点。"""
    print("=" * 60)
    print("📚 从春秋到民国 - Chapter Generator")
    print("=" * 60)
    print()
    
    # Load .env file at the start
    load_env_file()
    
    try:
        generator = ChapterGenerator()
        
        # Check if specific chapter ID is provided
        if len(sys.argv) > 1:
            try:
                chapter_id = int(sys.argv[1])
                generator.generate_specific_chapter(chapter_id)
            except ValueError:
                print("❌ Invalid chapter ID. Please provide a number.")
                sys.exit(1)
        else:
            # Generate next chapter in sequence
            generator.generate_next_chapter()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


