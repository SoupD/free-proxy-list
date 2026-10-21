#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# 北京时间：中国全境统一 UTC+8，无夏令时，不依赖运行环境的系统时区
CST = timezone(timedelta(hours=8))


class ProxyListScraper:
    def __init__(self):
        self.url = "https://proxy-socks5.com/proxy_list"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_proxy_list(self):
        """抓取代理列表"""
        try:
            print(f"正在抓取代理列表: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table')
            if not table:
                print("未找到代理数据表格")
                return []

            proxies = []
            rows = table.find_all('tr')[1:]  # 跳过表头

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:  # 至少4列：协议、IP、端口、位置
                    protocol = cells[0].text.strip()
                    ip = cells[1].text.strip()
                    port = cells[2].text.strip()
                    # len(cells) >= 4 已保证有第4列，这个兜底其实永不触发
                    location = cells[3].text.strip()

                    # 清理位置信息中的多余文本
                    location = location.replace('已复制', '').replace('复制', '').strip()
                    location = ' '.join(location.split()) or '未知'

                    if protocol and ip and port:
                        proxy = f"{protocol}://{ip}:{port} [{location}]"
                        proxies.append(proxy)

            print(f"成功抓取到 {len(proxies)} 个代理")
            return proxies

        except requests.RequestException as e:
            print(f"网络请求错误: {e}")
            return []
        except Exception as e:
            print(f"抓取错误: {e}")
            return []

    def save_to_file(self, proxies, filename='proxy.txt'):
        """保存代理列表到文件"""
        try:
            # 注意：这里必须是 utf-8，之前写成 utf+8 会直接报错
            with open(filename, 'w', encoding='utf-8') as f:
                now = datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"# 代理列表更新时间: {now} (UTC+8)\n")
                f.write(f"# 总计: {len(proxies)} 个代理\n\n")

                for proxy in proxies:
                    f.write(f"{proxy}\n")

            print(f"代理列表已保存到 {filename}")
            return True

        except OSError as e:
            print(f"保存文件错误: {e}")
            return False


def main():
    """主函数"""
    scraper = ProxyListScraper()

    proxies = scraper.scrape_proxy_list()

    if proxies:
        scraper.save_to_file(proxies)
        print("代理列表抓取完成！")
    else:
        print("未能获取到代理数据")


if __name__ == "__main__":
    main()
