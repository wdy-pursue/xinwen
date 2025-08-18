#!/usr/bin/env python3
"""
简单的微信公众号素材ID查看器
运行后会显示你素材库中的所有图片和缩略图的media_id
"""

import asyncio
import aiohttp
import json

async def get_wechat_materials(app_id, app_secret):
    """获取微信公众号素材库中的media_id"""

    # 1. 获取access_token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"

    async with aiohttp.ClientSession() as session:
        async with session.get(token_url) as response:
            # 先获取文本，再解析JSON
            response_text = await response.text()
            print(f"Token响应: {response_text}")

            try:
                token_result = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"❌ 无法解析token响应: {response_text}")
                return

        if 'access_token' not in token_result:
            print(f"获取token失败: {token_result}")
            return

        access_token = token_result['access_token']
        print(f"✅ 获取access_token成功")

        # 2. 获取缩略图素材（用于图文消息封面）
        print("\n🖼️  正在获取缩略图素材...")
        thumb_url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}"
        thumb_data = {"type": "thumb", "offset": 0, "count": 20}

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        async with session.post(thumb_url, json=thumb_data, headers=headers) as response:
            # 先获取文本，再解析JSON
            response_text = await response.text()
            print(f"缩略图响应状态: {response.status}")
            print(f"缩略图响应: {response_text[:200]}...")  # 只显示前200字符

            try:
                thumb_result = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"❌ 无法解析缩略图响应: {response_text}")
                return

        # 检查错误码
        if 'errcode' in thumb_result and thumb_result['errcode'] != 0:
            error_msg = get_error_message(thumb_result['errcode'])
            print(f"❌ 获取缩略图失败: {thumb_result['errcode']} - {error_msg}")
        elif 'item' in thumb_result:
            print(f"找到 {len(thumb_result['item'])} 个缩略图素材：")
            for i, item in enumerate(thumb_result['item'], 1):
                name = item.get('name', '未命名')
                media_id = item['media_id']
                print(f"  {i}. {name}")
                print(f"     📱 Media ID: {media_id}")
                print()
        else:
            print(f"❌ 没有找到缩略图素材，响应: {thumb_result}")

        # 3. 获取图片素材
        print("\n🎨 正在获取图片素材...")
        image_data = {"type": "image", "offset": 0, "count": 20}

        async with session.post(thumb_url, json=image_data, headers=headers) as response:
            # 先获取文本，再解析JSON
            response_text = await response.text()
            print(f"图片响应状态: {response.status}")
            print(f"图片响应: {response_text[:200]}...")  # 只显示前200字符

            try:
                image_result = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"❌ 无法解析图片响应: {response_text}")
                return

        # 检查错误码
        if 'errcode' in image_result and image_result['errcode'] != 0:
            error_msg = get_error_message(image_result['errcode'])
            print(f"❌ 获取图片失败: {image_result['errcode']} - {error_msg}")
        elif 'item' in image_result:
            print(f"找到 {len(image_result['item'])} 个图片素材：")
            for i, item in enumerate(image_result['item'], 1):
                name = item.get('name', '未命名')
                media_id = item['media_id']
                url = item.get('url', '')
                print(f"  {i}. {name}")
                print(f"     📱 Media ID: {media_id}")
                if url:
                    print(f"     🔗 URL: {url}")
                print()
        else:
            print(f"❌ 没有找到图片素材，响应: {image_result}")


def get_error_message(errcode: int) -> str:
    """获取微信API错误码对应的错误信息"""
    error_codes = {
        -1: "系统繁忙，此时请开发者稍候再试",
        0: "请求成功",
        40001: "AppSecret错误或者AppSecret不属于这个公众号",
        40013: "不合法的AppID",
        40014: "不合法的access_token",
        41001: "缺少access_token参数",
        42001: "access_token超时",
        43002: "需要POST请求",
        44002: "POST的数据包为空",
        47001: "解析JSON/XML内容错误",
        48001: "api功能未授权",
        50001: "用户未授权该api",
        61023: "素材不存在",
        61024: "账号未开通此功能",
    }
    return error_codes.get(errcode, f"未知错误码: {errcode}")

def main():
    """主函数"""
    print("=== 微信公众号素材ID查看器 ===\n")

    # 在这里填入你的公众号信息
    APP_ID = input("请输入你的AppID: ").strip()
    APP_SECRET = input("请输入你的AppSecret: ").strip()

    if not APP_ID or not APP_SECRET:
        print("❌ AppID和AppSecret不能为空！")
        return

    print(f"\n🔄 开始获取素材列表...")

    try:
        asyncio.run(get_wechat_materials(APP_ID, APP_SECRET))
    except Exception as e:
        print(f"❌ 发生错误: {e}")

    print("\n✨ 完成！你可以复制上面显示的Media ID用于发布文章。")
    print("💡 提示：用于图文消息封面的应该使用缩略图素材的Media ID")

if __name__ == "__main__":
    main()