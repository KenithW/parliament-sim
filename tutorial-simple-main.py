"""
main.py - 超简化版教学（兼容所有系统）
只保留核心逻辑，去掉 emoji 和中文字符
"""

# ============================================
# PART 1: 导入必要的库
# ============================================
import argparse        # 命令行参数解析
from datetime import datetime  # 时间戳


# ============================================
# PART 2: 定义一个简单的对话函数
# ============================================
def ask_llm(question, role):
    """
    向 LLM 提问
    
    Args:
        question: 问题内容
        role: 扮演什么角色（首相、反对党等）
    
    Returns:
        AI 的回答
    """
    from langchain_ollama import ChatOllama
    
    # 创建 LLM
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0.7
    )
    
    # 构造提示词
    prompt = f"""
You are a {role}. The debate topic is: "Should we increase NHS funding?"
Please give your short opinion (max 50 words) as a {role.lower()}.
"""
    
    # 发送请求
    response = llm.invoke(prompt)
    
    return response.content


# ============================================
# PART 3: 主程序入口
# ============================================
def main():
    # Step 1: 准备辩论数据
    print("=" * 60)
    print("UK Parliament Simulation (Simple Tutorial)")
    print("=" * 60)
    
    # 定义参与者
    participants = [
        {"name": "Speaker", "desc": "Presiding Officer"},
        {"name": "PM", "desc": "Prime Minister (Conservative)"},
        {"name": "LO", "desc": "Leader of Opposition (Labour)"},
        {"name": "Chancellor", "desc": "Chancellor of the Exchequer"},
        {"name": "Shadow Chancellor", "desc": "Shadow Chancellor"},
    ]
    
    topic = "Should we increase NHS funding?"
    
    print(f"\nTOPIC: {topic}")
    print(f"PARTICIPANTS: {len(participants)} people\n")
    
    # Step 2: 模拟辩论循环
    debate_records = []
    
    for i, person in enumerate(participants):
        print(f"[Round {i+1}] SPEAKER: {person['name']} ({person['desc']})")
        print("-" * 40)
        
        try:
            # 调用 LLM
            answer = ask_llm(topic, person['desc'])
            
            # 保存记录
            record = {
                "turn": i+1,
                "speaker": person['name'],
                "content": answer
            }
            debate_records.append(record)
            
            # 打印回答
            print(answer)
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    # Step 3: 总结
    print("=" * 60)
    print(f"DEBATE COMPLETE! Total rounds: {len(debate_records)}")
    print("=" * 60)
    
    # 保存到文件
    save_to_file(debate_records)


def save_to_file(records):
    """将记录保存到文件"""
    output_dir = "debates"
    
    # 创建目录（如果不存在）
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{timestamp}.txt"
    filepath = f"{output_dir}/{filename}"
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# UK Parliament Debate Record\n\n")
        
        for record in records:
            f.write(f"## Round {record['turn']}: {record['speaker']}\n\n")
            f.write(f"{record['content']}\n\n")
            f.write("---\n\n")
    
    print(f"RECORD SAVED TO: {filepath}")


# ============================================
# PART 4: 执行主程序
# ============================================
if __name__ == "__main__":
    main()
