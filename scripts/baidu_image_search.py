#!/usr/bin/env python3
"""
Baidu Image Search module for finding relevant images.
"""

import requests
import json
from typing import List, Dict, Optional
from pathlib import Path


class BaiduImageSearcher:
    """Handles image search from Baidu Image API."""
    
    def __init__(self):
        """Initialize the Baidu image searcher."""
        self.base_url = "https://image.baidu.com/search/acjson"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://image.baidu.com/",
            "X-Requested-With": "XMLHttpRequest"
        }
    
    def search(self, keyword: str, page: int = 0, per_page: int = 5) -> List[Dict]:
        """
        Search images from Baidu Image API.
        
        Args:
            keyword: Search keyword
            page: Page number (starts from 0)
            per_page: Number of images per page
            
        Returns:
            List of image dictionaries with url and description
        """
        try:
            # 直接使用原始关键词，不进行 URL encode
            params = {
                "tn": "resultjson_com",
                "word": keyword,
                "pn": 0,
                "rn": 5,
                "ie": "utf-8",
                "oe": "utf-8"
            }
            
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Baidu API returns JSON
            data = response.json()
            
            # Log the full data object
            print(f"\n   📋 图片搜索响应数据 (keyword: {keyword}):")
            print(f"   {json.dumps(data, ensure_ascii=False, indent=2)}")
            print()
            
            # Debug: check response structure
            if "data" not in data:
                print(f"   ⚠️  No 'data' field in response. Response keys: {list(data.keys())}")
                return []
            
            data_list = data.get("data", [])
            
            # 直接取第一项的 middleURL
            if not data_list or len(data_list) == 0:
                print(f"   ⚠️  No images found for keyword: {keyword}")
                return []
            
            first_item = data_list[0]
            if not first_item or not isinstance(first_item, dict):
                print(f"   ⚠️  Invalid first item for keyword: {keyword}")
                return []
            
            # 直接取 middleURL，不需要任何缺省逻辑
            middle_url = first_item.get("middleURL")
            
            if not middle_url:
                print(f"   ⚠️  No middleURL in first item for keyword: {keyword}")
                return []
            
            # 返回结果
            results = [{
                "url": middle_url,
                "description": first_item.get("fromPageTitleEnc", keyword),
                "width": first_item.get("width", 0),
                "height": first_item.get("height", 0),
                "type": first_item.get("type", "jpg"),
                "source": "baidu"
            }]
            
            print(f"   ✅ Found image URL for keyword: {keyword}")
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Network error searching for '{keyword}': {str(e)}")
            return []
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Invalid JSON response for '{keyword}': {str(e)}")
            return []
        except Exception as e:
            print(f"   ⚠️  Baidu image search failed for '{keyword}': {str(e)}")
            return []
    
    def download_image(self, image_url: str, save_path: Path) -> bool:
        """
        Download image from URL.
        
        Args:
            image_url: URL of the image
            save_path: Path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Some image URLs might need different headers
            download_headers = self.headers.copy()
            download_headers["Referer"] = "https://image.baidu.com/"
            
            response = requests.get(image_url, headers=download_headers, timeout=30, stream=True, allow_redirects=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get("Content-Type", "").lower()
            if not content_type.startswith("image/"):
                print(f"   ⚠️  URL does not point to an image (Content-Type: {content_type})")
                return False
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was written and has content
            if save_path.exists() and save_path.stat().st_size > 0:
                return True
            else:
                print(f"   ⚠️  Downloaded file is empty or does not exist")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Network error downloading image: {str(e)}")
            return False
        except Exception as e:
            print(f"   ⚠️  Failed to download image: {str(e)}")
            return False
    
    def search_and_get_url(self, keyword: str, page: int = 0, per_page: int = 5) -> Optional[str]:
        """
        Search for an image and return its URL directly (no download).
        
        Args:
            keyword: Search keyword
            page: Page number (starts from 0)
            per_page: Number of images per page
            
        Returns:
            Image URL if found, None otherwise
        """
        # Search for images
        images = self.search(keyword, page=page, per_page=per_page)
        
        if not images:
            print(f"   ⚠️  No images found for keyword: {keyword}")
            return None
        
        # Use the first result
        image = images[0]
        image_url = image.get("url")
        
        if image_url:
            print(f"   ✅ Found image URL for '{keyword}': {image_url[:80]}...")
            return image_url
        else:
            print(f"   ⚠️  No valid image URL found for keyword: {keyword}")
            return None


def extract_image_placeholders(content: str) -> List[Dict]:
    """
    从内容中提取图片占位符，按照在正文中出现的顺序。
    支持格式: __关键字__（前后各两个下划线）
    
    参数:
        content: 内容字符串
        
    返回:
        图片占位符字典列表（按出现顺序排序）
    """
    import re
    
    placeholders = []
    placeholder_positions = []  # 存储 (位置, 占位符信息) 的元组
    
    # Match placeholder format: __关键字__
    # 匹配前后各两个下划线，中间是关键字（可以包含中文、英文、数字、空格等）
    placeholder_pattern = r'__([^_]+)__'
    for match in re.finditer(placeholder_pattern, content):
        keyword = match.group(1).strip()
        if keyword:  # 确保关键字不为空
            placeholder_positions.append((match.start(), {
                "keyword": keyword,
                "path": match.group(0),  # 完整的占位符，如 __周天子东迁__
                "format": "placeholder"
            }))
    
    # 按位置排序，确保按照正文中出现的顺序
    placeholder_positions.sort(key=lambda x: x[0])
    
    # 添加 index 并构建最终列表
    for i, (pos, placeholder_info) in enumerate(placeholder_positions, 1):
        placeholder_info["index"] = i
        placeholders.append(placeholder_info)
    
    return placeholders

