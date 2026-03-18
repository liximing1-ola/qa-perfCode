import os
import time
import subprocess
import argparse


# 测试启动时间
# 创建App进程, 加载相关资源, 启动Main Thread, 初始化首屏Activity
class testPhoneTime:
    def __init__(self, device, pg_name, pga_name, wait_time=5):
        self.wait_time = wait_time  # 间隔时间
        self.device = device  # 设备序列号
        self.pg_name = pg_name  # 包名
        self.pga_name = pga_name  # activity名

    def startUpTime(self, iterations=30):  # 修改: 允许指定迭代次数
        try:
            su_time = []
            for i in range(iterations):
                # 改进: 使用subprocess并检查命令执行结果
                stop_cmd = f"adb -s {self.device} shell am force-stop {self.pg_name}"
                subprocess.run(stop_cmd.split(), check=True, capture_output=True)
                time.sleep(self.wait_time)

                start_cmd = f"adb -s {self.device} shell am start -W {self.pga_name}"
                result = subprocess.run(start_cmd.split(), capture_output=True, text=True)
                data = result.stdout.splitlines()

                total_time_found = False
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        # 改进: 更健壮的TotalTime解析
                        total_time_str = line.split(":")[1].strip()
                        try:
                            total_time = int(total_time_str)
                            print(f"第{i+1}次冷启动TotalTime为: {total_time}ms")
                            if total_time > 0:  # 忽略0值
                                su_time.append(total_time)
                            total_time_found = True
                        except ValueError:
                            print(f"无法解析TotalTime: {line}")
                if not total_time_found:
                    print(f"第{i+1}次冷启动未找到TotalTime")
                time.sleep(self.wait_time)
            return su_time
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e.stderr}")
            return []
        except Exception as error:
            print(f"冷启动测试错误: {error}")
            return []

    def startHotTime(self, iterations=30):  # 修改: 允许指定迭代次数
        try:
            # 先执行一次冷启动确保应用已加载
            self.startUpTime(iterations=1)

            hot_time = []
            for i in range(iterations):
                # 改进: 传递设备参数给keyEvent
                testPhoneTime.keyEvent(self.device, 3)  # Home键
                time.sleep(self.wait_time)

                start_cmd = f"adb -s {self.device} shell am start -W {self.pga_name}"
                result = subprocess.run(start_cmd.split(), capture_output=True, text=True)
                data = result.stdout.splitlines()

                total_time_found = False
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        total_time_str = line.split(":")[1].strip()
                        try:
                            total_time = int(total_time_str)
                            print(f"第{i+1}次热启动TotalTime为: {total_time}ms")
                            if total_time > 0:
                                hot_time.append(total_time)
                            total_time_found = True
                        except ValueError:
                            print(f"无法解析TotalTime: {line}")
                if not total_time_found:
                    print(f"第{i+1}次热启动未找到TotalTime")
                time.sleep(self.wait_time)
            return hot_time
        except Exception as error:
            print(f"热启动测试错误: {error}")
            return []

    @staticmethod
    def getDev():
        """
        :return: 获得设备信息 id，如果有多个设备，返回第一个在线设备；无设备返回None
        """
        try:
            # 改进: 使用subprocess并正确解析设备状态
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            data = result.stdout.splitlines()
            # 跳过标题行，检查在线设备
            for line in data[1:]:
                line = line.strip()
                if line.endswith('device'):  # 确保设备处于在线状态
                    return line.split('\t')[0]
            print("未找到在线设备")
            return None
        except subprocess.CalledProcessError as e:
            print(f"获取设备列表失败: {e.stderr}")
            return None
        except Exception as error:
            print(f"获取设备信息错误: {error}")
            return None

    @staticmethod
    def keyEvent(device, keycode):  # 修改: 增加device参数
        """
        :param device: 设备序列号
        :param keycode: key
        """
        # KEYCODE_HOME = 3
        # KEYCODE_BACK = 4
        cmd = f'adb -s {device} shell input keyevent {keycode}'
        subprocess.run(cmd.split(), capture_output=True)
        time.sleep(1)

    @staticmethod
    def save_results(mode, times, output_file):
        """保存测试结果到文件"""
        if not times:
            print("无测试数据可保存")
            return
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"{mode}启动测试结果\n")
                f.write(f"测试次数: {len(times)}\n")
                f.write(f"原始数据: {times}\n")
                f.write(f"最大值: {max(times)}ms\n")
                f.write(f"最小值: {min(times)}ms\n")
                # 移除最大最小值后计算平均值
                if len(times) > 2:
                    filtered = [t for t in times if t != max(times) and t != min(times)]
                    avg = sum(filtered) / len(filtered)
                    f.write(f"去极值后平均值: {avg:.2f}ms\n")
                else:
                    avg = sum(times) / len(times)
                    f.write(f"平均值: {avg:.2f}ms\n")
            print(f"结果已保存至: {output_file}")
        except Exception as e:
            print(f"保存结果失败: {e}")

    @staticmethod
    def main(mode, package_name, activity_name, iterations=30, output_file=None):
        device = testPhoneTime.getDev()
        if not device:
            raise Exception("未找到可用设备")

        print(f'设备id：{device}, APP包名：{package_name}, activity：{activity_name}')
        testTime = testPhoneTime(device, package_name, activity_name)

        if mode == 'cold':
            time_list = testTime.startUpTime(iterations)
        elif mode == 'hot':
            time_list = testTime.startHotTime(iterations)
        else:
            raise Exception('模式错误，只能是"cold"或"hot"')

        if not time_list:
            print("未获取到有效测试数据")
            return

        print(f"{mode}启动时间列表: {time_list}")
        print(f"max：{max(time_list)}ms")
        print(f"min：{min(time_list)}ms")

        # 计算平均值（移除最大最小值）
        if len(time_list) > 2:
            filtered = [t for t in time_list if t != max(time_list) and t != min(time_list)]
            avg_time = sum(filtered) / len(filtered)
            print(f"{mode}启动平均耗时(去极值): {avg_time:.2f}ms")
        else:
            avg_time = sum(time_list) / len(time_list)
            print(f"{mode}启动平均耗时: {avg_time:.2f}ms")

        # 保存结果
        if output_file:
            testPhoneTime.save_results(mode, time_list, output_file)


if __name__ == '__main__':
    # 新增: 命令行参数解析
    parser = argparse.ArgumentParser(description='APP启动时间测试工具')
    parser.add_argument('--mode', required=True, choices=['cold', 'hot'], help='测试模式: cold(冷启动)/hot(热启动)')
    parser.add_argument('--package', required=True, help='APP包名')
    parser.add_argument('--activity', required=True, help='APP主Activity')
    parser.add_argument('--iterations', type=int, default=30, help='测试次数，默认30次')
    parser.add_argument('--output', help='结果输出文件路径')
    args = parser.parse_args()

    testPhoneTime.main(
        mode=args.mode,
        package_name=args.package,
        activity_name=args.activity,
        iterations=args.iterations,
        output_file=args.output
    )

