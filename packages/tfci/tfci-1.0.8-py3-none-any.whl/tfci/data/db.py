import pandas as pd
import numpy as np

# 선택적 의존성 - DB 연결이 필요한 경우에만 import
try:
    import ibm_db
    import ibm_db_dbi
    IBM_DB_AVAILABLE = True
except ImportError:
    IBM_DB_AVAILABLE = False
    print("[WARNING] ibm_db 모듈이 설치되지 않았습니다. DB 기능을 사용할 수 없습니다.")

class Database:
    def __init__(self, config):
        self.config = config
        self.db_type = config.get("db_type", "").lower()

    def load(self):
        if not IBM_DB_AVAILABLE:
            raise ImportError("ibm_db 모듈이 설치되지 않았습니다. 'pip install ibm-db'를 실행하세요.")
        
        if self.db_type == "db2":
            return self._load_db2()
        else:
            raise ValueError(f"지원하지 않는 DB 타입: {self.db_type}")

    def save(self, df):
        if not IBM_DB_AVAILABLE:
            raise ImportError("ibm_db 모듈이 설치되지 않았습니다. 'pip install ibm-db'를 실행하세요.")
        
        if self.db_type == "db2":
            self._save_db2(df)
        else:
            raise ValueError(f"지원하지 않는 DB 타입: {self.db_type}")

    # ------------------- DB2 -------------------
    def _load_db2(self):
        """DB2에서 데이터 로드"""
        conn_str = (
            f"DATABASE={self.config['connection']['database']};"
            f"HOSTNAME={self.config['connection']['host']};"
            f"PORT={self.config['connection']['port']};"
            f"PROTOCOL=TCPIP;"
            f"UID={self.config['connection']['user']};"
            f"PWD={self.config['connection']['password']};"
        )
        
        target = self.config['target']
        if isinstance(target, str):
            target = [target]
        
        query = f"SELECT {', '.join(self.config['features'] + target)} FROM {self.config['table']}"
        print(f"[INFO] 실행 쿼리: {query}")

        conn = ibm_db.connect(conn_str, "", "")
        try:
            pconn = ibm_db_dbi.Connection(conn)
            df = pd.read_sql(query, pconn)
            print(f"[INFO] DB2에서 {len(df)} rows 로드 완료")
        finally:
            ibm_db.close(conn)

        return df

    def _save_db2(self, df):
        """DB2에 예측 결과 저장 - 완전히 동적 처리"""
        if df is None or len(df) == 0:
            print("[WARNING] 저장할 데이터가 없습니다.")
            return

        print(f"[INFO] 저장 전 데이터 검증 및 전처리 시작...")
        
        # ✅ 1. 데이터 전처리
        df_clean = self._preprocess_for_db(df)
        
        if len(df_clean) == 0:
            print("[WARNING] 전처리 후 유효한 데이터가 없습니다.")
            return

        # ✅ 설정에서 컬럼명 가져오기 (저장용)
        prediction_config = self.config.get('prediction', {})
        group_col = prediction_config.get('group_key')  # 예: "RGN_CD"
        time_col = prediction_config.get('time_col')    # 예: "CRTR_YR"

        conn_str = (
            f"DATABASE={self.config['connection']['database']};"
            f"HOSTNAME={self.config['connection']['host']};"
            f"PORT={self.config['connection']['port']};"
            f"PROTOCOL=TCPIP;"
            f"UID={self.config['connection']['user']};"
            f"PWD={self.config['connection']['password']};"
        )
        
        conn = None
        pconn = None
        cursor = None
        
        try:
            # 연결 생성
            conn = ibm_db.connect(conn_str, "", "")
            if conn is None:
                raise Exception("DB 연결 실패")
            
            pconn = ibm_db_dbi.Connection(conn)
            cursor = pconn.cursor()

            # ✅ DB 컬럼 타입 확인
            column_types = self._get_column_types(cursor)
            if not column_types:
                print(f"[WARNING] 테이블이 존재하지 않거나 컬럼 정보를 가져올 수 없습니다.")
                print(f"[INFO] 기본 타입으로 진행합니다.")
                column_types = {}

            # 데이터 준비
            df_to_save = df_clean.copy()
            
            # 컬럼 순서 정리 (메타데이터 없이)
            final_cols = list(df_to_save.columns)
            
            df_to_save = df_to_save[final_cols]

            print(f"[INFO] 최종 저장 데이터:")
            print(f"  - Shape: {df_to_save.shape}")
            print(f"  - Columns: {list(df_to_save.columns)}")
            print("  - Data types:")
            for col in df_to_save.columns:
                print(f"    {col}: {df_to_save[col].dtype}")
            
            print("  - Sample data:")
            print(df_to_save.head(3))
            print("  - NaN count per column:")
            print(df_to_save.isnull().sum())

            # ✅ 2. 배치별 저장 (완전히 동적 처리)
            batch_size = 1000
            total_saved = 0
            
            placeholders = ', '.join(['?'] * len(final_cols))
            sql = f"INSERT INTO {self.config['table']} ({', '.join(final_cols)}) VALUES ({placeholders})"
            
            for i in range(0, len(df_to_save), batch_size):
                batch_df = df_to_save.iloc[i:i+batch_size]
                
                # ✅ 데이터 타입 최종 검증 및 변환 (동적 처리)
                batch_tuples = []
                target_cols = self.config.get('target', [])
                if isinstance(target_cols, str):
                    target_cols = [target_cols]
                
                for _, row in batch_df.iterrows():
                    row_tuple = []
                    for col in final_cols:
                        val = row[col]
                        if pd.isna(val):
                            row_tuple.append(None)
                        else:
                            row_tuple.append(val)
                    
                    # ✅ DB 컬럼 타입에 맞게 데이터 변환
                    row_tuple = self._convert_to_db_types(row_tuple, final_cols, column_types)
                    batch_tuples.append(tuple(row_tuple))
                
                print(f"[INFO] 배치 {i//batch_size + 1}: {len(batch_tuples)}개 레코드 삽입...")
                cursor.executemany(sql, batch_tuples)
                total_saved += len(batch_tuples)
            
            pconn.commit()
            print(f"[SUCCESS] DB2에 총 {total_saved}건 저장 완료!")

        except Exception as e:
            if pconn:
                try:
                    pconn.rollback()
                except:
                    pass
            print(f"[ERROR] DB2 저장 실패: {str(e)}")
            raise

        finally:
            # 연결 정리
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if pconn:
                try:
                    pconn.close()
                except:
                    pass
            if conn:
                try:
                    ibm_db.close(conn)
                except:
                    pass

    def _preprocess_for_db(self, df):
        """DB 저장을 위한 데이터 전처리 - 완전히 동적 처리"""
        df_clean = df.copy()
        
        # ✅ 설정에서 실제 컬럼명 가져오기 (하드코딩 제거)
        prediction_config = self.config.get('prediction', {})
        group_col = prediction_config.get('group_key')  # 사용자 설정값
        time_col = prediction_config.get('time_col')    # 사용자 설정값
        
        print(f"[INFO] 사용할 컬럼명 - Group: {group_col}, Time: {time_col}")
        print(f"[INFO] 전처리 전 데이터 상태:")
        print(f"  - Shape: {df_clean.shape}")
        print(f"  - Columns: {list(df_clean.columns)}")
        print(f"  - NaN counts:\n{df_clean.isnull().sum()}")
        
        # ✅ 1. target 컬럼들의 NaN 값을 0으로 채우기 (예측 결과 처리)
        target_cols = self.config.get('target', [])
        if isinstance(target_cols, str):
            target_cols = [target_cols]
        
        for col in target_cols:
            if col in df_clean.columns:
                # 원본 데이터 타입 확인
                original_dtype = df_clean[col].dtype
                print(f"[INFO] {col} 원본 타입: {original_dtype}")
                
                df_clean[col] = df_clean[col].fillna(0.0)
                # 음수 허용 (실제 데이터에 음수가 있음)
                
                # float 타입인 경우 소수점 정밀도 보존, int 타입인 경우 정수 유지
                if pd.api.types.is_float_dtype(original_dtype):
                    # float 타입은 소수점 정밀도 보존 (round(4)로 더 정밀하게)
                    df_clean[col] = df_clean[col].round(4)
                    print(f"[INFO] {col} 컬럼 처리 완료 (float, 소수점 4자리 보존)")
                else:
                    # int 타입은 정수로 유지
                    df_clean[col] = df_clean[col].round().astype(int)
                    print(f"[INFO] {col} 컬럼 처리 완료 (int, 정수 유지)")
                
                # 데이터 정밀도 보존 (범위 제한 제거)
                if pd.api.types.is_float_dtype(df_clean[col].dtype):
                    # 원본 데이터의 정밀도 보존 (소수점 4자리까지 허용)
                    df_clean[col] = df_clean[col].round(4)
                    print(f"[INFO] {col} 컬럼 처리 완료 (float, 소수점 4자리 보존, 범위 제한 없음)")
                    print(f"  - 데이터 범위: {df_clean[col].min():.4f} ~ {df_clean[col].max():.4f}")
        
        # ✅ 2. 완전히 빈 행 제거 (이미 NaN을 0으로 채웠으므로 의미없음, 하지만 안전장치)
        before_len = len(df_clean)
        df_clean = df_clean.dropna(subset=target_cols, how='all')
        print(f"[INFO] 완전 빈 행 제거: {before_len} → {len(df_clean)} rows")
        
        # ✅ 3. 동적 컬럼 처리 (컬럼명 하드코딩 제거)
        # 그룹 컬럼 처리 (예: RGN_CD, REGION_ID, AREA_CODE 등 어떤 이름이든)
        if group_col:
            if isinstance(group_col, list):
                # group_col이 리스트인 경우 모든 컬럼을 처리
                for col in group_col:
                    if col in df_clean.columns:
                        df_clean[col] = df_clean[col].astype(str)
                        print(f"[INFO] {col} 컬럼을 문자열로 변환완료")
            else:
                # group_col이 단일 문자열인 경우
                if group_col in df_clean.columns:
                    df_clean[group_col] = df_clean[group_col].astype(str)
                    print(f"[INFO] {group_col} 컬럼을 문자열로 변환완료")
        
        # 시간 컬럼 처리 (예: CRTR_YR, YEAR, DATE 등 어떤 이름이든)
        if time_col and time_col in df_clean.columns:
            # 기본값을 현재 년도로 설정하고 정수형 변환 후 문자열로
            current_year = pd.Timestamp.now().year
            df_clean[time_col] = df_clean[time_col].fillna(current_year).astype(int).astype(str)
            print(f"[INFO] {time_col} 컬럼을 문자열로 변환 완료")
        
        # ✅ 4. 필수 컬럼 누락 확인 (동적)
        essential_cols = []
        if group_col:
            if isinstance(group_col, list):
                essential_cols.extend(group_col)
            else:
                essential_cols.append(group_col)
        if time_col:
            essential_cols.append(time_col)
        
        for col in essential_cols:
            if col in df_clean.columns:
                before_drop = len(df_clean)
                df_clean = df_clean.dropna(subset=[col])
                after_drop = len(df_clean)
                if before_drop != after_drop:
                    print(f"[INFO] {col} 누락 행 제거: {before_drop} → {after_drop}")
        
        print(f"[INFO] 전처리 후 데이터 상태:")
        print(f"  - Shape: {df_clean.shape}")
        print(f"  - Final columns: {list(df_clean.columns)}")
        
        return df_clean

    def _get_column_types(self, cursor):
        """DB 테이블의 컬럼 타입 정보를 가져옴"""
        try:
            table_name = self.config['table']
            schema_name, table_name_only = table_name.split('.') if '.' in table_name else ('', table_name)
            
            if schema_name:
                sql = f"""
                SELECT COLNAME, TYPENAME, LENGTH, SCALE 
                FROM SYSCAT.COLUMNS 
                WHERE TABSCHEMA = '{schema_name}' AND TABNAME = '{table_name_only}'
                ORDER BY COLNO
                """
            else:
                sql = f"""
                SELECT COLNAME, TYPENAME, LENGTH, SCALE 
                FROM SYSCAT.COLUMNS 
                WHERE TABNAME = '{table_name_only}'
                ORDER BY COLNO
                """
            
            cursor.execute(sql)
            columns_info = cursor.fetchall()
            
            column_types = {}
            for col_info in columns_info:
                colname, typename, length, scale = col_info
                column_types[colname] = {
                    'type': typename,
                    'length': length,
                    'scale': scale
                }
            
            print(f"[INFO] DB 컬럼 타입 확인 완료:")
            for col, type_info in column_types.items():
                print(f"  {col}: {type_info['type']}({type_info['length']},{type_info['scale']})")
            
            return column_types
            
        except Exception as e:
            print(f"[WARNING] 컬럼 타입 확인 실패: {e}")
            return {}

    def _convert_to_db_types(self, row_tuple, columns, column_types):
        """DB 컬럼 타입에 맞게 데이터 변환"""
        converted_tuple = []
        
        for i, (col, val) in enumerate(zip(columns, row_tuple)):
            if col in column_types:
                type_info = column_types[col]
                typename = type_info['type']
                length = type_info['length']
                scale = type_info['scale']
                
                if val is None:
                    converted_tuple.append(None)
                elif typename == 'DECIMAL':
                    # DECIMAL 타입에 맞게 변환
                    try:
                        if isinstance(val, (int, float)):
                            # DECIMAL 범위에 맞게 조정
                            max_value = 10 ** (length - scale) - 1
                            min_value = -max_value
                            
                            # 범위를 초과하는 경우 조정
                            if val > max_value:
                                print(f"[WARNING] {col} 값이 범위를 초과: {val} > {max_value}")
                                val = max_value
                            elif val < min_value:
                                print(f"[WARNING] {col} 값이 범위를 초과: {val} < {min_value}")
                                val = min_value
                            
                            # 소수점 자릿수 조정
                            val = round(float(val), scale)
                            converted_tuple.append(val)
                        else:
                            converted_tuple.append(float(val) if val else None)
                    except:
                        converted_tuple.append(None)
                elif typename in ['VARCHAR', 'CHAR']:
                    # 문자열 타입
                    str_val = str(val) if val else None
                    if str_val and len(str_val) > length:
                        str_val = str_val[:length]
                    converted_tuple.append(str_val)
                elif typename in ['INTEGER', 'SMALLINT', 'BIGINT']:
                    # 정수 타입
                    try:
                        converted_tuple.append(int(val) if val else None)
                    except:
                        converted_tuple.append(None)
                else:
                    # 기타 타입은 그대로
                    converted_tuple.append(val)
            else:
                # 타입 정보가 없으면 그대로
                converted_tuple.append(val)
        
        return converted_tuple
