import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import warnings
import random
warnings.filterwarnings('ignore')

# 랜덤 시드 설정 (재현성 보장)
random.seed(42)
np.random.seed(42)

# ✅ 멀티프로세싱을 위한 전역 함수로 분리
def process_single_task(args):
    """멀티프로세싱용 전역 함수"""
    region, group_data, target, time_col, future_steps, group_key, config, all_data = args
    processor = ModelProcessor(config)
    return processor.process_region_target(region, group_data, target, time_col, future_steps, group_key, all_data)


class ModelProcessor:
    """시계열 예측을 위한 모델 처리 클래스"""
    def __init__(self, config):
        self.config = config

    def tune_prophet(self, df):
        """Prophet 하이퍼파라미터 튜닝 - 단순화"""
        return {
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 1.0,
            "seasonality_mode": "additive",
            "changepoint_range": 0.8
        }

    def process_region_target(self, region, group_data, target, time_col, future_steps, group_key, all_data=None):
        """단일 (region, target) 처리"""
        try:
            group = group_data.copy()
            group = group.sort_values(by=time_col).reset_index(drop=True)
            
            valid_data = group[target].notna()
            if valid_data.sum() < 1:
                return self._create_empty_result(region, future_steps, group_key, time_col, target)

            group_clean = group[valid_data].copy()
            
            if group_clean[time_col].dtype == 'object':
                group_clean[time_col] = pd.to_numeric(group_clean[time_col], errors='coerce')
            
            group_clean = group_clean.dropna(subset=[time_col])
            
            if len(group_clean) < 1:
                return self._create_empty_result(region, future_steps, group_key, time_col, target)

            # 데이터 품질 검증
            target_values = group_clean[target].astype(float)
            
            # 트렌드/계절성 분석
            trend_strength = self._trend_strength(target_values)
            seasonality_strength = self._seasonality_strength(target_values)
            
            # 트렌드가 명확하고 계절성이 약하면 단순 선형 트렌드 기반 예측
            if trend_strength > 0.05 and seasonality_strength < 0.3:
                print(f"[DEBUG] {region}-{target}: 트렌드 기반 예측 사용 (trend_strength: {trend_strength:.3f}, seasonality_strength: {seasonality_strength:.3f})")
                final_preds = self._simple_trend_based_prediction(target_values, future_steps)
            else:
                print(f"[DEBUG] {region}-{target}: Prophet 예측 사용 (trend_strength: {trend_strength:.3f}, seasonality_strength: {seasonality_strength:.3f})")
                # Prophet 보조적 사용
                final_preds = self._prophet_prediction(group_clean, target, time_col, future_steps)
            
            # 미래 연도 계산
            last_year = int(group_clean[time_col].max())
            future_years = list(range(last_year + 1, last_year + future_steps + 1))
            
            # 결과 DataFrame 생성
            if isinstance(group_key, list):
                data_dict = {}
                for i, col in enumerate(group_key):
                    if isinstance(region, tuple) and len(region) == len(group_key):
                        data_dict[col] = [region[i]] * future_steps
                    else:
                        data_dict[col] = [region] * future_steps
                data_dict[time_col] = future_years
                data_dict[target] = final_preds
                result_df = pd.DataFrame(data_dict)
            else:
                result_df = pd.DataFrame({
                    group_key: [region] * future_steps,
                    time_col: future_years,
                    target: final_preds
                })
            result_df['_target_name'] = target
            return result_df

        except (ValueError, TypeError) as e:
            print(f"[WARNING] {region}-{target} 데이터 타입 오류: {str(e)}")
            return self._create_empty_result(region, future_steps, group_key, time_col, target)
        except (KeyError, IndexError) as e:
            print(f"[WARNING] {region}-{target} 컬럼/인덱스 오류: {str(e)}")
            return self._create_empty_result(region, future_steps, group_key, time_col, target)
        except Exception as e:
            print(f"[ERROR] {region}-{target} 예상치 못한 오류: {str(e)}")
            return self._create_empty_result(region, future_steps, group_key, time_col, target)

    def _simple_trend_based_prediction(self, historical_values, future_steps):
        """데이터 기반 동적 트렌드 예측 - 가중 회귀 적용"""
        if len(historical_values) < 1:
            return [historical_values.iloc[-1]] * future_steps
        
        print(f"[DEBUG] 예측 대상 데이터: {historical_values.tolist()}")
        
        mean_val = historical_values.mean()
        std_val = historical_values.std()
        last_value = historical_values.iloc[-1]
        
        print(f"[DEBUG] 평균: {mean_val:.2f}, 표준편차: {std_val:.2f}, 마지막값: {last_value:.2f}")
        
        # 변동계수 계산
        volatility = std_val / (abs(mean_val) + 1e-8)
        print(f"[DEBUG] 변동성: {volatility:.3f}")
        
        # 가중 회귀로 트렌드 계산 (최근 데이터에 더 큰 가중치)
        x = np.arange(len(historical_values))
        y = historical_values.values
        
        # 지수적 가중치: 최근 데이터일수록 높은 가중치
        weights = np.exp(np.linspace(-2, 0, len(historical_values)))
        print(f"[DEBUG] 가중치: {weights}")
        
        # 가중 선형 회귀
        slope = np.polyfit(x, y, 1, w=weights)[0]
        print(f"[DEBUG] 가중 회귀 기울기: {slope:.3f}")
        
        # 추가: 최근 3년 데이터가 있으면 단기 트렌드도 고려
        if len(historical_values) >= 3:
            recent_data = historical_values[-3:].values
            recent_x = np.arange(len(recent_data))
            recent_slope = np.polyfit(recent_x, recent_data, 1)[0]
            print(f"[DEBUG] 최근 3년 기울기: {recent_slope:.3f}")
            
            original_slope = slope
            # 장기 가중 트렌드(70%) + 최근 트렌드(30%) 결합
            slope = 0.7 * slope + 0.3 * recent_slope
            print(f"[DEBUG] 결합 기울기: {original_slope:.3f} * 0.7 + {recent_slope:.3f} * 0.3 = {slope:.3f}")
        
        # 슬로프 조정
        max_change_rate = 0.2
        if volatility > 0.5:
            max_change_rate *= 0.5
            print(f"[DEBUG] 높은 변동성으로 변화율 조정: {max_change_rate:.3f}")
        
        max_slope = abs(mean_val) * max_change_rate
        print(f"[DEBUG] 최대 허용 기울기: ±{max_slope:.3f}")
        
        original_slope_final = slope
        if abs(slope) > max_slope:
            slope = max_slope if slope > 0 else -max_slope
            print(f"[DEBUG] 기울기 제한: {original_slope_final:.3f} → {slope:.3f}")
        
        # 예측값 생성
        predictions = []
        for i in range(1, future_steps + 1):
            pred = last_value + slope * i
            
            # 연속성 제한
            if predictions:
                max_change = abs(last_value) * max(volatility, 0.01)
                if abs(pred - predictions[-1]) > max_change:
                    old_pred = pred
                    pred = predictions[-1] + (max_change if pred > predictions[-1] else -max_change)
                    print(f"[DEBUG] 연속성 제한: {old_pred:.2f} → {pred:.2f}")
            
            predictions.append(pred)
        
        print(f"[DEBUG] 최종 예측값: {predictions}")
        return predictions

    def _trend_strength(self, y):
        """트렌드 강도 계산"""
        if len(y) < 2:
            return 0
        
        mean_val = y.mean()
        std_val = y.std()
        
        # 선형 회귀로 기울기 계산
        x = np.arange(len(y))
        slope = np.polyfit(x, y, 1)[0]
        
        # 변동성 계산
        volatility = std_val / (abs(mean_val) + 1e-8)
        data_length_weight = min(len(y) / 10.0, 1.0)
        
        # 트렌드 신뢰도
        trend_confidence = max(0, 1 - volatility)
        
        # 트렌드 강도
        trend_strength = abs(slope) * trend_confidence * data_length_weight / (std_val + 1e-8)
        
        return trend_strength

    def _seasonality_strength(self, y):
        """계절성 강도 계산"""
        if len(y) < 4:
            return 0
        
        diff = np.diff(y)
        seasonality_strength = np.std(diff) / (np.std(y) + 1e-8)
        
        # 데이터 길이에 따른 가중치
        data_length_weight = min(len(y) / 10.0, 1.0)
        seasonality_strength = seasonality_strength * data_length_weight
        
        return seasonality_strength

    def _prophet_prediction(self, group_clean, target, time_col, future_steps):
        """Prophet 예측 - 디버그 및 후처리 추가"""
        historical_values = group_clean[target].astype(float)
        print(f"[DEBUG Prophet] {target} 예측 대상 데이터: {historical_values.tolist()}")
        
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(group_clean[time_col].astype(int).astype(str) + '-01-01'),
            'y': historical_values
        })
        
        print(f"[DEBUG Prophet] 마지막 값: {historical_values.iloc[-1]:.2f}")
        
        best_prophet_params = self.tune_prophet(prophet_df)
        prophet_model = Prophet(
            changepoint_prior_scale=best_prophet_params.get('changepoint_prior_scale', 0.05),
            seasonality_prior_scale=best_prophet_params.get('seasonality_prior_scale', 1.0),
            changepoint_range=best_prophet_params.get('changepoint_range', 0.8),
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode=best_prophet_params.get('seasonality_mode', 'additive')
        )
        prophet_model.fit(prophet_df)
        last_year = int(group_clean[time_col].max())
        future_years = list(range(last_year + 1, last_year + future_steps + 1))
        future_dates = pd.DataFrame({'ds': pd.to_datetime([f"{yr}-01-01" for yr in future_years])})
        prophet_preds = prophet_model.predict(future_dates)['yhat'].values
        
        print(f"[DEBUG Prophet] 원본 Prophet 예측값: {prophet_preds}")
        
        # 비현실적인 예측 감지 및 수정
        last_value = historical_values.iloc[-1]
        adjusted_preds = []
        
        for i, pred in enumerate(prophet_preds):
            # 급격한 변화 감지
            expected_change_per_year = abs(last_value) * 0.2  # 연간 20% 이상 변화 제한
            max_total_change = expected_change_per_year * (i + 1)
            
            if abs(pred - last_value) > max_total_change:
                print(f"[DEBUG Prophet] 급격한 변화 감지: Year {i+1}, {pred:.2f} → 제한 적용")
                # 변화를 제한
                if pred > last_value:
                    adjusted_pred = last_value + max_total_change
                else:
                    adjusted_pred = last_value - max_total_change
            else:
                adjusted_pred = pred
            
            # 특정 지표별 추가 제약
            if target and 'RT' in target.upper():  # 비율 지표
                if adjusted_pred < 0 and last_value > 0:
                    print(f"[DEBUG Prophet] 비율 지표 음수 방지: {adjusted_pred:.2f} → {max(0.1, last_value * 0.1):.2f}")
                    adjusted_pred = max(0.1, last_value * 0.1)
            
            adjusted_preds.append(adjusted_pred)
        
        print(f"[DEBUG Prophet] 조정된 예측값: {adjusted_preds}")
        return adjusted_preds

    def _create_empty_result(self, region, future_steps, group_key, time_col, target):
        """빈 결과 DataFrame 생성"""
        if isinstance(group_key, list):
            data_dict = {}
            for i, col in enumerate(group_key):
                if isinstance(region, tuple) and len(region) == len(group_key):
                    data_dict[col] = [region[i]] * future_steps
                else:
                    data_dict[col] = [region] * future_steps
            data_dict[time_col] = [np.nan] * future_steps
            data_dict[target] = [np.nan] * future_steps
            result_df = pd.DataFrame(data_dict)
        else:
            result_df = pd.DataFrame({
                group_key: [region] * future_steps,
                time_col: [np.nan] * future_steps,
                target: [np.nan] * future_steps
            })
        result_df['_target_name'] = target
        return result_df


class Model:
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.original_dtypes = {}

    def train_and_predict(self, X, y):
        """메인 학습 및 예측 함수"""
        # 설정 검증
        prediction_config = self.config.get("prediction", {})
        time_col = prediction_config.get("time_col")
        group_key = prediction_config.get("group_key")
        future_steps = prediction_config.get("future_steps")
        
        if not time_col or not group_key or not future_steps:
            raise ValueError("prediction 설정에서 time_col, group_key, future_steps가 모두 필요합니다.")
        
        if future_steps <= 0:
            raise ValueError("future_steps는 1 이상이어야 합니다.")

        print(f"[INFO] 시계열 예측 시작 - Time Col: {time_col}, Group: {group_key}")
        
        # 원본 데이터 타입 저장
        df = X.copy()
        for col in y.columns:
            df[col] = y[col]
        
        self.original_dtypes = {col: df[col].dtype for col in df.columns}
        print(f"[INFO] 원본 데이터 타입 저장 완료")
        
        # 시간 컬럼 처리
        df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col])
        
        if len(df) == 0:
            raise ValueError(f"시간 컬럼 '{time_col}'을 숫자형으로 변환할 수 없습니다.")
        
        # 데이터 검증
        if isinstance(group_key, list):
            missing_group_cols = [col for col in group_key if col not in df.columns]
            if missing_group_cols:
                raise ValueError(f"그룹 키 컬럼이 데이터에 존재하지 않습니다: {missing_group_cols}")
        else:
            if group_key not in df.columns:
                raise ValueError(f"그룹 키 '{group_key}'가 데이터에 존재하지 않습니다.")
        
        if time_col not in df.columns:
            raise ValueError(f"시간 컬럼 '{time_col}'이 데이터에 존재하지 않습니다.")
        
        missing_targets = [col for col in y.columns if col not in df.columns]
        if missing_targets:
            raise ValueError(f"타겟 컬럼이 데이터에 존재하지 않습니다: {missing_targets}")

        # 태스크 생성
        tasks = []
        for region, group_data in df.groupby(group_key):
            for target in y.columns:
                tasks.append((region, group_data, target, time_col, future_steps, group_key, self.config, df))

        print(f"[INFO] 총 {len(tasks)}개 태스크 생성")

        # 멀티프로세싱 실행
        results = []
        import os
        is_ci = os.getenv('CI', 'false').lower() == 'true'
        
        import multiprocessing as mp
        if mp.get_start_method(allow_none=True) != 'fork':
            mp.set_start_method('fork', force=True)
        
        if is_ci or len(tasks) <= 1:
            print("[INFO] 단일 프로세스 모드로 실행")
            for task in tqdm(tasks, desc="예측 진행", unit="task"):
                result = process_single_task(task)
                results.append(result)
        else:
            n_processes = max(1, min(cpu_count() - 1, len(tasks)))
            print(f"[INFO] 멀티프로세싱 모드로 실행 (프로세스 수: {n_processes})")
            
            try:
                with Pool(processes=n_processes) as pool:
                    for result in tqdm(pool.imap_unordered(process_single_task, tasks),
                                     total=len(tasks), desc="예측 진행", unit="task"):
                        results.append(result)
            except RuntimeError as e:
                if "bootstrapping phase" in str(e):
                    print("[WARNING] 멀티프로세싱 오류 발생, 단일 프로세스로 전환")
                    results = []
                    for task in tqdm(tasks, desc="예측 진행 (단일 프로세스)", unit="task"):
                        result = process_single_task(task)
                        results.append(result)
                else:
                    raise e

        if not results:
            print("[WARNING] 예측 결과가 없습니다.")
            return pd.DataFrame()

        # Wide Format으로 변환
        print("[INFO] 결과를 Wide Format으로 변환 중...")
        wide_format_df = self._convert_to_wide_format(results, group_key, time_col, y.columns)
        
        # 원본 데이터 타입으로 복원
        wide_format_df = self._restore_original_dtypes(wide_format_df)
            
        print(f"[INFO] 예측 완료 - 총 {len(wide_format_df)} rows 생성")
        return wide_format_df

    def _restore_original_dtypes(self, df):
        """원본 데이터 타입으로 복원"""
        print("[INFO] 원본 데이터 타입으로 복원 중...")
        
        df_restored = df.copy()
        time_col = self.config["prediction"]["time_col"]
        
        for col in df_restored.columns:
            if col in self.original_dtypes:
                original_dtype = self.original_dtypes[col]
                current_dtype = df_restored[col].dtype
                
                try:
                    if pd.api.types.is_integer_dtype(original_dtype):
                        df_restored[col] = df_restored[col].fillna(0).round().astype('Int64')
                        print(f"  {col}: {current_dtype} → Int64 (원본: {original_dtype})")
                        
                    elif pd.api.types.is_float_dtype(original_dtype):
                        df_restored[col] = pd.to_numeric(df_restored[col], errors='coerce').astype('float64')
                        print(f"  {col}: {current_dtype} → float64 (원본: {original_dtype})")
                        
                    elif pd.api.types.is_object_dtype(original_dtype):
                        if col == time_col:
                            df_restored[col] = df_restored[col].astype(str)
                        else:
                            df_restored[col] = df_restored[col].astype(str)
                        print(f"  {col}: {current_dtype} → object (원본: {original_dtype})")
                        
                    elif 'int' in str(original_dtype).lower():
                        df_restored[col] = df_restored[col].fillna(0).round().astype('Int64')
                        print(f"  {col}: {current_dtype} → Int64 (원본: {original_dtype})")
                        
                    else:
                        print(f"  {col}: {current_dtype} → 변환 안함 (원본: {original_dtype})")
                        
                except Exception as e:
                    print(f"  [WARNING] {col} 타입 복원 실패: {e}")
                    df_restored[col] = df_restored[col].astype(str)
        
        return df_restored

    def _convert_to_wide_format(self, results, group_key, time_col, target_columns):
        """개별 target 결과를 Wide Format으로 병합"""
        
        # 유효한 결과만 필터링
        valid_results = []
        for result_df in results:
            if '_target_name' in result_df.columns and len(result_df) > 0:
                target_name = result_df['_target_name'].iloc[0]
                if not result_df[target_name].isna().all():
                    valid_results.append(result_df)

        if not valid_results:
            print("[WARNING] 유효한 예측 결과가 없습니다.")
            return pd.DataFrame()

        print(f"[INFO] 유효한 결과 수: {len(valid_results)}")

        # 실제 예측된 결과만 사용하여 기준 프레임 생성
        actual_predictions = []
        for result_df in valid_results:
            target_name = result_df['_target_name'].iloc[0]
            valid_data = result_df.dropna(subset=[target_name])
            if len(valid_data) > 0:
                if isinstance(group_key, list):
                    columns_to_select = group_key + [time_col, target_name]
                else:
                    columns_to_select = [group_key, time_col, target_name]
                actual_predictions.append(valid_data[columns_to_select])
        
        if not actual_predictions:
            print("[WARNING] 유효한 예측 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 실제 예측된 조합들만 사용
        base_df = pd.concat(actual_predictions, ignore_index=True)
        if isinstance(group_key, list):
            columns_to_select = group_key + [time_col]
        else:
            columns_to_select = [group_key, time_col]
        base_df = base_df[columns_to_select].drop_duplicates()
        
        print(f"[INFO] 실제 예측 결과 기준 프레임 생성: {len(base_df)} rows")
        print(f"[INFO] 예측 연도 범위: {base_df[time_col].min()} ~ {base_df[time_col].max()}")
        print(f"[INFO] 지역별 예측 건수:")
        region_counts = base_df.groupby(group_key).size()
        print(region_counts.head(10))

        # Target별로 그룹화하여 중복 제거
        target_results = {}
        for result_df in valid_results:
            target_name = result_df['_target_name'].iloc[0]
            
            if target_name not in target_results:
                target_results[target_name] = []
            
            merge_df = result_df.drop(columns=['_target_name']).copy()
            if isinstance(group_key, list):
                merge_df = merge_df.dropna(subset=group_key + [time_col])
            else:
                merge_df = merge_df.dropna(subset=[group_key, time_col])
            target_results[target_name].append(merge_df)

        # 각 target별로 먼저 통합한 후 병합
        for target_name in target_results:
            print(f"[INFO] {target_name} 처리 중... ({len(target_results[target_name])} 개 결과)")
            
            if len(target_results[target_name]) == 1:
                if isinstance(group_key, list):
                    columns_to_select = group_key + [time_col, target_name]
                else:
                    columns_to_select = [group_key, time_col, target_name]
                target_df = target_results[target_name][0][columns_to_select]
            else:
                combined_data = []
                for df in target_results[target_name]:
                    if target_name in df.columns:
                        if isinstance(group_key, list):
                            columns_to_select = group_key + [time_col, target_name]
                        else:
                            columns_to_select = [group_key, time_col, target_name]
                        combined_data.append(df[columns_to_select])
                
                if combined_data:
                    target_df = pd.concat(combined_data, ignore_index=True)
                    if isinstance(group_key, list):
                        group_cols = group_key + [time_col]
                    else:
                        group_cols = [group_key, time_col]
                    target_df = target_df.groupby(group_cols, as_index=False)[target_name].mean()
                else:
                    continue
            
            # 기준 프레임에 병합
            if target_name in base_df.columns:
                base_df = base_df.drop(columns=[target_name])
            
            base_df = base_df.merge(
                target_df, 
                on=group_key + [time_col] if isinstance(group_key, list) else [group_key, time_col], 
                how='left'
            )
            
            print(f"[INFO] {target_name} 병합 완료")

        # 모든 target 컬럼이 존재하는지 확인하고 추가
        for target in target_columns:
            if target not in base_df.columns:
                base_df[target] = np.nan
                print(f"[WARNING] {target} 컬럼이 없어서 NaN으로 추가")

        # 컬럼 순서 정리
        if isinstance(group_key, list):
            column_order = group_key + [time_col] + list(target_columns)
        else:
            column_order = [group_key, time_col] + list(target_columns)
        base_df = base_df[column_order]

        # 정렬
        if isinstance(group_key, list):
            sort_cols = group_key + [time_col]
        else:
            sort_cols = [group_key, time_col]
        base_df = base_df.sort_values(sort_cols).reset_index(drop=True)
        
        print(f"[INFO] Wide Format 변환 완료: {base_df.shape}")
        print(f"[INFO] 최종 컬럼: {list(base_df.columns)}")
        
        return base_df