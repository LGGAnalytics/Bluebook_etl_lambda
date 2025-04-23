import pandas as pd
import glob
import numpy as np
import re

class ETL_Bluebook():

    def __init__(self, conn, cursor):

        self.conn = conn
        self.cursor = cursor

        self.cols = ['summary_date','summary_netsales_total', 'summary_tktcount_total', 'summary_tktcount_ontime', 'tktcount_ontime_pct',
                     'tkt_avg','av_time_all','av_time_callin','av_time_counter','av_time_stall','av_time_dt','av_time_patio',
                     'av_time_oa','av_time_delivery','reply_time','cash_due','cash_deposits', 'summary_overshort_amount',
                     'cancel_tkt','cancel_tkt_cnt','crew_labor','total_labor', 'food_cost','food_cost_pct']

        self.cols_to_update=['stores_number','summary_date','summary_netsales_total', 
                             'summary_tktcount_total', 'summary_tktcount_ontime','summary_overshort_amount']
        
        self.df = []
    
    @staticmethod
    def is_date(value):
        if isinstance(value, str):
            return bool(re.match(r'^\d{2}-\d{2}-\d{2}$', value))
        return False  # safely handle None or other types

    def extract(self):
        print('Starting extract')
        # df = pd.read_excel('/Users/felipesilverio/Documents/GitHub/miscellanious/BlueBook_OSonic_TEMP.xlsx', header=4)
        print(f"Extracting {glob.glob('/tmp/downloaded_files/*.xlsx')}")
        excel_files = glob.glob('/tmp/downloaded_files/*.xlsx')
        df = pd.read_excel(excel_files[0], header=4)

        df.columns = self.cols
        df.drop(0, inplace=True)
        self.df = df.copy()
        print('Finished extract')


    def transform(self):
        print('Starting transformations')
        df = self.df.copy()
        # Apply function to create new column
        df['is_date'] = df['summary_date'].apply(self.is_date).astype(int)
        df['summary_date'] = df['summary_date'].apply(lambda x: x if self.is_date(x) else str(x)[:4])

        df['stores_number'] = df.summary_date
        for idx in df.index:
            val = df.loc[idx, 'summary_date']
            if val.isdigit():  # If it's a numeric string (like 1082 or 1130)
                # Fill this value for the next 7 rows (including itself if needed)
                df.loc[idx:idx+7, 'stores_number'] = val
        df = df[df.is_date==1].copy()


        df['summary_date'] = pd.to_datetime(df['summary_date'], format='%m-%d-%y', errors='coerce')

        df.reset_index(drop=True)
        self.df = df[self.cols_to_update]
        print('Finished transformations')

    def load(self):
        print('Starting load')

        df = self.df.copy()

        # df = pd.read_csv('/Users/felipesilverio/Documents/GitHub/miscellanious/Consolidate_BB_v2.csv')
        df = df.dropna(axis=1, how='all')

        # Step 1: Create temporary table

        self.cursor.execute("""
            CREATE TABLE CMGSOAR.update_data (
                stores_number VARCHAR(28),
                summary_date VARCHAR(28),
                summary_netsales_total VARCHAR(28),
                summary_tktcount_total VARCHAR(28),
                summary_tktcount_ontime VARCHAR(28),
                summary_overshort_amount VARCHAR(28)
        );
        """)
        print('Created temporary table CMGSOAR.update_data')
        # self.df.to_csv('consolidate_bb.csv')

        # Step 2: Load data into temporary table
        # Convert datetime columns to strings
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
                
        values = df.values.tolist()
        values = [[None if isinstance(val, float) and np.isnan(val) else val for val in row] for row in values]
        columns2 = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))

        sql = f"""INSERT INTO CMGSOAR.update_data ({columns2}) VALUES ({placeholders})"""
        self.cursor.executemany(sql, values)
        print('Inserted values into update_data')
        self.cursor.execute("""
            UPDATE CMGSOAR.store_summary AS target
            JOIN CMGSOAR.update_data AS upd
            ON target.stores_number = upd.stores_number
            AND target.summary_date = upd.summary_date
            SET 
                target.summary_netsales_total = upd.summary_netsales_total,
                target.summary_tktcount_total = upd.summary_tktcount_total,
                target.summary_tktcount_ontime = upd.summary_tktcount_ontime,
                target.summary_overshort_amount = upd.summary_overshort_amount;
        """)
        print('Updated CMGSOAR.store_summary') 
        self.cursor.execute("""
            DROP TABLE CMGSOAR.update_data;
        """)
        print('Deleted temporary table CMGSOAR.update_data')

        # Commit and close
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('Finishing load')

    def run(self):
        self.extract()
        self.transform()
        self.load()
