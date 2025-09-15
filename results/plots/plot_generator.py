import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

# 한글 폰트 설정
plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8')

class PlotGenerator:
    def __init__(self):
        self.case1_voltage_data = None
        self.case2_voltage_data = None
        self.case2_ess_data = None
        self.case1_solar_data = None
        self.case2_solar_data = None

    def load_data(self):
        """데이터 로드"""
        try:
            self.case1_voltage_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/results/data/voltage_case1_data.csv')
            self.case1_solar_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/results/data/solar_case1_data.csv')

            # Case 2 데이터가 있는 경우만 로드
            try:
                self.case2_voltage_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/results/data/voltage_case2_data.csv')
                self.case2_ess_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/results/data/ess_case2_data.csv')
                self.case2_solar_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/results/data/solar_case2_data.csv')
            except FileNotFoundError:
                print("⚠️  Case 2 데이터가 없습니다. Case 1만 분석합니다.")

            return True
        except FileNotFoundError as e:
            print(f"❌ 필수 데이터 파일을 찾을 수 없습니다: {e}")
            return False

    def plot_solar_profile(self):
        """태양광 출력 프로파일 그래프"""
        fig, ax = plt.subplots(figsize=(12, 6))

        if self.case1_solar_data is not None:
            ax.plot(self.case1_solar_data['time'], self.case1_solar_data['pv_output'],
                   'b-', linewidth=2, label='태양광 출력', marker='o', markersize=4)

        ax.set_xlabel('시간 (h)', fontsize=12)
        ax.set_ylabel('PV 출력 (kW)', fontsize=12)
        ax.set_title('24시간 태양광 발전 프로파일', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        ax.set_xlim(0, 23)

        # 시간대별 배경색 (낮/밤 구분)
        ax.axvspan(6, 18, alpha=0.1, color='yellow', label='주간')
        ax.axvspan(18, 24, alpha=0.1, color='navy', label='야간')
        ax.axvspan(0, 6, alpha=0.1, color='navy')

        plt.tight_layout()
        plt.savefig('/Users/seokjaehong/work/cosim-paper/results/plots/solar_profile.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_voltage_comparison(self):
        """전압 비교 그래프 (Case 1 vs Case 2)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 상단: 전압 프로파일 비교
        if self.case1_voltage_data is not None:
            ax1.plot(self.case1_voltage_data['time'], self.case1_voltage_data['bus650_voltage_pu'],
                    'r-', linewidth=2, label='Case 1: ESS 없음', marker='s', markersize=3)

        if self.case2_voltage_data is not None:
            ax1.plot(self.case2_voltage_data['time'], self.case2_voltage_data['bus650_voltage_pu'],
                    'g-', linewidth=2, label='Case 2: ESS 있음', marker='o', markersize=3)

        # 전압 허용 범위 표시
        ax1.axhline(y=1.05, color='orange', linestyle='--', alpha=0.7, label='과전압 기준 (1.05 pu)')
        ax1.axhline(y=0.95, color='orange', linestyle='--', alpha=0.7, label='저전압 기준 (0.95 pu)')
        ax1.axhline(y=1.0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)

        ax1.set_xlabel('시간 (h)', fontsize=12)
        ax1.set_ylabel('Bus 650 전압 (pu)', fontsize=12)
        ax1.set_title('Bus 650 전압 프로파일 비교', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        ax1.set_xlim(0, 23)

        # 하단: ESS 운영 현황 (Case 2가 있는 경우)
        if self.case2_ess_data is not None:
            # ESS 출력
            ax2_ess = ax2.twinx()
            ax2.bar(self.case2_ess_data['time'], self.case2_ess_data['ess_output'],
                   alpha=0.6, color='blue', label='ESS 출력 (kW)')

            # SOC
            ax2_ess.plot(self.case2_ess_data['time'], self.case2_ess_data['soc']*100,
                        'purple', linewidth=2, marker='D', markersize=3, label='SOC (%)')

            ax2.set_xlabel('시간 (h)', fontsize=12)
            ax2.set_ylabel('ESS 출력 (kW)', fontsize=12)
            ax2_ess.set_ylabel('SOC (%)', fontsize=12)
            ax2.set_title('ESS 운영 현황 (Case 2)', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, 23)

            # 범례 결합
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_ess.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)

        plt.tight_layout()
        plt.savefig('/Users/seokjaehong/work/cosim-paper/results/plots/voltage_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_power_balance(self):
        """전력 수급 균형 그래프 (Case 2)"""
        if self.case2_voltage_data is None or self.case2_ess_data is None:
            print("⚠️  Case 2 데이터가 없어 전력 수급 그래프를 생성할 수 없습니다.")
            return

        fig, ax = plt.subplots(figsize=(12, 8))

        time = self.case2_voltage_data['time']
        pv_output = self.case2_voltage_data['pv_output']
        ess_output = self.case2_voltage_data['ess_output']
        net_power = self.case2_voltage_data['net_power']

        # 스택 바 차트로 전력 구성 표시
        ax.bar(time, pv_output, alpha=0.7, color='gold', label='PV 발전')

        # ESS 충전/방전 분리
        ess_charge = np.where(ess_output < 0, ess_output, 0)
        ess_discharge = np.where(ess_output > 0, ess_output, 0)

        ax.bar(time, ess_discharge, bottom=pv_output, alpha=0.7, color='blue', label='ESS 방전')
        ax.bar(time, ess_charge, alpha=0.7, color='red', label='ESS 충전')

        # 순 전력 라인
        ax.plot(time, net_power, 'k-', linewidth=3, label='순 주입 전력', marker='o', markersize=4)

        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)
        ax.set_xlabel('시간 (h)', fontsize=12)
        ax.set_ylabel('전력 (kW)', fontsize=12)
        ax.set_title('전력 수급 균형 (Case 2: ESS 있음)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        ax.set_xlim(0, 23)

        plt.tight_layout()
        plt.savefig('/Users/seokjaehong/work/cosim-paper/results/plots/power_balance.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_voltage_statistics(self):
        """전압 통계 비교 (박스플롯)"""
        if self.case2_voltage_data is None:
            print("⚠️  Case 2 데이터가 없어 비교 통계 그래프를 생성할 수 없습니다.")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # 박스플롯
        voltage_data = [
            self.case1_voltage_data['bus650_voltage_pu'],
            self.case2_voltage_data['bus650_voltage_pu']
        ]

        bp = ax1.boxplot(voltage_data, labels=['Case 1\n(ESS 없음)', 'Case 2\n(ESS 있음)'],
                        patch_artist=True, notch=True)

        # 색상 설정
        bp['boxes'][0].set_facecolor('lightcoral')
        bp['boxes'][1].set_facecolor('lightgreen')

        ax1.set_ylabel('Bus 650 전압 (pu)', fontsize=12)
        ax1.set_title('전압 분포 비교', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # 전압 허용 범위
        ax1.axhline(y=1.05, color='orange', linestyle='--', alpha=0.7)
        ax1.axhline(y=0.95, color='orange', linestyle='--', alpha=0.7)
        ax1.axhline(y=1.0, color='black', linestyle='-', alpha=0.5)

        # 히스토그램
        ax2.hist(self.case1_voltage_data['bus650_voltage_pu'], bins=15, alpha=0.6,
                color='red', label='Case 1 (ESS 없음)', density=True)
        ax2.hist(self.case2_voltage_data['bus650_voltage_pu'], bins=15, alpha=0.6,
                color='green', label='Case 2 (ESS 있음)', density=True)

        ax2.set_xlabel('Bus 650 전압 (pu)', fontsize=12)
        ax2.set_ylabel('확률 밀도', fontsize=12)
        ax2.set_title('전압 분포 히스토그램', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/Users/seokjaehong/work/cosim-paper/results/plots/voltage_statistics.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_ess_soc_profile(self):
        """ESS SOC 프로파일"""
        if self.case2_ess_data is None:
            print("⚠️  ESS 데이터가 없어 SOC 그래프를 생성할 수 없습니다.")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        time = self.case2_ess_data['time']
        soc = self.case2_ess_data['soc'] * 100
        ess_output = self.case2_ess_data['ess_output']

        # SOC 프로파일
        ax1.plot(time, soc, 'purple', linewidth=3, marker='o', markersize=4, label='SOC')
        ax1.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='최대 SOC (90%)')
        ax1.axhline(y=10, color='blue', linestyle='--', alpha=0.7, label='최소 SOC (10%)')
        ax1.fill_between(time, 10, 90, alpha=0.1, color='gray', label='운영 범위')

        ax1.set_ylabel('SOC (%)', fontsize=12)
        ax1.set_title('ESS 충전상태 (SOC) 프로파일', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=11)
        ax1.set_xlim(0, 23)
        ax1.set_ylim(0, 100)

        # ESS 출력
        colors = ['red' if x < 0 else 'blue' if x > 0 else 'gray' for x in ess_output]
        ax2.bar(time, ess_output, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)

        ax2.set_xlabel('시간 (h)', fontsize=12)
        ax2.set_ylabel('ESS 출력 (kW)', fontsize=12)
        ax2.set_title('ESS 충방전 프로파일 (양수: 방전, 음수: 충전)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 23)

        # 범례
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='blue', alpha=0.7, label='방전'),
                          Patch(facecolor='red', alpha=0.7, label='충전'),
                          Patch(facecolor='gray', alpha=0.7, label='대기')]
        ax2.legend(handles=legend_elements, fontsize=11)

        plt.tight_layout()
        plt.savefig('/Users/seokjaehong/work/cosim-paper/results/plots/ess_soc_profile.png', dpi=300, bbox_inches='tight')
        plt.show()

    def generate_all_plots(self):
        """모든 그래프 생성"""
        print("📊 그래프 생성 시작...")

        if not self.load_data():
            return False

        try:
            print("1. 태양광 프로파일 생성...")
            self.plot_solar_profile()

            print("2. 전압 비교 그래프 생성...")
            self.plot_voltage_comparison()

            if self.case2_voltage_data is not None:
                print("3. 전력 수급 균형 그래프 생성...")
                self.plot_power_balance()

                print("4. 전압 통계 그래프 생성...")
                self.plot_voltage_statistics()

            if self.case2_ess_data is not None:
                print("5. ESS SOC 프로파일 생성...")
                self.plot_ess_soc_profile()

            print("✅ 모든 그래프 생성 완료!")
            print("📁 그래프는 results/plots/ 폴더에 저장되었습니다.")
            return True

        except Exception as e:
            print(f"❌ 그래프 생성 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    plotter = PlotGenerator()
    plotter.generate_all_plots()