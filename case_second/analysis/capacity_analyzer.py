import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt

class ESSCapacityAnalyzer:
    def __init__(self):
        self.scenarios = {
            'no_ess': {'name': 'ESS 없음', 'capacity': 0},
            '100kwh': {'name': 'ESS 100kWh', 'capacity': 100},
            '500kwh': {'name': 'ESS 500kWh', 'capacity': 500},
            '1000kwh': {'name': 'ESS 1000kWh', 'capacity': 1000},
            '2000kwh': {'name': 'ESS 2000kWh', 'capacity': 2000}
        }
        self.data = {}

    def load_all_data(self):
        """모든 시나리오 데이터 로드"""
        print("📊 모든 ESS 용량별 데이터 로드 중...")
        
        for scenario, info in self.scenarios.items():
            try:
                if scenario == 'no_ess':
                    voltage_file = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case1/voltage_data.csv'
                    ess_file = None
                else:
                    voltage_file = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case{scenario}/voltage_data.csv'
                    ess_file = f'/Users/seokjaehong/work/cosim-paper/case_second/data/case{scenario}/ess_output_data.csv'
                
                # 전압 데이터 로드
                voltage_data = pd.read_csv(voltage_file)
                
                # ESS 데이터 로드 (있는 경우)
                ess_data = None
                if ess_file and os.path.exists(ess_file):
                    ess_data = pd.read_csv(ess_file)
                
                self.data[scenario] = {
                    'voltage': voltage_data,
                    'ess': ess_data,
                    'capacity': info['capacity'],
                    'name': info['name']
                }
                
                print(f"✅ {info['name']} 데이터 로드 완료")
                
            except FileNotFoundError as e:
                print(f"❌ {info['name']} 데이터 파일을 찾을 수 없습니다: {e}")
                return False
        
        print("✅ 모든 데이터 로드 완료")
        return True

    def calculate_metrics(self):
        """각 시나리오별 지표 계산"""
        metrics = {}
        
        for scenario, data in self.data.items():
            voltage_data = data['voltage']
            ess_data = data['ess']
            
            # 말단 버스 680 전압 분석
            if 'bus680_magnitude' in voltage_data.columns:
                voltages = voltage_data['bus680_magnitude']
            else:
                voltages = voltage_data['bus650_magnitude']
            
            scenario_metrics = {
                'capacity': data['capacity'],
                'name': data['name'],
                'voltage_min': voltages.min(),
                'voltage_max': voltages.max(),
                'voltage_mean': voltages.mean(),
                'voltage_std': voltages.std(),
                'voltage_range': voltages.max() - voltages.min(),
                'overvoltage_count': (voltages > 1.05).sum(),
                'undervoltage_count': (voltages < 0.95).sum()
            }
            
            # ESS 관련 지표 (있는 경우)
            if ess_data is not None:
                scenario_metrics.update({
                    'total_charge_energy': ess_data[ess_data['ess_output_kw'] < 0]['ess_output_kw'].abs().sum(),
                    'total_discharge_energy': ess_data[ess_data['ess_output_kw'] > 0]['ess_output_kw'].sum(),
                    'max_soc': ess_data['soc'].max(),
                    'min_soc': ess_data['soc'].min(),
                    'soc_utilization': ess_data['soc'].max() - ess_data['soc'].min(),
                    'avg_ess_power': ess_data['ess_output_kw'].abs().mean()
                })
            
            metrics[scenario] = scenario_metrics
        
        return metrics

    def print_comparison(self, metrics):
        """ESS 용량별 비교 결과 출력"""
        print("\n" + "="*100)
        print("📊 ESS 용량별 전압 안정화 효과 비교")
        print("="*100)
        
        # 헤더
        print(f"{'시나리오':<15} {'용량(kWh)':<10} {'전압범위(pu)':<15} {'변동폭(pu)':<12} {'표준편차':<10} {'ESS활용도':<10}")
        print("-" * 100)
        
        # 각 시나리오별 결과
        for scenario in ['no_ess', '100kwh', '500kwh', '1000kwh', '2000kwh']:
            if scenario in metrics:
                m = metrics[scenario]
                voltage_range = f"{m['voltage_min']:.4f}~{m['voltage_max']:.4f}"
                voltage_std = f"{m['voltage_std']:.6f}"
                voltage_range_val = f"{m['voltage_range']:.6f}"
                
                if 'soc_utilization' in m:
                    soc_util = f"{m['soc_utilization']:.1%}"
                else:
                    soc_util = "N/A"
                
                print(f"{m['name']:<15} {m['capacity']:<10} {voltage_range:<15} {voltage_range_val:<12} {voltage_std:<10} {soc_util:<10}")
        
        print("\n" + "="*100)
        print("📈 ESS 용량별 효과 분석")
        print("="*100)
        
        # 기준 시나리오 (ESS 없음)
        baseline = metrics['no_ess']
        baseline_std = baseline['voltage_std']
        baseline_range = baseline['voltage_range']
        
        print(f"기준 (ESS 없음): 변동폭={baseline_range:.6f} pu, 표준편차={baseline_std:.6f}")
        print()
        
        # 각 ESS 시나리오와 비교
        for scenario in ['100kwh', '500kwh', '1000kwh', '2000kwh']:
            if scenario in metrics:
                m = metrics[scenario]
                std_improvement = ((baseline_std - m['voltage_std']) / baseline_std * 100) if baseline_std > 0 else 0
                range_improvement = ((baseline_range - m['voltage_range']) / baseline_range * 100) if baseline_range > 0 else 0
                
                print(f"{m['name']}:")
                print(f"  - 변동폭 개선: {range_improvement:.1f}% ({baseline_range:.6f} → {m['voltage_range']:.6f} pu)")
                print(f"  - 표준편차 개선: {std_improvement:.1f}% ({baseline_std:.6f} → {m['voltage_std']:.6f} pu)")
                
                if 'total_charge_energy' in m:
                    print(f"  - ESS 운영: 충전 {m['total_charge_energy']:.1f} kWh, 방전 {m['total_discharge_energy']:.1f} kWh")
                    print(f"  - SOC 활용도: {m['soc_utilization']:.1%}")
                print()

    def create_visualization(self, metrics):
        """시각화 생성"""
        try:
            import matplotlib.pyplot as plt
            
            # 데이터 준비
            capacities = []
            voltage_stds = []
            voltage_ranges = []
            names = []
            
            for scenario in ['no_ess', '100kwh', '500kwh', '1000kwh', '2000kwh']:
                if scenario in metrics:
                    m = metrics[scenario]
                    capacities.append(m['capacity'])
                    voltage_stds.append(m['voltage_std'])
                    voltage_ranges.append(m['voltage_range'])
                    names.append(m['name'])
            
            # 그래프 생성
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 전압 표준편차
            ax1.plot(capacities, voltage_stds, 'bo-', linewidth=2, markersize=8)
            ax1.set_xlabel('ESS 용량 (kWh)')
            ax1.set_ylabel('전압 표준편차 (pu)')
            ax1.set_title('ESS 용량별 전압 표준편차')
            ax1.grid(True, alpha=0.3)
            
            # 전압 변동폭
            ax2.plot(capacities, voltage_ranges, 'ro-', linewidth=2, markersize=8)
            ax2.set_xlabel('ESS 용량 (kWh)')
            ax2.set_ylabel('전압 변동폭 (pu)')
            ax2.set_title('ESS 용량별 전압 변동폭')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('/Users/seokjaehong/work/cosim-paper/case_second/analysis/ess_capacity_analysis.png', dpi=300, bbox_inches='tight')
            print("📊 시각화 저장: ess_capacity_analysis.png")
            
        except ImportError:
            print("⚠️ matplotlib이 설치되지 않아 시각화를 생성할 수 없습니다.")

    def save_results(self, metrics):
        """결과를 JSON 파일로 저장"""
        with open('/Users/seokjaehong/work/cosim-paper/case_second/analysis/capacity_analysis.json', 'w') as f:
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
        print("📁 분석 결과가 capacity_analysis.json에 저장되었습니다.")

    def run_analysis(self):
        """전체 분석 실행"""
        if not self.load_all_data():
            return
        
        metrics = self.calculate_metrics()
        self.print_comparison(metrics)
        self.create_visualization(metrics)
        self.save_results(metrics)

if __name__ == "__main__":
    analyzer = ESSCapacityAnalyzer()
    analyzer.run_analysis()
