import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

def analyze_voltage_data(case_name, data_dir):
    """전압 데이터 분석 함수 (1초 단위)"""
    try:
        # 전압 데이터 로드
        voltage_file = os.path.join(data_dir, 'voltage_data.csv')
        if not os.path.exists(voltage_file):
            print(f"❌ {case_name}: 전압 데이터 파일이 없습니다: {voltage_file}")
            return None

        voltage_df = pd.read_csv(voltage_file)
        print(f"✅ {case_name}: 전압 데이터 로드 완료 ({len(voltage_df)} 포인트)")

        # PV 데이터 로드 (있는 경우)
        pv_file = os.path.join(data_dir, 'pv_output_data.csv')
        pv_output = []
        if os.path.exists(pv_file):
            pv_df = pd.read_csv(pv_file)
            pv_output = pv_df['pv_output_kw'].tolist()

        # ESS 데이터 로드 (있는 경우)
        ess_file = os.path.join(data_dir, 'ess_output_data.csv')
        ess_output = []
        ess_soc = []
        if os.path.exists(ess_file):
            ess_df = pd.read_csv(ess_file)
            ess_output = ess_df['ess_output_kw'].tolist()
            ess_soc = ess_df['soc'].tolist()

        # 주요 버스들의 전압 분석
        buses = ['650', '680', '692']
        analysis_results = {}

        for bus in buses:
            magnitude_col = f'bus{bus}_magnitude'
            if magnitude_col in voltage_df.columns:
                voltages = voltage_df[magnitude_col].values

                # 기본 통계
                mean_voltage = np.mean(voltages)
                std_voltage = np.std(voltages)
                min_voltage = np.min(voltages)
                max_voltage = np.max(voltages)
                voltage_range = max_voltage - min_voltage

                # 전압 변동성 지표 (1초 단위 특화)
                # 1. 연속적인 전압 변화율
                voltage_changes = np.abs(np.diff(voltages))
                max_change_rate = np.max(voltage_changes) if len(voltage_changes) > 0 else 0
                avg_change_rate = np.mean(voltage_changes) if len(voltage_changes) > 0 else 0

                # 2. 전압 변동 빈도 (임계값 초과)
                change_threshold = 0.001  # 0.1% 변동
                significant_changes = np.sum(voltage_changes > change_threshold)
                change_frequency = significant_changes / len(voltages) * 100

                # 3. 전압 범위 위반 (±5% 범위)
                violations_high = np.sum(voltages > 1.05)
                violations_low = np.sum(voltages < 0.95)
                total_violations = violations_high + violations_low
                violation_rate = total_violations / len(voltages) * 100

                analysis_results[bus] = {
                    'mean_voltage': float(mean_voltage),
                    'std_voltage': float(std_voltage),
                    'min_voltage': float(min_voltage),
                    'max_voltage': float(max_voltage),
                    'voltage_range': float(voltage_range),
                    'max_change_rate': float(max_change_rate),
                    'avg_change_rate': float(avg_change_rate),
                    'change_frequency_percent': float(change_frequency),
                    'voltage_violations': int(total_violations),
                    'violation_rate_percent': float(violation_rate),
                    'data_points': len(voltages)
                }

                print(f"📊 {case_name} Bus{bus} 분석:")
                print(f"   - 평균 전압: {mean_voltage:.4f} pu")
                print(f"   - 표준편차: {std_voltage:.4f} pu")
                print(f"   - 전압 범위: {voltage_range:.4f} pu")
                print(f"   - 최대 변화율: {max_change_rate:.4f} pu/s")
                print(f"   - 평균 변화율: {avg_change_rate:.4f} pu/s")
                print(f"   - 유의한 변동 빈도: {change_frequency:.2f}%")
                print(f"   - 전압 위반: {total_violations}회 ({violation_rate:.2f}%)")

        return {
            'case_name': case_name,
            'bus_analysis': analysis_results,
            'pv_output': pv_output[:100] if pv_output else [],  # 처음 100개만 저장
            'ess_output': ess_output[:100] if ess_output else [],
            'ess_soc': ess_soc[:100] if ess_soc else [],
            'simulation_duration_seconds': len(voltage_df),
            'total_data_points': len(voltage_df)
        }

    except Exception as e:
        print(f"❌ {case_name} 분석 중 오류: {e}")
        return None

def create_comparison_plots(case1_data, case2_data, output_dir):
    """비교 플롯 생성 (1초 단위 특화)"""
    try:
        os.makedirs(output_dir, exist_ok=True)

        # 1. 전압 변동성 비교 (주요 지표)
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('전압 변동성 비교 (1초 단위 시뮬레이션)', fontsize=16)

        buses = ['650', '680', '692']

        # 표준편차 비교
        case1_std = [case1_data['bus_analysis'][bus]['std_voltage'] for bus in buses]
        case2_std = [case2_data['bus_analysis'][bus]['std_voltage'] for bus in buses if bus in case2_data['bus_analysis']]

        axes[0,0].bar(range(len(buses)), case1_std, alpha=0.7, label='Case 1 (태양광만)', color='orange')
        if case2_std:
            axes[0,0].bar([x+0.4 for x in range(len(case2_std))], case2_std, alpha=0.7, label='Case 2 (태양광+ESS)', color='green')
        axes[0,0].set_title('전압 표준편차 (변동성)')
        axes[0,0].set_xlabel('버스')
        axes[0,0].set_ylabel('표준편차 (pu)')
        axes[0,0].set_xticks([x+0.2 for x in range(len(buses))])
        axes[0,0].set_xticklabels([f'Bus {bus}' for bus in buses])
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)

        # 평균 변화율 비교
        case1_change = [case1_data['bus_analysis'][bus]['avg_change_rate'] for bus in buses]
        case2_change = [case2_data['bus_analysis'][bus]['avg_change_rate'] for bus in buses if bus in case2_data['bus_analysis']]

        axes[0,1].bar(range(len(buses)), case1_change, alpha=0.7, label='Case 1 (태양광만)', color='orange')
        if case2_change:
            axes[0,1].bar([x+0.4 for x in range(len(case2_change))], case2_change, alpha=0.7, label='Case 2 (태양광+ESS)', color='green')
        axes[0,1].set_title('평균 전압 변화율')
        axes[0,1].set_xlabel('버스')
        axes[0,1].set_ylabel('변화율 (pu/s)')
        axes[0,1].set_xticks([x+0.2 for x in range(len(buses))])
        axes[0,1].set_xticklabels([f'Bus {bus}' for bus in buses])
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)

        # 변동 빈도 비교
        case1_freq = [case1_data['bus_analysis'][bus]['change_frequency_percent'] for bus in buses]
        case2_freq = [case2_data['bus_analysis'][bus]['change_frequency_percent'] for bus in buses if bus in case2_data['bus_analysis']]

        axes[1,0].bar(range(len(buses)), case1_freq, alpha=0.7, label='Case 1 (태양광만)', color='orange')
        if case2_freq:
            axes[1,0].bar([x+0.4 for x in range(len(case2_freq))], case2_freq, alpha=0.7, label='Case 2 (태양광+ESS)', color='green')
        axes[1,0].set_title('유의한 전압 변동 빈도')
        axes[1,0].set_xlabel('버스')
        axes[1,0].set_ylabel('빈도 (%)')
        axes[1,0].set_xticks([x+0.2 for x in range(len(buses))])
        axes[1,0].set_xticklabels([f'Bus {bus}' for bus in buses])
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)

        # 전압 위반 비교
        case1_viol = [case1_data['bus_analysis'][bus]['violation_rate_percent'] for bus in buses]
        case2_viol = [case2_data['bus_analysis'][bus]['violation_rate_percent'] for bus in buses if bus in case2_data['bus_analysis']]

        axes[1,1].bar(range(len(buses)), case1_viol, alpha=0.7, label='Case 1 (태양광만)', color='orange')
        if case2_viol:
            axes[1,1].bar([x+0.4 for x in range(len(case2_viol))], case2_viol, alpha=0.7, label='Case 2 (태양광+ESS)', color='green')
        axes[1,1].set_title('전압 위반율 (±5% 범위)')
        axes[1,1].set_xlabel('버스')
        axes[1,1].set_ylabel('위반율 (%)')
        axes[1,1].set_xticks([x+0.2 for x in range(len(buses))])
        axes[1,1].set_xticklabels([f'Bus {bus}' for bus in buses])
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)

        plt.tight_layout()
        plot_file = os.path.join(output_dir, 'voltage_variation_comparison_1s.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📈 비교 플롯 저장: {plot_file}")
        return True

    except Exception as e:
        print(f"❌ 플롯 생성 중 오류: {e}")
        return False

def main():
    """메인 분석 함수"""
    print("🔍 1초 단위 시뮬레이션 데이터 분석 시작")

    # 데이터 경로 설정
    case1_dir = "/Users/seokjaehong/work/cosim-paper/results/data/case1"
    case2_dir = "/Users/seokjaehong/work/cosim-paper/results/data/case2"
    output_dir = "/Users/seokjaehong/work/cosim-paper/results/case_second"

    # 각 케이스 분석
    case1_data = analyze_voltage_data("Case 1 (태양광만)", case1_dir)
    case2_data = analyze_voltage_data("Case 2 (태양광+ESS)", case2_dir)

    if not case1_data:
        print("❌ Case 1 데이터 분석 실패")
        return

    if not case2_data:
        print("❌ Case 2 데이터 분석 실패")
        return

    # 결과 비교 및 요약
    print("\n" + "="*60)
    print("📋 전압 변동성 비교 요약 (1초 단위)")
    print("="*60)

    summary = {
        'simulation_type': '1초 단위 (3600초)',
        'case1': case1_data,
        'case2': case2_data,
        'improvement_analysis': {}
    }

    # Bus 650 기준으로 개선 효과 분석
    if '650' in case1_data['bus_analysis'] and '650' in case2_data['bus_analysis']:
        case1_bus650 = case1_data['bus_analysis']['650']
        case2_bus650 = case2_data['bus_analysis']['650']

        std_improvement = ((case1_bus650['std_voltage'] - case2_bus650['std_voltage']) / case1_bus650['std_voltage']) * 100
        change_improvement = ((case1_bus650['avg_change_rate'] - case2_bus650['avg_change_rate']) / case1_bus650['avg_change_rate']) * 100
        freq_improvement = case1_bus650['change_frequency_percent'] - case2_bus650['change_frequency_percent']
        viol_improvement = case1_bus650['violation_rate_percent'] - case2_bus650['violation_rate_percent']

        summary['improvement_analysis'] = {
            'voltage_std_improvement_percent': float(std_improvement),
            'change_rate_improvement_percent': float(change_improvement),
            'frequency_reduction_percent': float(freq_improvement),
            'violation_reduction_percent': float(viol_improvement)
        }

        print(f"🎯 Bus 650 기준 개선 효과:")
        print(f"   - 전압 표준편차: {std_improvement:.1f}% 개선")
        print(f"   - 평균 변화율: {change_improvement:.1f}% 개선")
        print(f"   - 변동 빈도: {freq_improvement:.1f}%p 감소")
        print(f"   - 전압 위반: {viol_improvement:.1f}%p 감소")

        if std_improvement > 0 and change_improvement > 0:
            print("✅ ESS가 전압 변동성을 효과적으로 감소시켰습니다!")
        else:
            print("⚠️  ESS 효과가 제한적이거나 예상과 다릅니다.")

    # 플롯 생성
    create_comparison_plots(case1_data, case2_data, output_dir)

    # 결과를 JSON으로 저장
    summary_file = os.path.join(output_dir, 'metrics_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n📁 결과 요약 저장: {summary_file}")
    print("🔍 1초 단위 시뮬레이션 분석 완료")

if __name__ == "__main__":
    main()