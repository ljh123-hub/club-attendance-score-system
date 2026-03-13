# score_calculator.py
# 社团考勤分数计算模块

class ScoreCalculator:
    def __init__(self):
        self.members = {}
    
    def add_member(self, name, student_id):
        """添加新成员，初始分39分"""
        self.members[student_id] = {
            'name': name,
            'base_score': 39,
            'records': [],
            'current_score': 39,
            'cancel_reward': False  # 是否取消兑换资格
        }
        print(f"已添加成员：{name}，初始分39分")
    
    def add_record(self, student_id, event_type, points, reason):
        """添加一条加分/扣分记录
        event_type: 'add' 加分, 'subtract' 扣分
        """
        if student_id not in self.members:
            print(f"错误：成员 {student_id} 不存在")
            return
        
        member = self.members[student_id]
        current = member['current_score']
        
        # 特殊规则：如果分数>39且要扣分，先重置为39再扣
        if current > 39 and event_type == 'subtract':
            print(f"⚠️ 特殊规则：{member['name']} 分数{current}>39，先重置为39再扣分")
            member['current_score'] = 39
            member['cancel_reward'] = True  # 取消兑换资格
            current = 39
        
        # 记录事件
        record = {
            'type': event_type,
            'points': points,
            'reason': reason
        }
        member['records'].append(record)
        
        # 更新分数
        if event_type == 'add':
            member['current_score'] += points
            print(f"{member['name']} 加分 {points} 分，原因：{reason}")
        else:
            member['current_score'] -= points
            print(f"{member['name']} 扣分 {points} 分，原因：{reason}")
        
        print(f"{member['name']} 当前分数：{member['current_score']}")
        
        # 检查警告
        self.check_warning(student_id)
    
    def check_warning(self, student_id):
        """检查是否需要警告或劝退"""
        member = self.members[student_id]
        score = member['current_score']
        if score < 20:
            print(f"⚠️ 警告：{member['name']} 分数低于20分，建议劝退！")
        elif score < 30:
            print(f"⚠️ 提醒：{member['name']} 分数低于30分，需要写1000字反思报告")
    
    def calculate_reward(self, student_id):
        """计算可兑换积分"""
        member = self.members[student_id]
        score = member['current_score']
        
        if member['cancel_reward']:
            return f"{member['name']} 本学期已取消兑换资格"
        
        extra = score - 39
        if extra <= 0:
            return f"{member['name']} 无可兑换积分"
        
        # 根据分数返回可兑换金额
        if extra >= 60:
            money = 500
        elif extra >= 50:
            money = 300
        elif extra >= 40:
            money = 200
        elif extra >= 20:
            money = 100
        elif extra >= 10:
            money = 50
        else:
            money = 0
        
        return f"{member['name']} 可兑换积分：{extra}分，对应{ money }元红包"
    
    def export_to_excel(self, filename):
        """导出数据到Excel（需要安装pandas和openpyxl）"""
        try:
            import pandas as pd
            data = []
            for sid, info in self.members.items():
                data.append({
                    '学号': sid,
                    '姓名': info['name'],
                    '当前分数': info['current_score'],
                    '初始分': info['base_score'],
                    '超出积分': max(0, info['current_score'] - 39),
                    '取消资格': '是' if info['cancel_reward'] else '否'
                })
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            print(f"数据已导出到 {filename}")
        except ImportError:
            print("请安装pandas和openpyxl：pip install pandas openpyxl")


# 测试代码
if __name__ == "__main__":
    calculator = ScoreCalculator()
    
    # 添加测试成员
    calculator.add_member("张三", "2024001")
    calculator.add_member("李四", "2024002")
    
    # 测试加分
    calculator.add_record("2024001", "add", 5, "获得省一等奖")
    calculator.add_record("2024001", "add", 2, "做值日生")
    
    # 测试扣分
    calculator.add_record("2024002", "subtract", 10, "毁坏设备")
    
    # 测试超分后扣分
    calculator.add_record("2024001", "subtract", 3, "开会玩手机")
    
    # 计算奖励
    print("\n" + "="*30)
    print(calculator.calculate_reward("2024001"))
    print(calculator.calculate_reward("2024002"))
