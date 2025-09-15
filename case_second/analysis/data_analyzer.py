import pandas as pd
import numpy as np
import json
import os

class SecondDataAnalyzer:
    def __init__(self):
        self.case1_voltage_data = None
        self.case1_solar_data = None
        self.case2_voltage_data = None
        self.case2_ess_data = None
        self.case2_solar_data = None

    def load_data(self):
        """모든 시나리오 데이터 로드"""
        try:
            # Case 1 데이터
            self.case1_voltage_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/case_second/data/case1/voltage_data.csv')
            self.case1_solar_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/case_second/data/case1/pv_output_data.csv')

            # Case 2 데이터
            self.case2_voltage_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/case_second/data/case2/voltage_data.csv')
            self.case2_ess_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/case_second/data/case2/ess_output_data.csv')
            self.case2_solar_data = pd.read_csv('/Users/seokjaehong/work/cosim-paper/case_second/data/case2/pv_output_data.csv')

            print("✅ 모든 데이터 로드 완료")
            return True
        except FileNotFoundError as e:
            print(f"❌ 데이터 파일을 찾을 수 없습니다: {e}")
            return False

    def calculate_metrics(self):
        """지표 계산"""
        if self.case1_voltage_data is None:
            print("❌ 데이터를 먼저 로드하세요")
            return

        metrics = {}

        # Case 1 (ESS 없음) 지표 - 여러 버스 분석 (말단 버스 680 중심)
        if 'bus680_magnitude' in self.case1_voltage_data.columns:
            case1_voltages = self.case1_voltage_data['bus680_magnitude']  # 말단 버스 680
        else:
            case1_voltages = self.case1_voltage_data['bus650_magnitude']  # 백업: 변전소 버스 650
            
        metrics['case1'] = {
            'voltage_max': case1_voltages.max(),
            'voltage_min': case1_voltages.min(),
            'voltage_mean': case1_voltages.mean(),
            'voltage_std': case1_voltages.std(),
            'voltage_range': case1_voltages.max() - case1_voltages.min(),
            'overvoltage_count': (case1_voltages > 1.05).sum(),
            'undervoltage_count': (case1_voltages < 0.95).sum()
        }

        # Case 2 (ESS 있음) 지표 - 여러 버스 분석 (말단 버스 680 중심)
        if self.case2_voltage_data is not None:
            if 'bus680_magnitude' in self.case2_voltage_data.columns:
                case2_voltages = self.case2_voltage_data['bus680_magnitude']  # 말단 버스 680
            else:
                case2_voltages = self.case2_voltage_data['bus650_magnitude']  # 백업: 변전소 버스 650
                
            metrics['case2'] = {
                'voltage_max': case2_voltages.max(),
                'voltage_min': case2_voltages.min(),
                'voltage_mean': case2_voltages.mean(),
                'voltage_std': case2_voltages.std(),
                'voltage_range': case2_voltages.max() - case2_voltages.min(),
                'overvoltage_count': (case2_voltages > 1.05).sum(),
                'undervoltage_count': (case2_voltages < 0.95).sum()
            }

            # ESS 관련 지표
            if self.case2_ess_data is not None:
                metrics['ess'] = {
                    'total_charge_energy': self.case2_ess_data[self.case2_ess_data['ess_output_kw'] < 0]['ess_output_kw'].abs().sum(),
                    'total_discharge_energy': self.case2_ess_data[self.case2_ess_data['ess_output_kw'] > 0]['ess_output_kw'].sum(),
                    'max_soc': self.case2_ess_data['soc'].max(),
                    'min_soc': self.case2_ess_data['soc'].min(),
                    'soc_utilization': self.case2_ess_data['soc'].max() - self.case2_ess_data['soc'].min()
                }

        # 개선 효과 계산
        if 'case2' in metrics:
            # 0으로 나누기 방지
            voltage_range_reduction = 0
            if metrics['case1']['voltage_range'] > 0:
                voltage_range_reduction = (metrics['case1']['voltage_range'] - metrics['case2']['voltage_range']) / metrics['case1']['voltage_range'] * 100
            
            std_reduction = 0
            if metrics['case1']['voltage_std'] > 0:
                std_reduction = (metrics['case1']['voltage_std'] - metrics['case2']['voltage_std']) / metrics['case1']['voltage_std'] * 100
            
            metrics['improvement'] = {
                'voltage_range_reduction': voltage_range_reduction,
                'std_reduction': std_reduction,
                'overvoltage_reduction': metrics['case1']['overvoltage_count'] - metrics['case2']['overvoltage_count'],
                'undervoltage_reduction': metrics['case1']['undervoltage_count'] - metrics['case2']['undervoltage_count']
            }

        return metrics

    def print_summary(self, metrics):
        """결과 요약 출력"""
        print("\n" + "="*80)
        print("📊 1초 단위 Co-Simulation 분석 결과 요약")
        print("="*80)

        print("\n🔹 Case 1 (ESS 없음) - 말단 버스 680")
        print(f"  전압 범위: {metrics['case1']['voltage_min']:.6f} ~ {metrics['case1']['voltage_max']:.6f} pu")
        print(f"  전압 변동폭: {metrics['case1']['voltage_range']:.6f} pu")
        print(f"  전압 표준편차: {metrics['case1']['voltage_std']:.6f}")
        print(f"  과전압 발생 횟수: {metrics['case1']['overvoltage_count']}회")
        print(f"  저전압 발생 횟수: {metrics['case1']['undervoltage_count']}회")

        if 'case2' in metrics:
            print("\n🔹 Case 2 (ESS 있음) - 말단 버스 680")
            print(f"  전압 범위: {metrics['case2']['voltage_min']:.6f} ~ {metrics['case2']['voltage_max']:.6f} pu")
            print(f"  전압 변동폭: {metrics['case2']['voltage_range']:.6f} pu")
            print(f"  전압 표준편차: {metrics['case2']['voltage_std']:.6f}")
            print(f"  과전압 발생 횟수: {metrics['case2']['overvoltage_count']}회")
            print(f"  저전압 발생 횟수: {metrics['case2']['undervoltage_count']}회")

            if 'ess' in metrics:
                print("\n🔋 ESS 운영 결과")
                print(f"  총 충전량: {metrics['ess']['total_charge_energy']:.1f} kWh")
                print(f"  총 방전량: {metrics['ess']['total_discharge_energy']:.1f} kWh")
                print(f"  SOC 범위: {metrics['ess']['min_soc']:.1%} ~ {metrics['ess']['max_soc']:.1%}")
                print(f"  SOC 활용도: {metrics['ess']['soc_utilization']:.1%}")

            if 'improvement' in metrics:
                print("\n📈 ESS 도입 효과")
                print(f"  전압 변동폭: Case1 {metrics['case1']['voltage_range']:.6f} → Case2 {metrics['case2']['voltage_range']:.6f} pu")
                print(f"  전압 표준편차: Case1 {metrics['case1']['voltage_std']:.6f} → Case2 {metrics['case2']['voltage_std']:.6f} pu")
                print(f"  전압 안정화 효과: {metrics['improvement']['voltage_range_reduction']:.1f}% (변동폭 감소)")
                print(f"  전압 일정성 향상: {metrics['improvement']['std_reduction']:.1f}% (표준편차 감소)")
                print(f"  과전압 발생 감소: {metrics['improvement']['overvoltage_reduction']}회")
                print(f"  저전압 발생 감소: {metrics['improvement']['undervoltage_reduction']}회")

        print("="*80)

    def save_metrics(self, metrics):
        """지표를 JSON 파일로 저장"""
        with open('/Users/seokjaehong/work/cosim-paper/case_second/analysis/metrics_summary.json', 'w') as f:
            # numpy 타입을 일반 Python 타입으로 변환
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj

            def deep_convert(obj):
                if isinstance(obj, dict):
                    return {key: deep_convert(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [deep_convert(item) for item in obj]
                else:
                    return convert_numpy(obj)

            json.dump(deep_convert(metrics), f, indent=2)
        print("📁 분석 결과가 metrics_summary.json에 저장되었습니다.")

    def run_analysis(self):
        """전체 분석 실행"""
        if not self.load_data():
            return
        
        metrics = self.calculate_metrics()
        self.print_summary(metrics)
        self.save_metrics(metrics)

if __name__ == "__main__":
    analyzer = SecondDataAnalyzer()
    analyzer.run_analysis()
