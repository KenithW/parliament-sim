"""
Ollama 连接测试脚本
测试能否连接到远程 Ollama 服务
"""

import requests
import sys

def test_ollama_connection(base_url: str):
    """测试 Ollama 连接"""
    print(f"\n🔍 Testing Ollama connection: {base_url}")
    print("=" * 50)
    
    try:
        # 测试连接
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = data.get("models", [])
        
        print(f"\n✅ Connection successful!")
        print(f"\n📦 Available models ({len(models)}):")
        print("-" * 50)
        
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0)
            size_gb = round(size / (1024**3), 2) if size > 0 else "N/A"
            print(f"  • {name} ({size_gb} GB)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection failed!")
        print(f"   Cannot connect to {base_url}")
        print(f"\n   Possible issues:")
        print(f"   1. Check if the IP address is correct")
        print(f"   2. Ensure Ollama is running on the remote machine")
        print(f"   3. Check firewall settings (port 11434)")
        print(f"   4. Verify Docker port mapping: docker ps")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Connection timeout!")
        print(f"   The server at {base_url} didn't respond in 10 seconds")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    print("\n🦙 Ollama Connection Tester")
    print("=" * 50)
    
    # 测试配置
    test_configs = [
        ("Local (localhost)", "http://localhost:11434"),
        ("Remote (example)", "http://192.168.x.x:11434"),  # 修改为你的实际 IP
    ]
    
    results = {}
    
    for name, url in test_configs:
        if url == "http://192.168.x.x:11434":
            print(f"\n⏭️  Skipping {name} - please edit the IP address first")
            continue
        
        results[name] = test_ollama_connection(url)
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("-" * 50)
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    print("\n💡 To test remote connection:")
    print(f"   1. Edit this script and change '192.168.x.x' to actual IP")
    print(f"   2. Run: python test_ollama_connection.py")
    print()


if __name__ == "__main__":
    main()
