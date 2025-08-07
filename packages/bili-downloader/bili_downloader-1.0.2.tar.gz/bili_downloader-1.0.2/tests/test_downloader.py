#!/usr/bin/env python3
"""
BiliDownloader测试文件
测试各个模块的功能
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.extractor import BilibiliExtractor
from src.downloader import VideoDownloader
from src.converter import VideoConverter
from src.utils import (
    sanitize_filename, 
    format_bytes, 
    format_duration,
    is_bilibili_url, 
    extract_video_id_from_url,
    validate_url
)


class TestBilibiliExtractor(unittest.TestCase):
    """测试Bilibili信息提取器"""
    
    def setUp(self):
        self.extractor = BilibiliExtractor()
    
    def test_extract_bv_from_url(self):
        """测试从URL提取BV号"""
        test_cases = [
            ("https://www.bilibili.com/video/BV1234567890", "BV1234567890"),
            ("https://bilibili.com/video/av12345", "av12345"),
            ("invalid_url", None)
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.extractor.extract_bv_from_url(url)
                self.assertEqual(result, expected)


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_sanitize_filename(self):
        """测试文件名清理"""
        test_cases = [
            ("测试视频<>", "测试视频__"),
            ("normal_filename.mp4", "normal_filename.mp4"),
            ("file:with|illegal*chars", "file_with_illegal_chars"),
            ("", "")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_format_bytes(self):
        """测试字节格式化"""
        test_cases = [
            (1024, "1.0 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (500, "500.0 B")
        ]
        
        for bytes_count, expected in test_cases:
            with self.subTest(bytes=bytes_count):
                result = format_bytes(bytes_count)
                self.assertEqual(result, expected)
    
    def test_format_duration(self):
        """测试时长格式化"""
        test_cases = [
            (3661, "01:01:01"),  # 1小时1分1秒
            (125, "02:05"),      # 2分5秒
            (59, "00:59")        # 59秒
        ]
        
        for seconds, expected in test_cases:
            with self.subTest(seconds=seconds):
                result = format_duration(seconds)
                self.assertEqual(result, expected)
    
    def test_is_bilibili_url(self):
        """测试B站URL验证"""
        test_cases = [
            ("https://www.bilibili.com/video/BV1234567890", True),
            ("https://bilibili.com/video/av12345", True),
            ("https://b23.tv/abc123", True),
            ("https://youtube.com/watch?v=abc", False),
            ("invalid_url", False)
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = is_bilibili_url(url)
                self.assertEqual(result, expected)
    
    def test_extract_video_id_from_url(self):
        """测试从URL提取视频ID"""
        test_cases = [
            ("https://www.bilibili.com/video/BV1234567890", "BV1234567890"),
            ("https://bilibili.com/video/av12345", "12345"),
            ("invalid_url", None)
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = extract_video_id_from_url(url)
                self.assertEqual(result, expected)
    
    def test_validate_url(self):
        """测试URL验证"""
        test_cases = [
            ("https://www.example.com", True),
            ("http://test.com", True),
            ("ftp://files.example.com", True),
            ("invalid_url", False),
            ("", False)
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = validate_url(url)
                self.assertEqual(result, expected)


class TestVideoDownloader(unittest.TestCase):
    """测试视频下载器"""
    
    def setUp(self):
        self.downloader = VideoDownloader()
    
    @patch('requests.Session.head')
    def test_get_file_info(self, mock_head):
        """测试获取文件信息"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Length': '1048576',
            'Accept-Ranges': 'bytes',
            'Content-Type': 'video/mp4'
        }
        mock_head.return_value = mock_response
        
        info = self.downloader.get_file_info("http://example.com/test.mp4")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['size'], 1048576)
        self.assertTrue(info['supports_range'])
        self.assertEqual(info['content_type'], 'video/mp4')


class TestVideoConverter(unittest.TestCase):
    """测试视频转换器"""
    
    def setUp(self):
        self.converter = VideoConverter()
    
    @patch('subprocess.run')
    def test_check_ffmpeg(self, mock_run):
        """测试FFmpeg检查"""
        # 模拟FFmpeg可用
        mock_run.return_value.returncode = 0
        self.assertTrue(self.converter.check_ffmpeg())
        
        # 模拟FFmpeg不可用
        mock_run.return_value.returncode = 1
        self.assertFalse(self.converter.check_ffmpeg())


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestBilibiliExtractor,
        TestUtils,
        TestVideoDownloader,
        TestVideoConverter
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestClass(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("运行BiliDownloader测试...")
    success = run_tests()
    
    if success:
        print("\n✓ 所有测试通过!")
        sys.exit(0)
    else:
        print("\n✗ 测试失败!")
        sys.exit(1)